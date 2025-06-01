# backend/app/api/public/parts.py (修复版本)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text, distinct
from typing import List, Optional, Union, Any, Dict
from app.core.database import get_db
from app.models.part import Part
from app.schemas.part import PartResponse
from app.auth.middleware import get_current_user_optional
from app.auth.models import User
import re
from collections import defaultdict, Counter

router = APIRouter()

@router.get("/search", response_model=List[PartResponse])
async def search_parts_enhanced(
    q: Optional[str] = Query(None, description="搜索关键词，支持多词搜索"),
    category: Optional[str] = Query(None, description="类别筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    增强搜索API - 支持多关键词和属性搜索
    
    搜索逻辑：
    - 支持空格分隔的多关键词搜索
    - 搜索范围：名称、描述、类别、所有自定义属性
    - 多词搜索：所有词都必须匹配（AND逻辑）
    - 示例：搜索"电阻 5V"会找到名称包含"电阻"且属性包含"5V"的零件
    """
    query = db.query(Part)
    
    # 如果有搜索关键词
    if q and q.strip():
        # 分割搜索词（按空格）
        search_terms = [term.strip() for term in q.split() if term.strip()]
        
        if search_terms:
            # 对每个搜索词，构建OR条件（在各字段中搜索）
            for term in search_terms:
                search_term = f"%{term}%"
                
                # 构建单个词的搜索条件
                term_conditions = [
                    Part.name.ilike(search_term),           # 名称搜索
                    Part.description.ilike(search_term),    # 描述搜索
                    Part.category.ilike(search_term),       # 类别搜索
                ]
                
                # PostgreSQL JSON字段搜索 - 搜索所有properties的键和值
                try:
                    # 搜索JSON中的所有键和值
                    term_conditions.append(
                        text("properties::text ILIKE :search_term").bindparam(search_term=search_term)
                    )
                except Exception as e:
                    print(f"JSON搜索出错: {e}")
                    # 降级处理：尝试转换为字符串搜索
                    pass
                
                # 应用OR条件（任一字段匹配该词即可）
                query = query.filter(or_(*term_conditions))
    
    # 类别筛选
    if category:
        query = query.filter(Part.category == category)
    
    # 分页
    parts = query.offset(skip).limit(limit).all()
    
    return parts

@router.get("/", response_model=List[PartResponse])
async def get_parts_public(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取零件列表（兼容性保持）"""
    query = db.query(Part)
    
    if category:
        query = query.filter(Part.category == category)
    
    parts = query.offset(skip).limit(limit).all()
    return parts

@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    q: Optional[str] = Query(None, min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=20, description="建议数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    获取搜索建议 - 支持属性值建议
    """
    if not q:
        return []
    
    suggestions = set()
    search_term = f"%{q}%"
    
    try:
        # 获取匹配的类别
        categories = db.query(Part.category).filter(
            Part.category.ilike(search_term)
        ).distinct().limit(3).all()
        
        for cat in categories:
            if cat[0]:
                suggestions.add(cat[0])
        
        # 获取匹配的零件名称
        names = db.query(Part.name).filter(
            Part.name.ilike(search_term)
        ).limit(5).all()
        
        for name in names:
            if name[0]:
                suggestions.add(name[0])
        
        # 获取匹配的属性值（从JSON中提取）
        # 这里简化处理，实际生产环境可能需要更复杂的JSON查询
        parts_with_properties = db.query(Part.properties).filter(
            Part.properties.isnot(None)
        ).limit(50).all()
        
        for part_props in parts_with_properties:
            if part_props[0]:  # properties不为空
                try:
                    properties = part_props[0]
                    if isinstance(properties, dict):
                        # 搜索属性键
                        for key in properties.keys():
                            if q.lower() in key.lower():
                                suggestions.add(key)
                        
                        # 搜索属性值
                        for value in properties.values():
                            if isinstance(value, str) and q.lower() in value.lower():
                                suggestions.add(value)
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"获取搜索建议时出错: {e}")
        return []
    
    # 限制返回数量并排序
    result = sorted(list(suggestions))[:limit]
    return result

# 添加高级搜索端点
@router.get("/advanced-search", response_model=List[PartResponse])
async def advanced_search(
    name: Optional[str] = Query(None, description="名称搜索"),
    category: Optional[str] = Query(None, description="类别搜索"),
    description: Optional[str] = Query(None, description="描述搜索"),
    properties: Optional[str] = Query(None, description="属性搜索，格式: key:value,key2:value2"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    高级搜索API - 支持精确字段搜索
    """
    query = db.query(Part)
    
    # 名称搜索
    if name:
        query = query.filter(Part.name.ilike(f"%{name}%"))
    
    # 类别搜索
    if category:
        query = query.filter(Part.category == category)
    
    # 描述搜索
    if description:
        query = query.filter(Part.description.ilike(f"%{description}%"))
    
    # 属性搜索
    if properties:
        try:
            # 解析属性搜索：key:value,key2:value2
            prop_conditions = []
            for prop_pair in properties.split(','):
                if ':' in prop_pair:
                    key, value = prop_pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # JSON属性搜索
                    prop_conditions.append(
                        text("properties ->> :key ILIKE :value").bindparam(
                            key=key, value=f"%{value}%"
                        )
                    )
            
            if prop_conditions:
                query = query.filter(and_(*prop_conditions))
                
        except Exception as e:
            print(f"属性搜索出错: {e}")
    
    parts = query.offset(skip).limit(limit).all()
    return parts

@router.get("/{part_id}", response_model=PartResponse)
async def get_part_public(
    part_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取零件详情（公开API）"""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    return part

@router.get("/categories/", response_model=List[str])
async def get_categories_public(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取所有类别（公开API）"""
    categories = db.query(Part.category).distinct().filter(Part.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]

@router.get("/filters/metadata")
async def get_filters_metadata(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    分析数据库中所有零件的properties，返回可筛选的字段元数据
    """
    
    try:
        # 获取所有有properties的零件
        parts_with_properties = db.query(Part.properties, Part.category).filter(
            Part.properties.isnot(None)
        ).all()
        
        print(f"找到 {len(parts_with_properties)} 个有属性的零件")
        
        # 分析字段类型和值
        field_analysis = defaultdict(lambda: {
            'values': [],
            'types': Counter(),
            'count': 0
        })
        
        category_counts = Counter()
        
        # 遍历所有零件的properties
        for part_props, category in parts_with_properties:
            if category:
                category_counts[category] += 1
                
            if part_props and isinstance(part_props, dict):
                for key, value in part_props.items():
                    field_analysis[key]['count'] += 1
                    field_analysis[key]['values'].append(value)
                    
                    # 改进的类型判断逻辑
                    if isinstance(value, bool):
                        field_analysis[key]['types']['boolean'] += 1
                    elif isinstance(value, (int, float)):
                        field_analysis[key]['types']['numeric'] += 1
                    elif isinstance(value, str):
                        # 更精确的数值检测
                        value_str = value.strip()
                        
                        # 检查是否为纯数字
                        if value_str.replace('.', '').replace('-', '').isdigit():
                            field_analysis[key]['types']['numeric'] += 1
                        # 检查是否为带单位的数值（如 "3.3V", "125W"）
                        elif re.match(r'^\d+\.?\d*[A-Za-z]*$', value_str):
                            # 如果数字部分占主要，且单位部分较短，认为是数值
                            numeric_part = re.search(r'(\d+\.?\d*)', value_str)
                            if numeric_part:
                                field_analysis[key]['types']['numeric_with_unit'] += 1
                            else:
                                field_analysis[key]['types']['enum'] += 1
                        else:
                            field_analysis[key]['types']['enum'] += 1
                    else:
                        field_analysis[key]['types']['other'] += 1
        
        print(f"字段分析结果:")
        for field, analysis in field_analysis.items():
            print(f"  {field}: {analysis['count']} 次, 类型: {dict(analysis['types'])}")
        
        # 生成筛选器元数据
        result = {
            'numeric_filters': [],
            'enum_filters': [],
            'boolean_filters': [],
            'categories': []
        }
        
        # 处理分类
        for category, count in category_counts.most_common():
            result['categories'].append({
                'value': category,
                'label': category,
                'count': count
            })
        
        # 处理字段分析结果 - 降低最小出现次数要求
        for field_name, analysis in field_analysis.items():
            if analysis['count'] < 1:  # 改为至少出现1次
                continue
                
            most_common_type = analysis['types'].most_common(1)[0][0] if analysis['types'] else 'other'
            
            # 生成友好的字段标签
            field_label = _generate_field_label(field_name)
            
            print(f"处理字段 {field_name}, 主要类型: {most_common_type}")
            
            if most_common_type == 'boolean':
                # 布尔型筛选器
                true_count = sum(1 for v in analysis['values'] if v is True)
                false_count = analysis['count'] - true_count
                
                result['boolean_filters'].append({
                    'field': field_name,
                    'label': field_label,
                    'true_count': true_count,
                    'false_count': false_count,
                    'count': analysis['count']
                })
                
            elif most_common_type in ['numeric', 'numeric_with_unit']:
                # 数值型筛选器 - 改进数值提取
                numeric_values = []
                unit = None
                
                for value in analysis['values']:
                    try:
                        if isinstance(value, (int, float)):
                            numeric_values.append(float(value))
                        elif isinstance(value, str):
                            # 提取数值部分
                            value_str = str(value).strip()
                            
                            # 尝试直接转换
                            try:
                                numeric_values.append(float(value_str))
                            except ValueError:
                                # 提取数字部分
                                match = re.search(r'(\d+\.?\d*)', value_str)
                                if match:
                                    numeric_values.append(float(match.group(1)))
                                    # 提取单位
                                    if not unit:
                                        unit_match = re.search(r'[A-Za-z]+', value_str)
                                        if unit_match:
                                            unit = unit_match.group()
                    except (ValueError, TypeError):
                        continue
                
                if numeric_values and len(numeric_values) >= 2:  # 至少有2个有效数值
                    min_val = min(numeric_values)
                    max_val = max(numeric_values)
                    
                    # 计算合适的步长
                    value_range = max_val - min_val
                    if value_range <= 1:
                        step = 0.01
                    elif value_range <= 10:
                        step = 0.1
                    elif value_range <= 100:
                        step = 1
                    else:
                        step = 10
                    
                    result['numeric_filters'].append({
                        'field': field_name,
                        'label': field_label,
                        'min': round(min_val, 2),
                        'max': round(max_val, 2),
                        'unit': unit or '',
                        'step': step,
                        'count': len(numeric_values)
                    })
                    print(f"  -> 添加数值筛选器: {field_name} ({min_val}-{max_val})")
                else:
                    # 数值不足，降级为枚举
                    print(f"  -> 数值不足，{field_name} 降级为枚举")
                    most_common_type = 'enum'
            
            if most_common_type == 'enum' or (most_common_type in ['numeric', 'numeric_with_unit'] and field_name not in [f['field'] for f in result['numeric_filters']]):
                # 枚举型筛选器
                value_counts = Counter()
                for v in analysis['values']:
                    if v is not None:
                        # 统一转换为字符串
                        str_val = str(v).strip()
                        if str_val:  # 不为空
                            value_counts[str_val] += 1
                
                # 保留所有有效选项，不限制最小出现次数
                options = []
                for value, count in value_counts.most_common(50):  # 最多50个选项
                    if count >= 1:  # 至少出现1次
                        options.append({
                            'value': value,
                            'label': value,
                            'count': count
                        })
                
                if options:
                    result['enum_filters'].append({
                        'field': field_name,
                        'label': field_label,
                        'options': options,
                        'count': analysis['count']
                    })
                    print(f"  -> 添加枚举筛选器: {field_name} ({len(options)} 个选项)")
        
        # 按使用频率排序
        result['numeric_filters'].sort(key=lambda x: x['count'], reverse=True)
        result['enum_filters'].sort(key=lambda x: x['count'], reverse=True)
        result['boolean_filters'].sort(key=lambda x: x['count'], reverse=True)
        
        print(f"最终结果: {len(result['numeric_filters'])} 数值, {len(result['enum_filters'])} 枚举, {len(result['boolean_filters'])} 布尔")
        
        return result
        
    except Exception as e:
        print(f"分析筛选元数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            'numeric_filters': [],
            'enum_filters': [],
            'boolean_filters': [],
            'categories': []
        }

def _generate_field_label(field_name: str) -> str:
    """生成友好的字段标签 - 扩展版本"""
    
    # 常见字段的中文映射
    field_labels = {
        'voltage': '电压',
        'current': '电流',
        'power': '功率',
        'power_consumption': '功耗',
        'resistance': '电阻',
        'capacitance': '电容',
        'frequency': '频率',
        'temperature': '温度',
        'package': '封装',
        'material': '材料',
        'color': '颜色',
        'size': '尺寸',
        'weight': '重量',
        'length': '长度',
        'width': '宽度',
        'height': '高度',
        'diameter': '直径',
        'thickness': '厚度',
        'brand': '品牌',
        'model': '型号',
        'series': '系列',
        'in_stock': '有库存',
        'available': '可用',
        'new': '新品',
        'recommended': '推荐',
        'price': '价格',
        'quantity': '数量',
        'min_order': '最小订购量',
        'lead_time': '交货期',
        'socket': '接口类型',
        'cores': '核心数',
        'threads': '线程数',
        'tdp': '热设计功耗',
        'memory': '内存',
        'storage': '存储',
        'gpu': '显卡',
        'display': '显示',
        'connectivity': '连接性',
        'interface': '接口',
        'protocol': '协议',
        'speed': '速度',
        'bandwidth': '带宽',
        'latency': '延迟'
    }
    
    # 首先尝试直接映射
    if field_name.lower() in field_labels:
        return field_labels[field_name.lower()]
    
    # 尝试匹配部分关键词
    for key, label in field_labels.items():
        if key in field_name.lower():
            return label
    
    # 如果没有匹配，进行基本的格式化
    # 将下划线替换为空格，首字母大写
    formatted = field_name.replace('_', ' ').title()
    
    # 处理常见的英文缩写
    replacements = {
        'Cpu': 'CPU',
        'Gpu': 'GPU',
        'Ram': 'RAM',
        'Ssd': 'SSD',
        'Hdd': 'HDD',
        'Usb': 'USB',
        'Hdmi': 'HDMI',
        'Wifi': 'WiFi',
        'Bluetooth': 'Bluetooth',
        'Pcie': 'PCIe',
        'Sata': 'SATA',
        'Nvme': 'NVMe',
        'Ddr': 'DDR',
        'Gddr': 'GDDR'
    }
    
    for old, new in replacements.items():
        formatted = formatted.replace(old, new)
    
    return formatted

# backend/app/api/public/parts.py (数值筛选修复版本)

@router.get("/search/advanced", response_model=List[PartResponse])
async def advanced_search_with_filters(
    # 基础搜索参数
    q: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="类别筛选"),
    categories: Optional[str] = Query(None, description="多类别筛选，逗号分隔"),
    
    # 动态筛选参数
    numeric_filters: Optional[str] = Query(None, description="数值筛选，格式: field:min:max,field2:min2:max2"),
    enum_filters: Optional[str] = Query(None, description="枚举筛选，格式: field:value1,value2|field2:value3"),
    boolean_filters: Optional[str] = Query(None, description="布尔筛选，格式: field:true,field2:false"),
    
    # 排序参数
    sort_by: Optional[str] = Query("name", description="排序字段"),
    sort_order: Optional[str] = Query("asc", description="排序顺序: asc/desc"),
    
    # 分页参数
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    高级搜索API - 修复SQL查询构建
    """
    
    print(f"收到高级搜索请求:")
    print(f"  q: {q}")
    print(f"  category: {category}")
    print(f"  categories: {categories}")
    print(f"  numeric_filters: {numeric_filters}")
    print(f"  enum_filters: {enum_filters}")
    print(f"  boolean_filters: {boolean_filters}")
    print(f"  sort_by: {sort_by}, sort_order: {sort_order}")
    
    query = db.query(Part)
    applied_filters = []  # 记录应用的筛选条件
    
    # 基础关键词搜索
    if q and q.strip():
        search_terms = [term.strip() for term in q.split() if term.strip()]
        print(f"  搜索词: {search_terms}")
        
        if search_terms:
            for term in search_terms:
                search_term = f"%{term}%"
                term_conditions = [
                    Part.name.ilike(search_term),
                    Part.description.ilike(search_term),
                    Part.category.ilike(search_term),
                ]
                
                try:
                    # 修复：正确使用text()和bindparam()
                    term_conditions.append(
                        text("properties::text ILIKE :search_term").params(search_term=search_term)
                    )
                except Exception as e:
                    print(f"  关键词搜索SQL错误: {e}")
                
                query = query.filter(or_(*term_conditions))
                applied_filters.append(f"关键词搜索: {term}")
    
    # 类别筛选 - 支持单个和多个
    if categories:
        # 多分类筛选
        category_list = [c.strip() for c in categories.split(',') if c.strip()]
        print(f"  多分类筛选: {category_list}")
        if category_list:
            query = query.filter(Part.category.in_(category_list))
            applied_filters.append(f"分类筛选: {', '.join(category_list)}")
    elif category:
        # 单分类筛选
        print(f"  单分类筛选: {category}")
        query = query.filter(Part.category == category)
        applied_filters.append(f"分类筛选: {category}")
    
    # 数值筛选
    if numeric_filters:
        print(f"  处理数值筛选: {numeric_filters}")
        try:
            for filter_spec in numeric_filters.split(','):
                parts = filter_spec.strip().split(':')
                if len(parts) == 3:
                    field, min_val, max_val = parts
                    field = field.strip()
                    
                    # 处理空值
                    min_val = float(min_val) if min_val.strip() else None
                    max_val = float(max_val) if max_val.strip() else None
                    
                    print(f"    数值筛选: {field} 范围 {min_val} - {max_val}")
                    
                    # 构建数值筛选条件 - 修复bindparam用法
                    if min_val is not None and max_val is not None:
                        # 检查字段值是否为数字，并在范围内
                        condition = text("""
                            (properties ->> :field) ~ '^[0-9.]+$' 
                            AND (properties ->> :field)::numeric BETWEEN :min_val AND :max_val
                        """).params(field=field, min_val=min_val, max_val=max_val)
                        query = query.filter(condition)
                        applied_filters.append(f"数值筛选: {field} [{min_val}-{max_val}]")
                        
                    elif min_val is not None:
                        condition = text("""
                            (properties ->> :field) ~ '^[0-9.]+$' 
                            AND (properties ->> :field)::numeric >= :min_val
                        """).params(field=field, min_val=min_val)
                        query = query.filter(condition)
                        applied_filters.append(f"数值筛选: {field} [>={min_val}]")
                        
                    elif max_val is not None:
                        condition = text("""
                            (properties ->> :field) ~ '^[0-9.]+$' 
                            AND (properties ->> :field)::numeric <= :max_val
                        """).params(field=field, max_val=max_val)
                        query = query.filter(condition)
                        applied_filters.append(f"数值筛选: {field} [<={max_val}]")
                        
        except Exception as e:
            print(f"  数值筛选错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 枚举筛选 - 修复SQL构建
    if enum_filters:
        print(f"  处理枚举筛选: {enum_filters}")
        try:
            for filter_spec in enum_filters.split('|'):
                if ':' in filter_spec:
                    field, values_str = filter_spec.split(':', 1)
                    field = field.strip()
                    values = [v.strip() for v in values_str.split(',') if v.strip()]
                    
                    print(f"    枚举筛选: {field} 值 {values}")
                    
                    if values:
                        # 构建OR条件 - 修复SQL语法
                        enum_conditions = []
                        for i, value in enumerate(values):
                            # 为每个值创建独立的参数名
                            param_name = f"{field}_value_{i}"
                            condition = text(f"properties ->> :{field}_field = :{param_name}").params(**{
                                f"{field}_field": field,
                                param_name: value
                            })
                            enum_conditions.append(condition)
                        
                        if enum_conditions:
                            query = query.filter(or_(*enum_conditions))
                            applied_filters.append(f"枚举筛选: {field} [{', '.join(values)}]")
                            print(f"    -> 应用枚举筛选: {field} = {values}")
                        
        except Exception as e:
            print(f"  枚举筛选错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 布尔筛选
    if boolean_filters:
        print(f"  处理布尔筛选: {boolean_filters}")
        try:
            for filter_spec in boolean_filters.split(','):
                if ':' in filter_spec:
                    field, bool_value = filter_spec.split(':', 1)
                    field = field.strip()
                    bool_value = bool_value.strip().lower() == 'true'
                    
                    print(f"    布尔筛选: {field} = {bool_value}")
                    
                    condition = text("(properties ->> :field)::boolean = :bool_value").params(
                        field=field, bool_value=bool_value
                    )
                    query = query.filter(condition)
                    applied_filters.append(f"布尔筛选: {field} = {bool_value}")
                    
        except Exception as e:
            print(f"  布尔筛选错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 排序
    try:
        if sort_by == 'name':
            order_col = Part.name
        elif sort_by == 'category':
            order_col = Part.category
        elif sort_by == 'created_at':
            order_col = Part.created_at
        else:
            # 尝试按properties中的字段排序
            print(f"  按属性排序: {sort_by}")
            if sort_order.lower() == 'desc':
                query = query.order_by(
                    text("(properties ->> :sort_field)::text DESC NULLS LAST").params(sort_field=sort_by)
                )
            else:
                query = query.order_by(
                    text("(properties ->> :sort_field)::text ASC NULLS LAST").params(sort_field=sort_by)
                )
            order_col = None
        
        if order_col is not None:
            if sort_order.lower() == 'desc':
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col.asc())
                
    except Exception as e:
        print(f"  排序错误: {e}")
        # 降级到默认排序
        query = query.order_by(Part.name.asc())
    
    # 执行查询
    try:
        print(f"应用的筛选条件: {applied_filters}")
        
        # 分页
        parts = query.offset(skip).limit(limit).all()
        
        print(f"  返回结果: {len(parts)} 个零件")
        
        # 调试：显示前几个结果
        for i, part in enumerate(parts[:3]):
            print(f"  示例零件 {i+1}: {part.name}, properties: {part.properties}")
        
        return parts
        
    except Exception as e:
        print(f"  SQL执行错误: {e}")
        import traceback
        traceback.print_exc()
        return []

# 同时需要修复筛选元数据API，确保正确分析数值字段
@router.get("/filters/metadata")
async def get_filters_metadata(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    分析数据库中所有零件的properties，返回可筛选的字段元数据（修复版本）
    """
    
    try:
        # 获取所有有properties的零件
        parts_with_properties = db.query(Part.properties, Part.category).filter(
            Part.properties.isnot(None)
        ).all()
        
        print(f"分析 {len(parts_with_properties)} 个零件的属性")
        
        # 分析字段类型和值
        field_analysis = defaultdict(lambda: {
            'values': [],
            'types': Counter(),
            'count': 0
        })
        
        category_counts = Counter()
        
        # 遍历所有零件的properties
        for part_props, category in parts_with_properties:
            if category:
                category_counts[category] += 1
                
            if part_props and isinstance(part_props, dict):
                for key, value in part_props.items():
                    field_analysis[key]['count'] += 1
                    field_analysis[key]['values'].append(value)
                    
                    # 判断值的类型
                    if isinstance(value, bool):
                        field_analysis[key]['types']['boolean'] += 1
                    elif isinstance(value, (int, float)):
                        field_analysis[key]['types']['numeric'] += 1
                    elif isinstance(value, str):
                        # 改进的数值检测
                        value_str = str(value).strip()
                        
                        # 检查是否是纯数字
                        if re.match(r'^[0-9]*\.?[0-9]+$', value_str):
                            field_analysis[key]['types']['numeric'] += 1
                        # 检查是否是带单位的数字
                        elif re.match(r'^[0-9]*\.?[0-9]+[a-zA-ZΩμ]+$', value_str):
                            field_analysis[key]['types']['numeric_with_unit'] += 1
                        # 检查是否是科学计数法
                        elif re.match(r'^[0-9]*\.?[0-9]+[eE][+-]?[0-9]+$', value_str):
                            field_analysis[key]['types']['numeric'] += 1
                        else:
                            field_analysis[key]['types']['enum'] += 1
                    else:
                        field_analysis[key]['types']['other'] += 1
        
        print(f"字段分析结果:")
        for field_name, analysis in field_analysis.items():
            print(f"  {field_name}: {analysis['types']}")
        
        # 生成筛选器元数据
        result = {
            'numeric_filters': [],
            'enum_filters': [],
            'boolean_filters': [],
            'categories': []
        }
        
        # 处理分类
        for category, count in category_counts.most_common():
            result['categories'].append({
                'value': category,
                'label': category,
                'count': count
            })
        
        # 处理字段分析结果
        for field_name, analysis in field_analysis.items():
            if analysis['count'] < 3:  # 忽略出现次数太少的字段
                continue
                
            most_common_type = analysis['types'].most_common(1)[0][0] if analysis['types'] else 'other'
            
            # 生成友好的字段标签
            field_label = _generate_field_label(field_name)
            
            if most_common_type == 'boolean':
                # 布尔型筛选器
                true_count = sum(1 for v in analysis['values'] if v is True)
                false_count = analysis['count'] - true_count
                
                result['boolean_filters'].append({
                    'field': field_name,
                    'label': field_label,
                    'true_count': true_count,
                    'false_count': false_count,
                    'count': analysis['count']
                })
                
            elif most_common_type in ['numeric', 'numeric_with_unit']:
                # 数值型筛选器
                numeric_values = []
                unit = None
                
                for value in analysis['values']:
                    try:
                        if isinstance(value, (int, float)):
                            numeric_values.append(float(value))
                        elif isinstance(value, str):
                            # 提取数值
                            value_str = str(value).strip()
                            
                            # 纯数字
                            if re.match(r'^[0-9]*\.?[0-9]+$', value_str):
                                numeric_values.append(float(value_str))
                            # 带单位的数字
                            elif re.match(r'^[0-9]*\.?[0-9]+[a-zA-ZΩμ]+$', value_str):
                                match = re.match(r'^([0-9]*\.?[0-9]+)([a-zA-ZΩμ]+)$', value_str)
                                if match:
                                    numeric_values.append(float(match.group(1)))
                                    if not unit and match.group(2):
                                        unit = match.group(2)
                            # 科学计数法
                            elif re.match(r'^[0-9]*\.?[0-9]+[eE][+-]?[0-9]+$', value_str):
                                numeric_values.append(float(value_str))
                    except (ValueError, TypeError):
                        continue
                
                if numeric_values:
                    min_val = min(numeric_values)
                    max_val = max(numeric_values)
                    
                    # 计算合适的步长
                    value_range = max_val - min_val
                    if value_range <= 1:
                        step = 0.01
                    elif value_range <= 10:
                        step = 0.1
                    elif value_range <= 100:
                        step = 1
                    else:
                        step = 10
                    
                    result['numeric_filters'].append({
                        'field': field_name,
                        'label': field_label,
                        'min': round(min_val, 2),
                        'max': round(max_val, 2),
                        'unit': unit or '',
                        'step': step,
                        'count': len(numeric_values)
                    })
                    
                    print(f"  添加数值筛选器: {field_name} ({min_val}-{max_val}{unit or ''})")
                    
            else:
                # 枚举型筛选器
                value_counts = Counter(str(v) for v in analysis['values'] if v is not None)
                
                # 只保留出现次数较多的选项
                options = []
                for value, count in value_counts.most_common(20):  # 最多20个选项
                    if count >= 2:  # 至少出现2次
                        options.append({
                            'value': value,
                            'label': value,
                            'count': count
                        })
                
                if options:
                    result['enum_filters'].append({
                        'field': field_name,
                        'label': field_label,
                        'options': options,
                        'count': analysis['count']
                    })
        
        # 按使用频率排序
        result['numeric_filters'].sort(key=lambda x: x['count'], reverse=True)
        result['enum_filters'].sort(key=lambda x: x['count'], reverse=True)
        result['boolean_filters'].sort(key=lambda x: x['count'], reverse=True)
        
        print(f"生成筛选器元数据: {len(result['numeric_filters'])} 数值, {len(result['enum_filters'])} 枚举, {len(result['boolean_filters'])} 布尔")
        
        return result
        
    except Exception as e:
        print(f"分析筛选元数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            'numeric_filters': [],
            'enum_filters': [],
            'boolean_filters': [],
            'categories': []
        }