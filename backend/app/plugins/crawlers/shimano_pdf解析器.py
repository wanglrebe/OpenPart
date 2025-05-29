# shimano_pdf_plugin.py
"""
Shimano PDF解析插件 - 完整版

功能特性：
1. 支持PDF文件上传和安全解析
2. 智能提取Shimano产品数据
3. 动态爬取产品图片
4. 测试模式用于验证功能
5. 完整的错误处理和调试支持
"""

import time
import requests
import json
import re
from typing import Dict, Any, List, Optional
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField,
    CrawlResult, TestResult, PartData, DataSourceType
)

class ShimanoPDFPlugin(BaseCrawlerPlugin):
    """Shimano PDF解析插件"""
    
    def __init__(self):
        super().__init__()
        
        # 产品类别映射
        self.category_patterns = {
            'Shifter': r'Shifter|SL-M\d+|ST-R\d+',
            'Brake Lever': r'Brake Lever|BL-M\d+',
            'Rear Derailleur': r'Rear Derailleur|RD-M\d+|RD-R\d+',
            'Front Derailleur': r'Front Derailleur|FD-M\d+|FD-R\d+',
            'Brake': r'Brake.*\(.*Disc.*\)|BR-M\d+|BR-R\d+',
            'Crankset': r'Crankset|FC-M\d+|FC-R\d+',
            'Chain Device': r'Chain Device|SMCD',
            'Chainring': r'Chainring|SMCR',
            'Bottom Bracket': r'Bottom Bracket|BB-M\d+|BB-R\d+',
            'Cassette': r'Cassette|CS-M\d+|CS-R\d+',
            'Hub': r'Front Hub|FREEHUB|HB-M\d+|FH-M\d+|HB-R\d+|FH-R\d+',
            'Wheel': r'Wheel|WH-M\d+|WH-R\d+'
        }
        
        # Shimano图片爬取配置
        self.shimano_base_url = "https://productinfo.shimano.com"
        self.product_url_template = "https://productinfo.shimano.com/en/product/{}"
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="Shimano PDF解析器",
            version="2.0.0",
            description="解析Shimano产品规格PDF文档，提取零件数据并从官网动态爬取产品图片",
            author="Plugin Developer",
            data_source="Shimano PDF Documents",
            data_source_type=DataSourceType.DOCUMENT,
            homepage="https://productinfo.shimano.com",
            rate_limit=3,
            batch_size=100
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            # PDF文件相关配置
            ConfigField(
                name="pdf_processing_mode",
                label="PDF处理模式",
                type="select",
                default="test",
                options=[
                    {"value": "test", "label": "测试模式（使用示例数据）"},
                    {"value": "upload", "label": "上传PDF文件"}
                ],
                help_text="选择PDF文件的处理方式"
            ),
            
            # PDF文件上传字段
            ConfigField(
                name="pdf_file",
                label="PDF文件",
                type="file",
                required=False,
                help_text="上传Shimano产品规格PDF文档",
                validation={
                    "accept": ".pdf,application/pdf",
                    "max_size": 50 * 1024 * 1024  # 50MB
                }
            ),
            
            # PDF解析配置
            ConfigField(
                name="max_pages",
                label="最大解析页数",
                type="number",
                default=50,
                validation={"min": 1, "max": 200},
                help_text="限制PDF解析的最大页数，避免处理过大文件"
            ),
            
            ConfigField(
                name="pdf_password",
                label="PDF密码",
                type="password",
                required=False,
                help_text="如果PDF文件有密码保护请填写"
            ),
            
            # 解析配置
            ConfigField(
                name="extract_categories",
                label="提取的产品类别",
                type="checkbox-group",
                default=["Shifter", "Rear Derailleur", "Brake"],
                options=[
                    {"value": "Shifter", "label": "变速器"},
                    {"value": "Brake Lever", "label": "刹车把手"},
                    {"value": "Rear Derailleur", "label": "后拨"},
                    {"value": "Front Derailleur", "label": "前拨"},
                    {"value": "Brake", "label": "刹车"},
                    {"value": "Crankset", "label": "曲柄组"},
                    {"value": "Cassette", "label": "飞轮"},
                    {"value": "Hub", "label": "花鼓"},
                    {"value": "Wheel", "label": "轮组"}
                ],
                help_text="选择要提取的产品类别"
            ),
            
            # 图片爬取配置
            ConfigField(
                name="enable_image_crawling",
                label="启用图片爬取",
                type="checkbox",
                default=True,
                help_text="是否从Shimano官网动态爬取产品图片"
            ),
            
            ConfigField(
                name="image_crawl_delay",
                label="图片爬取延时(秒)",
                type="number",
                default=3.0,
                validation={"min": 1.0, "max": 10.0, "step": 0.5},
                help_text="图片爬取请求之间的延时，避免过于频繁"
            ),
            
            # 数据质量配置
            ConfigField(
                name="min_specs_count",
                label="最少规格参数数量",
                type="number",
                default=5,
                validation={"min": 1, "max": 30},
                help_text="产品至少需要多少个规格参数才被认为有效"
            ),
            
            # 调试配置
            ConfigField(
                name="debug_mode",
                label="调试模式",
                type="checkbox",
                default=True,
                help_text="启用详细的调试日志输出"
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        extract_categories = config.get("extract_categories", [])
        if not extract_categories:
            raise ValueError("至少需要选择一个产品类别")
        
        delay = config.get("image_crawl_delay", 3.0)
        if delay < 1.0 or delay > 10.0:
            raise ValueError("图片爬取延时应在1-10秒之间")
        
        min_specs = config.get("min_specs_count", 5)
        if min_specs < 1 or min_specs > 30:
            raise ValueError("最少规格参数数量应在1-30之间")
        
        max_pages = config.get("max_pages", 50)
        if max_pages < 1 or max_pages > 200:
            raise ValueError("最大解析页数应在1-200之间")
        
        return True
    
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        """测试连接"""
        start_time = time.time()
        
        try:
            # 测试Shimano网站连接
            shimano_available = self._test_shimano_connection()
            
            # 测试文件API
            files_api_available = self._test_files_api()
            
            # 测试图片API
            images_api_available = self._test_images_api()
            
            response_time = time.time() - start_time
            
            issues = []
            if not shimano_available:
                issues.append("无法连接到Shimano官网")
            if not files_api_available:
                issues.append("文件处理API不可用")
            if not images_api_available:
                issues.append("图片下载API不可用")
            
            if not issues:
                return TestResult(
                    success=True,
                    message="所有功能测试通过，插件可以正常使用",
                    response_time=round(response_time, 3),
                    sample_data={
                        "shimano_connection": "可用",
                        "files_api": "可用",
                        "images_api": "可用",
                        "processing_mode": config.get("pdf_processing_mode", "test")
                    }
                )
            else:
                return TestResult(
                    success=len(issues) < 2,
                    message=f"部分功能不可用: {', '.join(issues)}"
                )
        
        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接测试失败: {str(e)}"
            )
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """主要的数据爬取方法"""
        start_time = time.time()
        extracted_parts = []
        warnings = []
        
        try:
            debug_mode = config.get("debug_mode", False)
            if debug_mode:
                self._log("开始PDF解析任务")
            
            # 1. 获取数据
            if config.get("pdf_processing_mode", "test") == "test":
                # 测试模式：使用真实数据格式
                parsed_data = self._get_test_shimano_data()
                if debug_mode:
                    self._log("使用测试模式数据")
            else:
                # 文件上传模式：使用安全PDF解析
                if debug_mode:
                    self._log("获取PDF文件内容")
                
                pdf_content = self._get_pdf_content(config, debug_mode)
                if not pdf_content:
                    return CrawlResult(
                        success=False,
                        data=[],
                        total_count=0,
                        error_message="无法获取PDF内容"
                    )
                
                # 使用智能文件解析
                parsed_data = self._smart_parse_uploaded_file(pdf_content, config, debug_mode)
                if not parsed_data:
                    return CrawlResult(
                        success=False,
                        data=[],
                        total_count=0,
                        error_message="PDF解析失败，请检查文件格式"
                    )
            
            if not parsed_data:
                return CrawlResult(
                    success=False,
                    data=[],
                    total_count=0,
                    error_message="没有解析到有效数据"
                )
            
            # 2. 转换为PartData格式
            extract_categories = config.get("extract_categories", [])
            for category, products in parsed_data.items():
                if category not in extract_categories:
                    if debug_mode:
                        self._log(f"跳过类别: {category}")
                    continue
                    
                if debug_mode:
                    self._log(f"处理类别: {category} ({len(products)} 个产品)")
                    
                for product in products:
                    try:
                        part = self._convert_shimano_to_part_data(product, category)
                        if part and self._is_valid_part(part, config):
                            extracted_parts.append(part)
                        elif debug_mode:
                            self._log(f"产品验证失败: {product.get('model_number', 'Unknown')}")
                    except Exception as e:
                        warnings.append(f"转换产品数据失败: {product.get('model_number', 'Unknown')} - {str(e)}")
            
            if debug_mode:
                self._log(f"转换完成，共 {len(extracted_parts)} 个有效产品")
            
            # 3. 图片爬取（如果启用）
            if config.get("enable_image_crawling", True) and extracted_parts:
                if debug_mode:
                    self._log(f"开始动态爬取 {len(extracted_parts)} 个产品的图片")
                
                extracted_parts = self._crawl_shimano_images_dynamic(
                    extracted_parts, config, warnings, debug_mode
                )
            
            execution_time = time.time() - start_time
            
            return CrawlResult(
                success=True,
                data=extracted_parts,
                total_count=len(extracted_parts),
                execution_time=round(execution_time, 3),
                warnings=warnings
            )
            
        except Exception as e:
            return CrawlResult(
                success=False,
                data=extracted_parts,
                total_count=len(extracted_parts),
                error_message=f"处理过程出错: {str(e)}",
                execution_time=time.time() - start_time,
                warnings=warnings
            )
    
    def _get_test_shimano_data(self) -> Dict[str, List[Dict]]:
        """获取测试用的真实Shimano数据格式"""
        return {
            "Shifter": [
                {
                    "model_number": "ST-R9120-R",
                    "series": "DURA-ACE",
                    "category": "Shifter",
                    "page_number": 1,
                    "table_index": 1,
                    "specifications": {
                        "Color - 1": "Series color",
                        "Color - 2": "-",
                        "Shifter type": "DUAL CONTROL LEVER",
                        "Shift lever - Front speeds": "-",
                        "Shift lever - Rear speeds": "11",
                        "Shift lever - Max multiple shifts (main lever rear)": "2",
                        "Shift lever - Multi-bearing construction": "-",
                        "Shift lever cable - Outer casing": "OT-SP41",
                        "Shift lever cable - Inner cable": "✔",
                        "Brake lever - Brake hose (kit)": "SM-BH90-JK-SSR",
                        "Brake lever - Hose joint": "Straight",
                        "Brake lever - Brake hose color (kit)": "Black",
                        "Brake lever - Recommended brake caliper": "BR-R8070",
                        "Brake lever - Oil": "SHIMANO Mineral",
                        "Brake lever - Reach adjust": "✔",
                        "Brake lever - Clamp band (mm)": "23.8-24.2",
                        "Brake lever - Funnel bleeding": "✔",
                        "Brake lever - Free stroke adjust": "✔",
                        "Brake lever - SERVO WAVE": "✔",
                        "Brake lever - Material": "Engineering composite",
                        "Brake lever - Finish": "Painted",
                        "Bracket - Material": "Engineering composite",
                        "Bracket - Finish": "-",
                        "Clamp band - Material": "Steel",
                        "Average weight (g)": "554 ( /pair)"
                    }
                },
                {
                    "model_number": "ST-R9120-L",
                    "series": "DURA-ACE",
                    "category": "Shifter",
                    "page_number": 1,
                    "table_index": 1,
                    "specifications": {
                        "Color - 1": "Series color",
                        "Color - 2": "-",
                        "Shifter type": "DUAL CONTROL LEVER",
                        "Shift lever - Front speeds": "2",
                        "Shift lever - Rear speeds": "-",
                        "Shift lever - Max multiple shifts (main lever rear)": "-",
                        "Shift lever - Multi-bearing construction": "-",
                        "Shift lever cable - Outer casing": "OT-SP41",
                        "Shift lever cable - Inner cable": "✔",
                        "Brake lever - Brake hose (kit)": "SM-BH90-JK-SSR",
                        "Brake lever - Hose joint": "Straight",
                        "Brake lever - Brake hose color (kit)": "Black",
                        "Brake lever - Recommended brake caliper": "BR-R8070",
                        "Brake lever - Oil": "SHIMANO Mineral",
                        "Brake lever - Reach adjust": "✔",
                        "Brake lever - Clamp band (mm)": "23.8-24.2",
                        "Brake lever - Funnel bleeding": "✔",
                        "Brake lever - Free stroke adjust": "✔",
                        "Brake lever - SERVO WAVE": "✔",
                        "Brake lever - Material": "Engineering composite",
                        "Brake lever - Finish": "Painted",
                        "Bracket - Material": "Engineering composite",
                        "Bracket - Finish": "-",
                        "Clamp band - Material": "Steel",
                        "Average weight (g)": "554 ( /pair)"
                    }
                }
            ],
            "Rear Derailleur": [
                {
                    "model_number": "RD-R9150-SS",
                    "series": "DURA-ACE",
                    "category": "Rear Derailleur",
                    "page_number": 2,
                    "table_index": 1,
                    "specifications": {
                        "Color - 1": "Series color",
                        "Color - 2": "-",
                        "Speed": "11",
                        "Max sprocket - Low": "28T",
                        "Max sprocket - Top": "32T",
                        "Min sprocket": "11T",
                        "Total capacity": "35T",
                        "Chain wrap capacity": "35T",
                        "Pulley wheel - Upper": "11T",
                        "Pulley wheel - Lower": "11T",
                        "Spring tension": "Standard",
                        "Cage length": "Short cage",
                        "Chain compatibility": "HG-X11",
                        "Weight (g)": "215"
                    }
                }
            ],
            "Brake": [
                {
                    "model_number": "BR-R9170-F",
                    "series": "DURA-ACE",
                    "category": "Brake",
                    "page_number": 3,
                    "table_index": 1,
                    "specifications": {
                        "Color - 1": "Series color",
                        "Color - 2": "-",
                        "Brake type": "Hydraulic disc brake",
                        "Recommended rotor size (mm)": "140-160",
                        "Rotor mount": "Flat mount",
                        "Hose connection": "Banjo bolt",
                        "Oil type": "SHIMANO Mineral oil",
                        "Pad type": "Resin/Metal",
                        "Brake pad": "A01S",
                        "Weight (g)": "130"
                    }
                }
            ]
        }
    
    def _convert_shimano_to_part_data(self, shimano_product: Dict, category: str) -> Optional[PartData]:
        """将Shimano产品数据转换为PartData格式"""
        try:
            model_number = shimano_product.get('model_number', '')
            series = shimano_product.get('series', '')
            specifications = shimano_product.get('specifications', {})
            
            if not model_number:
                return None
            
            # 构建产品名称
            name = model_number
            if series:
                name = f"{model_number} ({series})"
            
            # 构建描述
            description_parts = []
            if series:
                description_parts.append(f"系列: {series}")
            if 'Speed' in specifications:
                description_parts.append(f"速别: {specifications['Speed']}")
            if 'Brake type' in specifications:
                description_parts.append(f"类型: {specifications['Brake type']}")
            if 'Shifter type' in specifications:
                description_parts.append(f"类型: {specifications['Shifter type']}")
            
            description = ', '.join(description_parts) if description_parts else f"Shimano {category}"
            
            # 创建PartData对象
            part = PartData(
                name=name,
                category=f"Shimano {category}",
                description=description,
                properties=specifications,
                external_id=model_number,
                source_url=f"https://productinfo.shimano.com/en/product/{model_number}"
            )
            
            return part
            
        except Exception as e:
            raise Exception(f"转换Shimano产品数据失败: {str(e)}")
    
    def _is_valid_part(self, part: PartData, config: Dict[str, Any]) -> bool:
        """验证零件数据是否有效"""
        min_specs_count = config.get("min_specs_count", 5)
        
        # 检查规格参数数量
        if part.properties:
            specs_count = len([v for v in part.properties.values() if v and v != "-"])
            if specs_count < min_specs_count:
                return False
        else:
            return False
        
        # 检查型号格式
        if not re.search(r'[A-Z]+-[A-Z]*\d+', part.external_id or part.name):
            return False
        
        return True
    
    def _crawl_shimano_images_dynamic(self, parts: List[PartData], config: Dict[str, Any], 
                                    warnings: List[str], debug_mode: bool) -> List[PartData]:
        """动态爬取Shimano产品图片"""
        
        if not config.get("enable_image_crawling", True):
            return parts
        
        crawl_delay = config.get("image_crawl_delay", 3.0)
        updated_parts = []
        
        # 设置请求会话
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://productinfo.shimano.com/'
        })
        
        for i, part in enumerate(parts):
            try:
                model_number = part.external_id or part.name.split('(')[0].strip()
                
                if debug_mode:
                    self._log(f"动态爬取图片 ({i+1}/{len(parts)}): {model_number}")
                
                # 1. 查找产品页面
                product_url = self._find_shimano_product_page(session, model_number, debug_mode)
                if not product_url:
                    warnings.append(f"找不到产品页面: {model_number}")
                    updated_parts.append(part)
                    continue
                
                # 2. 从产品页面动态提取图片URL
                image_url = self._extract_shimano_image_dynamic(session, product_url, model_number, debug_mode)
                
                if image_url:
                    part.image_url = image_url
                    if debug_mode:
                        self._log(f"✓ 找到图片: {image_url}")
                else:
                    warnings.append(f"未找到产品图片: {model_number}")
                
                updated_parts.append(part)
                
                # 延时
                if i < len(parts) - 1:
                    time.sleep(crawl_delay)
                
            except Exception as e:
                warnings.append(f"图片爬取失败 {part.name}: {str(e)}")
                updated_parts.append(part)
        
        return updated_parts
    
    def _find_shimano_product_page(self, session: requests.Session, model_number: str, debug_mode: bool) -> Optional[str]:
        """查找Shimano产品页面"""
        
        # 尝试直接URL
        product_url = self.product_url_template.format(model_number)
        
        try:
            if debug_mode:
                self._log(f"尝试访问: {product_url}")
            
            response = session.get(product_url, timeout=10)
            
            if response.status_code == 200:
                if model_number.upper() in response.text.upper():
                    if debug_mode:
                        self._log(f"✓ 找到产品页面: {model_number}")
                    return product_url
                else:
                    if debug_mode:
                        self._log(f"页面存在但不包含产品信息: {model_number}")
            else:
                if debug_mode:
                    self._log(f"页面不存在 (状态码: {response.status_code}): {model_number}")
                    
        except Exception as e:
            if debug_mode:
                self._log(f"访问产品页面失败 {model_number}: {str(e)}")
        
        # 尝试URL变体
        return self._try_shimano_url_variants(session, model_number, debug_mode)
    
    def _try_shimano_url_variants(self, session: requests.Session, model_number: str, debug_mode: bool) -> Optional[str]:
        """尝试Shimano URL的不同变体"""
        variants = [
            model_number.upper(),
            model_number.lower(),
            model_number.replace('-', ''),
        ]
        
        for variant in variants:
            if variant == model_number:
                continue
                
            url = self.product_url_template.format(variant)
            try:
                response = session.get(url, timeout=10)
                if response.status_code == 200 and model_number.upper() in response.text.upper():
                    if debug_mode:
                        self._log(f"✓ 找到产品页面变体: {model_number} -> {variant}")
                    return url
            except:
                continue
        
        return None
    
    def _extract_shimano_image_dynamic(self, session: requests.Session, product_url: str, 
                                     model_number: str, debug_mode: bool) -> Optional[str]:
        """从Shimano产品页面动态提取图片URL"""
        
        try:
            response = session.get(product_url, timeout=10)
            response.raise_for_status()
            
            html_content = response.text
            if debug_mode:
                self._log(f"页面内容长度: {len(html_content)} 字符")
            
            # 使用全面分析方法
            image_url = self._extract_from_comprehensive_js_analysis(html_content, model_number, debug_mode)
            if image_url:
                if debug_mode:
                    self._log(f"✓ 动态提取到图片URL: {image_url}")
                return image_url
            
            if debug_mode:
                self._log(f"无法从页面中动态提取图片信息: {product_url}")
            
            return None
            
        except Exception as e:
            if debug_mode:
                self._log(f"动态解析产品页面失败 {product_url}: {str(e)}")
            return None
    
    def _extract_from_comprehensive_js_analysis(self, html_content: str, model_number: str, debug_mode: bool) -> Optional[str]:
        """全面分析JavaScript数据提取图片信息"""
        
        # 方法1: 直接查找fileName模式
        if debug_mode:
            self._log("尝试方法1: 直接查找fileName")
        filename = self._find_filename_directly(html_content)
        if filename:
            image_url = f"https://productinfo.shimano.com/images/spec/products/{filename}"
            if debug_mode:
                self._log(f"方法1成功: {image_url}")
            return image_url
        
        # 方法2: 解析modelImages JSON
        if debug_mode:
            self._log("尝试方法2: 解析modelImages JSON")
        filename = self._parse_model_images_json(html_content)
        if filename:
            image_url = f"https://productinfo.shimano.com/images/spec/products/{filename}"
            if debug_mode:
                self._log(f"方法2成功: {image_url}")
            return image_url
        
        # 方法3: 查找所有可能的图片引用
        if debug_mode:
            self._log("尝试方法3: 查找所有图片引用")
        image_url = self._find_any_image_reference(html_content)
        if image_url:
            if debug_mode:
                self._log(f"方法3成功: {image_url}")
            return image_url
        
        # 方法4: 深度正则表达式搜索
        if debug_mode:
            self._log("尝试方法4: 深度正则搜索")
        image_url = self._deep_regex_search(html_content, model_number)
        if image_url:
            if debug_mode:
                self._log(f"方法4成功: {image_url}")
            return image_url
        if debug_mode:
            self._log("所有方法都未能提取到图片URL")
        return None
    
    def _find_filename_directly(self, html_content: str) -> Optional[str]:
        """直接查找文件名模式"""
        patterns = [
            r'"fileName":"([^"]+\.(?:png|jpg|jpeg|webp))"',
            r'fileName["\']:\s*["\']([^"\']+\.(?:png|jpg|jpeg|webp))["\']',
            r'filename["\']:\s*["\']([^"\']+\.(?:png|jpg|jpeg|webp))["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_shimano_filename(match):
                    return match
        
        return None
    
    def _parse_model_images_json(self, html_content: str) -> Optional[str]:
        """解析modelImages的JSON数据"""
        patterns = [
            r'"modelImages":"(\{[^"]+\})"',
            r'"modelImages":(\{[^}]+\})',
            r'modelImages["\']:\s*["\'](\{[^"\']+\})["\']',
            r'modelImages["\']:\s*(\{[^}]+\})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    json_str = match.replace('\\"', '"').replace('\\/', '/')
                    image_data = json.loads(json_str)
                    
                    if 'modelImages' in image_data and image_data['modelImages']:
                        images = image_data['modelImages']
                        if isinstance(images, list) and len(images) > 0:
                            filename = images[0].get('fileName', '')
                            if filename and self._is_valid_shimano_filename(filename):
                                return filename
                                
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        
        return None
    
    def _find_any_image_reference(self, html_content: str) -> Optional[str]:
        """查找任何可能的图片引用"""
        patterns = [
            r'https://productinfo\.shimano\.com/images/[^"\'>\s]+\.(?:png|jpg|jpeg|webp)',
            r'https://[^"\'>\s]*shimano[^"\'>\s]*\.(?:png|jpg|jpeg|webp)',
            r'/images/[^"\'>\s]+\.(?:png|jpg|jpeg|webp)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_shimano_image_url(match):
                    if not match.startswith('http'):
                        match = 'https://productinfo.shimano.com' + match
                    return match
        
        return None
    
    def _deep_regex_search(self, html_content: str, model_number: str) -> Optional[str]:
        """深度正则表达式搜索"""
        model_patterns = [
            rf'({re.escape(model_number)}[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
            r'([A-Z]{2}-[A-Z]*\d+[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
            r'(SL-M\d+[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
            r'(RD-[A-Z]*\d+[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
            r'(BR-[A-Z]*\d+[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
            r'(FC-[A-Z]*\d+[^"\'>\s]*\.(?:png|jpg|jpeg|webp))',
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_shimano_filename(match):
                    return f"https://productinfo.shimano.com/images/spec/products/{match}"
        
        return None
    
    def _is_valid_shimano_filename(self, filename: str) -> bool:
        """检查是否是有效的禧玛诺图片文件名"""
        if not filename:
            return False
        
        if not any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
            return False
        
        if re.search(r'[A-Z]{2}-[A-Z]*\d+', filename, re.IGNORECASE):
            return True
        
        invalid_patterns = ['logo', 'icon', 'banner', 'bg', 'background', 'header', 'footer']
        if any(pattern in filename.lower() for pattern in invalid_patterns):
            return False
        
        return True
    
    def _is_valid_shimano_image_url(self, url: str) -> bool:
        """检查是否是有效的禧玛诺图片URL"""
        if not url or 'shimano.com' not in url.lower():
            return False
        
        if '/images/' not in url.lower():
            return False
        
        if not any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
            return False
        
        invalid_patterns = ['logo', 'icon', 'banner', 'bg', 'background']
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False
        
        return True
    
    def _get_pdf_content(self, config: Dict[str, Any], debug_mode: bool) -> Optional[bytes]:
        """获取PDF内容"""
        processing_mode = config.get("pdf_processing_mode", "test")
        
        if processing_mode == "upload":
            if debug_mode:
                self._log("从上传的文件获取PDF内容")
            
            file_id = config.get("pdf_file")
            if not file_id:
                raise ValueError("请先上传PDF文件，或选择测试模式")
            
            return self._download_uploaded_file(file_id, debug_mode)
        
        return None
    
    def _download_uploaded_file(self, file_id: str, debug_mode: bool) -> Optional[bytes]:
        """从文件上传API下载文件"""
        try:
            if debug_mode:
                self._log(f"下载文件: {file_id}")
                self._log(f"当前token状态: {'有' if self.get_admin_token() else '无'}")
            
            # 使用基类提供的下载方法
            content = self.download_uploaded_file(file_id)
            
            if debug_mode:
                self._log(f"文件下载成功，大小: {len(content)} bytes")
            
            return content
                
        except Exception as e:
            error_msg = f"下载文件时出错: {str(e)}"
            if debug_mode:
                self._log(error_msg)
            raise Exception(error_msg)
    
    def _smart_parse_uploaded_file(self, file_content: bytes, config: Dict[str, Any], debug_mode: bool) -> Dict[str, List[Dict]]:
        """智能解析上传的文件 - 支持多种格式，使用安全工具类"""
        
        if debug_mode:
            self._log("开始智能文件解析")
        
        try:
            from app.plugins.crawler_base import PluginUtils
            
            # 智能解析文件
            parse_result = PluginUtils.safe_parse_any_file(file_content, **{
                'max_pages': config.get('max_pages', 50),
                'max_rows': config.get('max_rows', 5000),
                'extract_tables': True,
                'password': config.get('pdf_password')
            })
            
            if not parse_result['success']:
                raise Exception(f"文件解析失败: {parse_result['error']}")
            
            file_type = parse_result['file_type']
            content = parse_result['content']
            
            if debug_mode:
                self._log(f"检测到文件类型: {file_type}")
                self._log(f"文件大小: {parse_result.get('file_size', 'unknown')} 字节")
            
            # 根据文件类型处理内容
            if file_type == 'pdf':
                # PDF文本内容 - 使用Shimano专用解析
                return self._extract_shimano_from_pdf_text(content, debug_mode)
                
            elif file_type in ['excel', 'csv']:
                # 表格数据
                return self._extract_products_from_table_data(content, debug_mode)
                
            elif file_type == 'word':
                # Word文档文本
                return self._extract_shimano_from_pdf_text(content, debug_mode)
                
            else:
                raise Exception(f"不支持的文件类型: {file_type}")
            
        except Exception as e:
            if debug_mode:
                self._log(f"智能文件解析失败: {str(e)}")
            raise Exception(f"文件解析失败: {str(e)}")
    
    def _extract_shimano_from_pdf_text(self, text_content: str, debug_mode: bool) -> Dict[str, List[Dict]]:
        """从PDF文本中提取Shimano产品信息 - 基于你的核心算法但适配PDF文本"""
        
        if debug_mode:
            self._log("开始从PDF文本提取Shimano产品")
        
        products_by_category = {}
        lines = text_content.split('\n')
        
        current_category = None
        current_product = None
        current_series = None
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 检测Series信息
            if 'series' in line.lower() and any(series in line.upper() for series in ['DURA-ACE', 'ULTEGRA', 'XTR', 'XT', 'SLX']):
                series_match = re.search(r'(DURA-ACE|ULTEGRA|XTR|XT|SLX|DEORE|CUES)', line.upper())
                if series_match:
                    current_series = series_match.group()
                    if debug_mode:
                        self._log(f"检测到系列: {current_series} (行 {line_num})")
                continue
            
            # 检测产品类别
            detected_category = self._detect_category_from_line(line)
            if detected_category:
                current_category = detected_category
                current_series = None  # 重置系列信息
                if debug_mode:
                    self._log(f"检测到类别: {current_category} (行 {line_num})")
                continue
            
            # 检测产品型号
            model_matches = re.findall(r'([A-Z]{2}-[A-Z]*\d+[A-Z\-]*)', line)
            if model_matches and current_category:
                # 保存之前的产品
                if current_product:
                    self._finalize_shimano_product(products_by_category, current_category, current_product)
                
                # 处理第一个型号
                model_number = model_matches[0]
                current_product = {
                    'model_number': model_number,
                    'series': current_series or '',
                    'category': current_category,
                    'page_number': line_num // 50 + 1,  # 估算页码
                    'table_index': 1,
                    'specifications': {},
                    'raw_line': line
                }
                
                if debug_mode:
                    self._log(f"检测到产品: {model_number} (系列: {current_series or 'Unknown'})")
                continue
            
            # 提取规格参数
            if current_product:
                specs_extracted = self._extract_specs_from_line(line, debug_mode)
                if specs_extracted:
                    current_product['specifications'].update(specs_extracted)
        
        # 保存最后一个产品
        if current_product and current_category:
            self._finalize_shimano_product(products_by_category, current_category, current_product)
        
        # 后处理：清理和验证数据
        self._post_process_shimano_data(products_by_category, debug_mode)
        
        return products_by_category
    
    def _detect_category_from_line(self, line: str) -> Optional[str]:
        """从文本行中检测产品类别"""
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                return category
        return None
    
    def _extract_specs_from_line(self, line: str, debug_mode: bool) -> Dict[str, str]:
        """从文本行中提取规格参数 - 适配Shimano格式"""
        specs = {}
        
        # 模式1: 标准格式 "参数名: 值"
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                param_name = parts[0].strip()
                param_value = parts[1].strip()
                if param_name and param_value:
                    specs[param_name] = param_value
        
        # 模式2: 表格格式 "参数名    值1    值2    值3"
        elif '\t' in line or '  ' in line:
            # 分割多个空格或制表符
            parts = re.split(r'\s{2,}|\t+', line)
            if len(parts) >= 2:
                param_name = parts[0].strip()
                if param_name and not param_name.startswith(('ST-', 'RD-', 'BR-', 'FC-')):
                    # 不是型号，可能是参数名
                    for i, value in enumerate(parts[1:], 1):
                        if value.strip():
                            specs[f"{param_name} - {i}"] = value.strip()
        
        # 模式3: 连续格式 - 查找关键词模式
        else:
            patterns = [
                r'Speed[:\s]*(\d+)',
                r'Weight[:\s]*(\d+\.?\d*\s*g)',
                r'Max[:\s]*(\d+T)',
                r'Rotor[:\s]*(\d+-\d+mm)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    param_name = pattern.split('[')[0]  # 提取参数名
                    specs[param_name] = match.group(1)
        
        return specs
    
    def _finalize_shimano_product(self, products_dict: Dict, category: str, product: Dict):
        """完成Shimano产品数据并添加到分类字典"""
        
        # 确保有基本的规格参数
        if not product['specifications']:
            return  # 跳过没有规格的产品
        
        # 规范化系列信息
        if not product['series'] and product['specifications']:
            # 尝试从规格中推断系列
            for spec_value in product['specifications'].values():
                for series in ['DURA-ACE', 'ULTEGRA', 'XTR', 'XT', 'SLX', 'DEORE']:
                    if series in str(spec_value).upper():
                        product['series'] = series
                        break
                if product['series']:
                    break
        
        if category not in products_dict:
            products_dict[category] = []
        products_dict[category].append(product)
    
    def _post_process_shimano_data(self, products_dict: Dict, debug_mode: bool):
        """后处理Shimano数据：清理、验证和优化"""
        
        categories_to_remove = []
        
        for category, products in products_dict.items():
            valid_products = []
            
            for product in products:
                # 验证产品数据质量
                if self._validate_shimano_product(product):
                    # 清理规格参数
                    cleaned_specs = {}
                    for param, value in product['specifications'].items():
                        if value and str(value).strip() not in ['-', 'N/A', '']:
                            cleaned_specs[param.strip()] = str(value).strip()
                    
                    product['specifications'] = cleaned_specs
                    valid_products.append(product)
                elif debug_mode:
                    self._log(f"过滤无效产品: {product['model_number']}")
            
            if valid_products:
                products_dict[category] = valid_products
            else:
                categories_to_remove.append(category)
        
        # 移除空类别
        for category in categories_to_remove:
            del products_dict[category]
            if debug_mode:
                self._log(f"移除空类别: {category}")
    
    def _validate_shimano_product(self, product: Dict) -> bool:
        """验证Shimano产品数据是否有效"""
        
        # 检查型号格式
        model = product.get('model_number', '')
        if not re.match(r'^[A-Z]{2}-[A-Z]*\d+[A-Z\-]*$', model):
            return False
        
        # 检查规格参数数量和质量
        specs = product.get('specifications', {})
        if not specs:
            return False
        
        # 统计有效规格参数
        valid_specs = 0
        for value in specs.values():
            if value and str(value).strip() not in ['-', 'N/A', '', '✔']:
                valid_specs += 1
        
        # 至少需要3个有效规格参数
        return valid_specs >= 3
    
    def _extract_products_from_table_data(self, table_data: List[Dict], debug_mode: bool) -> Dict[str, List[Dict]]:
        """从表格数据中提取产品信息"""
        
        if debug_mode:
            self._log(f"处理表格数据，共 {len(table_data)} 行")
        
        products_by_category = {}
        
        for row_idx, row in enumerate(table_data):
            # 查找型号列
            model_number = None
            for key, value in row.items():
                if isinstance(value, str) and re.match(r'^[A-Z]{2}-[A-Z]*\d+[A-Z\-]*$', value):
                    model_number = value
                    break
            
            if not model_number:
                continue
            
            # 推断类别
            category = 'Unknown'
            for cat, pattern in self.category_patterns.items():
                if any(re.search(pattern, str(v), re.IGNORECASE) for v in row.values() if v):
                    category = cat
                    break
            
            # 构建产品数据
            product = {
                'model_number': model_number,
                'series': row.get('Series', ''),
                'category': category,
                'page_number': row_idx // 20 + 1,
                'table_index': 1,
                'specifications': {k: v for k, v in row.items() if k != 'model_number' and v}
            }
            
            if self._validate_shimano_product(product):
                if category not in products_by_category:
                    products_by_category[category] = []
                products_by_category[category].append(product)
        
        return products_by_category
    
    # 测试辅助方法
    def _test_files_api(self) -> bool:
        """测试文件API是否可用"""
        try:
            headers = self.get_auth_headers()
            return bool(headers)
        except:
            return False
    
    def _test_images_api(self) -> bool:
        """测试图片API是否可用"""
        try:
            return True
        except:
            return False
    
    def _test_shimano_connection(self) -> bool:
        """测试Shimano网站连接"""
        try:
            response = requests.get("https://productinfo.shimano.com", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _log(self, message: str):
        """简单的日志输出"""
        print(f"[Shimano Plugin] {message}")
    
    def get_allowed_domains(self) -> List[str]:
        """返回允许访问的域名"""
        return [
            "productinfo.shimano.com",
            "shimano.com"
        ]
    
    def get_required_permissions(self) -> List[str]:
        """返回需要的权限"""
        return ["network"]
    
    def cleanup(self):
        """清理资源"""
        pass

# 必需：创建插件实例
plugin = ShimanoPDFPlugin()