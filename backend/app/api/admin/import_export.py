# backend/app/api/admin/import_export.py (修复版本)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import csv
import io
from datetime import datetime, date
from app.core.database import get_db
from app.models.part import Part
from app.auth.middleware import require_admin
from app.auth.models import User
from app.schemas.part import PartCreate
from pydantic import BaseModel

router = APIRouter()

class ImportResult(BaseModel):
    total_processed: int
    successful_imports: int
    skipped_duplicates: int
    updated_existing: int
    errors: List[Dict[str, Any]]
    
class ExportOptions(BaseModel):
    format: str = "json"  # json 或 csv
    include_images: bool = True
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    categories: Optional[List[str]] = None

@router.post("/export", response_class=StreamingResponse)
async def export_parts_data(
    options: ExportOptions,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    导出零件数据
    """
    
    try:
        # 构建查询
        query = db.query(Part)
        
        # 时间范围筛选
        if options.date_from:
            date_from = datetime.fromisoformat(options.date_from)
            query = query.filter(Part.created_at >= date_from)
            
        if options.date_to:
            date_to = datetime.fromisoformat(options.date_to)
            query = query.filter(Part.created_at <= date_to)
            
        # 类别筛选
        if options.categories:
            query = query.filter(Part.category.in_(options.categories))
            
        parts = query.all()
        
        # 准备导出数据
        export_data = []
        for part in parts:
            part_data = {
                "id": part.id,
                "name": part.name,
                "category": part.category,
                "description": part.description,
                "properties": part.properties,
                "created_at": part.created_at.isoformat() if part.created_at else None,
                "updated_at": part.updated_at.isoformat() if part.updated_at else None
            }
            
            # 是否包含图片信息
            if options.include_images:
                part_data["image_url"] = part.image_url
                
            export_data.append(part_data)
        
        # 生成文件
        if options.format.lower() == "json":
            return _export_as_json(export_data)
        elif options.format.lower() == "csv":
            return _export_as_csv(export_data)
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

def _export_as_json(data: List[Dict]) -> StreamingResponse:
    """导出为JSON格式"""
    
    export_package = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "total_records": len(data),
            "format": "json"
        },
        "data": data
    }
    
    json_str = json.dumps(export_package, ensure_ascii=False, indent=2)
    json_bytes = json_str.encode('utf-8')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"openpart_export_{timestamp}.json"
    
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def _export_as_csv(data: List[Dict]) -> StreamingResponse:
    """导出为CSV格式 - 修复版本"""
    
    if not data:
        raise HTTPException(status_code=400, detail="没有数据可导出")
    
    # 处理嵌套的properties字段
    flattened_data = []
    all_property_keys = set()
    
    # 收集所有属性键
    for item in data:
        if item.get('properties') and isinstance(item['properties'], dict):
            all_property_keys.update(item['properties'].keys())
    
    # 定义基础字段顺序
    basic_fields = ["id", "name", "category", "description", "image_url", "created_at", "updated_at"]
    
    # 展平数据
    for item in data:
        flat_item = {}
        
        # 添加基础字段
        for field in basic_fields:
            flat_item[field] = str(item.get(field, "")) if item.get(field) is not None else ""
        
        # 添加属性字段
        if item.get('properties') and isinstance(item['properties'], dict):
            for key in sorted(all_property_keys):  # 排序保证字段顺序一致
                prop_key = f"prop_{key}"
                flat_item[prop_key] = str(item['properties'].get(key, ""))
        else:
            for key in sorted(all_property_keys):
                prop_key = f"prop_{key}"
                flat_item[prop_key] = ""
                
        flattened_data.append(flat_item)
    
    # 确定最终的字段名列表
    if flattened_data:
        # 基础字段 + 属性字段（按字母顺序）
        prop_fields = sorted([f for f in flattened_data[0].keys() if f.startswith("prop_")])
        final_fieldnames = basic_fields + prop_fields
    else:
        final_fieldnames = basic_fields
    
    # 生成CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=final_fieldnames)
    writer.writeheader()
    
    # 确保每行数据都包含所有字段
    for row in flattened_data:
        normalized_row = {}
        for field in final_fieldnames:
            normalized_row[field] = row.get(field, "")
        writer.writerow(normalized_row)
    
    csv_content = output.getvalue()
    csv_bytes = csv_content.encode('utf-8-sig')  # 使用BOM，Excel可以正确识别中文
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"openpart_export_{timestamp}.csv"
    
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# 修复导入API - 简化参数处理
@router.post("/import", response_model=ImportResult)
async def import_parts_data(
    file: UploadFile = File(...),
    conflict_strategy: str = Form("skip"),  # 使用Form而不是复杂的options对象
    validate_data: bool = Form(True),
    duplicate_check_name: bool = Form(True),
    duplicate_check_category: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    导入零件数据 - 修复版本
    """
    
    try:
        print(f"开始导入文件: {file.filename}")
        print(f"冲突策略: {conflict_strategy}")
        print(f"数据验证: {validate_data}")
        
        # 读取文件内容
        file_content = await file.read()
        print(f"文件大小: {len(file_content)} bytes")
        
        # 根据文件类型解析数据
        if file.filename.endswith('.json'):
            data = _parse_json_file(file_content)
        elif file.filename.endswith('.csv'):
            data = _parse_csv_file(file_content)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，请使用JSON或CSV文件")
        
        print(f"解析到 {len(data)} 条记录")
        
        # 构建重复检查字段列表
        duplicate_check_fields = []
        if duplicate_check_name:
            duplicate_check_fields.append("name")
        if duplicate_check_category:
            duplicate_check_fields.append("category")
        
        # 执行导入
        result = _import_parts_data(data, conflict_strategy, duplicate_check_fields, validate_data, db)
        
        print(f"导入完成: {result}")
        return result
        
    except Exception as e:
        print(f"导入异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

def _parse_json_file(content: bytes) -> List[Dict]:
    """解析JSON文件"""
    try:
        text_content = content.decode('utf-8')
        print("JSON内容前100字符:", text_content[:100])
        
        json_data = json.loads(text_content)
        
        # 支持导出的包装格式
        if isinstance(json_data, dict) and 'data' in json_data:
            print(f"检测到包装格式，提取data字段，包含 {len(json_data['data'])} 条记录")
            return json_data['data']
        elif isinstance(json_data, list):
            print(f"检测到数组格式，包含 {len(json_data)} 条记录")
            return json_data
        else:
            raise ValueError("JSON格式不正确，应为数组或包含data字段的对象")
            
    except Exception as e:
        print(f"JSON解析错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"JSON文件解析失败: {str(e)}")

def _parse_csv_file(content: bytes) -> List[Dict]:
    """解析CSV文件 - 改进版本"""
    try:
        # 尝试不同的编码方式
        text_content = None
        for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
            try:
                text_content = content.decode(encoding)
                print(f"使用编码 {encoding} 成功解析CSV")
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            raise HTTPException(status_code=400, detail="无法解析CSV文件编码")
        
        print("CSV内容前300字符:", repr(text_content[:300]))
        
        # 解析CSV
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        data = []
        for row_num, row in enumerate(csv_reader, 1):
            # 跳过注释行
            if any(str(value).strip().startswith('#') for value in row.values()):
                print(f"跳过注释行 {row_num}")
                continue
                
            # 跳过空行
            if all(not str(value).strip() for value in row.values()):
                print(f"跳过空行 {row_num}")
                continue
            
            print(f"处理第 {row_num} 行: {dict(row)}")
            
            # 重新组装properties
            properties = {}
            clean_row = {}
            
            for key, value in row.items():
                if not key:  # 跳过空键
                    continue
                    
                key = key.strip()
                value = str(value).strip() if value else ""
                
                if key.startswith('prop_') and value:
                    prop_key = key[5:]  # 移除 'prop_' 前缀
                    properties[prop_key] = value
                elif key in ['id', 'name', 'category', 'description', 'image_url', 'created_at', 'updated_at']:
                    clean_row[key] = value if value else None
            
            # 只有在有名称的情况下才添加记录
            if clean_row.get('name'):
                if properties:
                    clean_row['properties'] = properties
                data.append(clean_row)
                print(f"成功处理记录: {clean_row['name']}")
        
        print(f"CSV解析完成，共处理 {len(data)} 条有效记录")
        return data
        
    except Exception as e:
        print(f"CSV解析错误详情: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"CSV文件解析失败: {str(e)}")

def _import_parts_data(
    data: List[Dict], 
    conflict_strategy: str, 
    duplicate_check_fields: List[str], 
    validate_data: bool, 
    db: Session
) -> ImportResult:
    """执行数据导入"""
    
    result = ImportResult(
        total_processed=0,
        successful_imports=0,
        skipped_duplicates=0,
        updated_existing=0,
        errors=[]
    )
    
    print(f"开始处理 {len(data)} 条记录")
    
    for i, item_data in enumerate(data):
        result.total_processed += 1
        
        try:
            print(f"处理第 {i+1} 条记录: {item_data.get('name', 'Unknown')}")
            
            # 数据验证
            if validate_data:
                if not item_data.get('name'):
                    error_msg = "缺少必需字段: name"
                    print(f"验证失败: {error_msg}")
                    result.errors.append({
                        "row": i + 1,
                        "error": error_msg
                    })
                    continue
            
            # 检查重复
            existing_part = _find_duplicate_part(item_data, duplicate_check_fields, db)
            
            if existing_part:
                print(f"发现重复零件: {existing_part.name} (ID: {existing_part.id})")
                
                if conflict_strategy == "skip":
                    result.skipped_duplicates += 1
                    print("跳过重复记录")
                    continue
                elif conflict_strategy == "update":
                    _update_existing_part(existing_part, item_data, db)
                    result.updated_existing += 1
                    print("更新现有记录")
                    continue
                elif conflict_strategy == "rename":
                    item_data['name'] = _generate_unique_name(item_data['name'], db)
                    print(f"重命名为: {item_data['name']}")
            
            # 创建新零件 - 过滤掉导入时不需要的字段
            part_data = {
                "name": item_data.get('name'),
                "category": item_data.get('category'),
                "description": item_data.get('description'),
                "properties": item_data.get('properties'),
                "image_url": item_data.get('image_url')
            }
            
            # 过滤None值和空字符串
            part_data = {k: v for k, v in part_data.items() if v is not None and v != ""}
            
            print(f"创建零件数据: {part_data}")
            
            new_part = Part(**part_data)
            db.add(new_part)
            db.commit()
            db.refresh(new_part)
            
            result.successful_imports += 1
            print(f"成功创建零件: {new_part.name} (ID: {new_part.id})")
            
        except Exception as e:
            error_msg = f"处理记录时出错: {str(e)}"
            print(f"错误: {error_msg}")
            result.errors.append({
                "row": i + 1,
                "error": error_msg
            })
            db.rollback()
            continue
    
    print(f"导入完成: {result}")
    return result

def _find_duplicate_part(item_data: Dict, check_fields: List[str], db: Session) -> Optional[Part]:
    """查找重复的零件"""
    
    if not check_fields:
        return None
    
    query = db.query(Part)
    conditions = []
    
    for field in check_fields:
        if field in item_data and item_data[field]:
            if field == "name":
                conditions.append(Part.name == item_data[field])
            elif field == "category":
                conditions.append(Part.category == item_data[field])
    
    if conditions:
        from sqlalchemy import and_
        result = query.filter(and_(*conditions)).first()
        return result
    
    return None

def _update_existing_part(existing_part: Part, new_data: Dict, db: Session):
    """更新现有零件"""
    
    update_fields = ['category', 'description', 'properties', 'image_url']
    
    for field in update_fields:
        if field in new_data and new_data[field] is not None and new_data[field] != "":
            setattr(existing_part, field, new_data[field])
    
    existing_part.updated_at = datetime.utcnow()
    db.commit()

def _generate_unique_name(base_name: str, db: Session) -> str:
    """生成唯一的名称"""
    
    counter = 1
    new_name = f"{base_name}_副本"
    
    while db.query(Part).filter(Part.name == new_name).first():
        counter += 1
        new_name = f"{base_name}_副本_{counter}"
    
    return new_name

@router.get("/import/template")
async def download_import_template(
    format: str = Query("csv", description="模板格式: csv 或 json"),
    current_user: User = Depends(require_admin)
):
    """下载导入模板文件"""
    
    if format.lower() == "csv":
        return _generate_csv_template()
    elif format.lower() == "json":
        return _generate_json_template()
    else:
        raise HTTPException(status_code=400, detail="不支持的模板格式")

def _generate_csv_template() -> StreamingResponse:
    """生成CSV模板 - 完全重写版本"""
    
    # 定义模板数据结构 - 使用更简单的结构避免字段不匹配
    basic_fields = ["name", "category", "description", "image_url"]
    
    # 预定义一些常见的属性字段
    common_props = ["prop_阻值", "prop_功率", "prop_精度", "prop_容量", "prop_电压", "prop_类型"]
    
    # 组合所有字段
    all_fields = basic_fields + common_props
    
    # 创建模板数据 - 确保所有字段都存在
    template_rows = [
        {
            "name": "示例零件1",
            "category": "电阻", 
            "description": "这是一个示例电阻零件",
            "image_url": "",
            "prop_阻值": "1kΩ",
            "prop_功率": "0.25W", 
            "prop_精度": "±5%",
            "prop_容量": "",
            "prop_电压": "",
            "prop_类型": ""
        },
        {
            "name": "示例零件2",
            "category": "电容",
            "description": "这是一个示例电容零件", 
            "image_url": "",
            "prop_阻值": "",
            "prop_功率": "",
            "prop_精度": "",
            "prop_容量": "100μF",
            "prop_电压": "16V",
            "prop_类型": "电解电容"
        },
        {
            "name": "示例零件3",
            "category": "集成电路",
            "description": "这是一个没有属性的示例零件",
            "image_url": "",
            "prop_阻值": "",
            "prop_功率": "",
            "prop_精度": "",
            "prop_容量": "",
            "prop_电压": "",
            "prop_类型": ""
        }
    ]
    
    try:
        # 生成CSV内容
        output = io.StringIO()
        
        # 使用确定的字段顺序
        writer = csv.DictWriter(output, fieldnames=all_fields)
        writer.writeheader()
        
        # 写入数据行
        for row in template_rows:
            # 确保行数据完整
            complete_row = {}
            for field in all_fields:
                complete_row[field] = row.get(field, "")
            writer.writerow(complete_row)
        
        # 添加说明行
        comment_row = {}
        for field in all_fields:
            if field == "name":
                comment_row[field] = "# 说明：name为必填字段"
            elif field.startswith("prop_"):
                comment_row[field] = "# 自定义属性，可为空"
            else:
                comment_row[field] = "# 可选字段"
        writer.writerow(comment_row)
        
        csv_content = output.getvalue()
        csv_bytes = csv_content.encode('utf-8-sig')
        
        print(f"CSV模板生成成功，长度: {len(csv_bytes)} 字节")
        print("CSV内容预览:")
        print(csv_content[:500])
        
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=import_template.csv"}
        )
        
    except Exception as e:
        print(f"CSV模板生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"CSV模板生成失败: {str(e)}")

def _generate_json_template() -> StreamingResponse:
    """生成JSON模板"""
    
    template_data = {
        "import_info": {
            "format": "json",
            "version": "1.0",
            "description": "OpenPart 导入模板 - 请修改data数组中的内容"
        },
        "data": [
            {
                "name": "示例零件1",
                "category": "电阻",
                "description": "这是一个示例零件",
                "image_url": "",
                "properties": {
                    "阻值": "1kΩ",
                    "功率": "0.25W",
                    "精度": "±5%"
                }
            },
            {
                "name": "示例零件2",
                "category": "电容", 
                "description": "另一个示例零件",
                "image_url": "",
                "properties": {
                    "容量": "100μF",
                    "电压": "16V",
                    "类型": "电解电容"
                }
            }
        ]
    }
    
    json_str = json.dumps(template_data, ensure_ascii=False, indent=2)
    json_bytes = json_str.encode('utf-8')
    
    return StreamingResponse(
        io.BytesIO(json_bytes), 
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=import_template.json"}
    )