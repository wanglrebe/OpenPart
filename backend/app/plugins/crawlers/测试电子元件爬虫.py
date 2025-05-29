# backend/app/plugins/crawlers/test_electronics_plugin.py
"""
测试用电子元件插件

这是一个用于测试插件系统的示例插件，模拟从电子元件网站爬取数据。
可以直接在管理后台上传此文件进行测试。
"""

import time
import random
from typing import Dict, Any, List
from app.plugins.crawler_base import (
    BaseCrawlerPlugin, PluginInfo, ConfigField, 
    CrawlResult, TestResult, PartData, DataSourceType,
    PluginUtils
)

class TestElectronicsPlugin(BaseCrawlerPlugin):
    """测试电子元件插件"""
    
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="测试电子元件爬虫",
            version="1.0.0",
            description="用于测试的电子元件数据爬虫，模拟从电商网站获取零件信息",
            author="OpenPart Team",
            data_source="测试电子商城",
            data_source_type=DataSourceType.ECOMMERCE,
            homepage="https://test-electronics.com",
            rate_limit=1,
            batch_size=20
        )
    
    @property
    def config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="api_base_url",
                label="API基础地址",
                type="url",
                required=True,
                default="https://api.test-electronics.com",
                help_text="测试电商API的基础地址"
            ),
            ConfigField(
                name="api_key",
                label="API密钥",
                type="password",
                required=False,
                placeholder="可选，某些接口需要",
                help_text="如果网站需要API密钥请填写"
            ),
            ConfigField(
                name="category_filter",
                label="零件类别",
                type="select",
                required=False,
                default="all",
                options=[
                    {"value": "all", "label": "所有类别"},
                    {"value": "resistor", "label": "电阻器"},
                    {"value": "capacitor", "label": "电容器"},
                    {"value": "inductor", "label": "电感器"},
                    {"value": "diode", "label": "二极管"},
                    {"value": "transistor", "label": "三极管"}
                ],
                help_text="选择要爬取的零件类别"
            ),
            ConfigField(
                name="max_price",
                label="最高价格(元)",
                type="number",
                required=False,
                validation={"min": 0, "max": 1000},
                help_text="只获取价格低于此值的零件"
            ),
            ConfigField(
                name="include_images",
                label="包含图片",
                type="checkbox",
                default=True,
                help_text="是否获取零件的图片URL"
            ),
            ConfigField(
                name="request_delay",
                label="请求延迟(秒)",
                type="number",
                default=2,
                validation={"min": 1, "max": 10},
                help_text="两次请求之间的延迟时间"
            ),
            ConfigField(
                name="search_keywords",
                label="搜索关键词",
                type="textarea",
                required=False,
                placeholder="每行一个关键词\n例如：\n电阻\n电容\n二极管",
                help_text="每行输入一个搜索关键词，留空则按类别获取"
            )
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        
        # 检查必填字段
        if not config.get("api_base_url"):
            raise ValueError("API基础地址不能为空")
        
        # 验证URL格式
        if not PluginUtils.validate_url(config["api_base_url"]):
            raise ValueError("API基础地址格式不正确")
        
        # 验证价格范围
        max_price = config.get("max_price")
        if max_price is not None and (max_price < 0 or max_price > 1000):
            raise ValueError("最高价格应在0-1000元之间")
        
        # 验证延迟时间
        delay = config.get("request_delay", 2)
        if delay < 1 or delay > 10:
            raise ValueError("请求延迟应在1-10秒之间")
        
        return True
    
    def test_connection(self, config: Dict[str, Any]) -> TestResult:
        """测试连接"""
        
        try:
            start_time = time.time()
            
            # 模拟连接测试
            api_url = config.get("api_base_url", "")
            
            # 模拟网络延迟
            time.sleep(random.uniform(0.5, 2.0))
            
            response_time = time.time() - start_time
            
            # 模拟不同的测试结果
            success_rate = 0.9  # 90% 成功率
            
            if random.random() < success_rate:
                return TestResult(
                    success=True,
                    message=f"连接成功！服务器响应正常",
                    response_time=round(response_time, 3),
                    sample_data={
                        "server": "test-electronics-api",
                        "version": "v2.1",
                        "status": "online",
                        "endpoints": ["products", "categories", "search"]
                    }
                )
            else:
                return TestResult(
                    success=False,
                    message="连接超时，请检查网络或服务器状态"
                )
        
        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接测试失败: {str(e)}"
            )
    
    def crawl(self, config: Dict[str, Any], **kwargs) -> CrawlResult:
        """执行数据爬取"""
        
        start_time = time.time()
        crawled_data = []
        warnings = []
        
        try:
            # 获取参数
            page_token = kwargs.get("page_token", "1")
            limit = kwargs.get("limit", config.get("batch_size", 20))
            
            # 模拟数据爬取
            page_num = int(page_token) if page_token.isdigit() else 1
            category = config.get("category_filter", "all")
            max_price = config.get("max_price")
            include_images = config.get("include_images", True)
            delay = config.get("request_delay", 2)
            
            # 添加请求延迟
            time.sleep(delay)
            
            # 生成模拟数据
            sample_parts = self._generate_sample_data(category, limit, max_price, include_images)
            
            for i, part_data in enumerate(sample_parts):
                try:
                    # 模拟一些随机错误
                    if random.random() < 0.05:  # 5% 错误率
                        warnings.append(f"零件 {part_data['name']} 数据不完整，已跳过部分字段")
                        continue
                    
                    # 创建零件数据
                    crawled_part = PartData(
                        name=part_data["name"],
                        category=part_data["category"],
                        description=part_data["description"],
                        properties=part_data["properties"],
                        image_url=part_data.get("image_url"),
                        source_url=part_data["source_url"],
                        external_id=part_data["id"],
                        price=part_data.get("price"),
                        availability=part_data["availability"]
                    )
                    
                    crawled_data.append(crawled_part)
                    
                except Exception as e:
                    warnings.append(f"处理零件数据时出错: {str(e)}")
                    continue
            
            execution_time = time.time() - start_time
            
            # 计算下一页标识
            next_page = None
            if len(crawled_data) >= limit and page_num < 5:  # 模拟最多5页
                next_page = str(page_num + 1)
            
            return CrawlResult(
                success=True,
                data=crawled_data,
                total_count=len(crawled_data),
                execution_time=round(execution_time, 3),
                warnings=warnings,
                next_page_token=next_page
            )
            
        except Exception as e:
            return CrawlResult(
                success=False,
                data=crawled_data,
                total_count=len(crawled_data),
                error_message=f"爬取过程出错: {str(e)}",
                execution_time=time.time() - start_time,
                warnings=warnings
            )
    
    def _generate_sample_data(self, category: str, limit: int, max_price: float, include_images: bool) -> List[Dict]:
        """生成模拟数据"""
        
        # 定义不同类别的零件模板
        part_templates = {
            "resistor": {
                "names": ["碳膜电阻", "金属膜电阻", "精密电阻", "功率电阻", "可变电阻"],
                "properties": {
                    "阻值": ["1Ω", "10Ω", "100Ω", "1kΩ", "10kΩ", "100kΩ", "1MΩ"],
                    "功率": ["0.125W", "0.25W", "0.5W", "1W", "2W", "5W"],
                    "精度": ["±1%", "±5%", "±10%"],
                    "温度系数": ["±50ppm/°C", "±100ppm/°C", "±200ppm/°C"]
                }
            },
            "capacitor": {
                "names": ["电解电容", "陶瓷电容", "薄膜电容", "钽电容", "超级电容"],
                "properties": {
                    "容量": ["1pF", "10pF", "100pF", "1nF", "10nF", "100nF", "1μF", "10μF", "100μF", "1mF"],
                    "电压": ["6.3V", "10V", "16V", "25V", "35V", "50V", "100V", "200V", "400V"],
                    "类型": ["NPO", "X7R", "Y5V", "电解", "薄膜"],
                    "精度": ["±1%", "±5%", "±10%", "±20%"]
                }
            },
            "inductor": {
                "names": ["功率电感", "贴片电感", "磁环电感", "色环电感", "屏蔽电感"],
                "properties": {
                    "电感量": ["1μH", "10μH", "100μH", "1mH", "10mH", "100mH"],
                    "电流": ["0.5A", "1A", "2A", "3A", "5A", "10A"],
                    "DCR": ["0.1Ω", "0.5Ω", "1Ω", "2Ω", "5Ω"],
                    "封装": ["0603", "0805", "1206", "1210", "直插"]
                }
            },
            "diode": {
                "names": ["整流二极管", "稳压二极管", "发光二极管", "肖特基二极管", "快恢复二极管"],
                "properties": {
                    "正向电流": ["100mA", "500mA", "1A", "3A", "5A", "10A"],
                    "反向电压": ["50V", "100V", "200V", "400V", "600V", "1000V"],
                    "正向压降": ["0.3V", "0.7V", "1.2V", "2.0V", "3.3V"],
                    "封装": ["DO-35", "DO-41", "SMA", "SMB", "TO-220"]
                }
            },
            "transistor": {
                "names": ["小信号三极管", "功率三极管", "达林顿管", "场效应管", "IGBT"],
                "properties": {
                    "类型": ["NPN", "PNP", "N-MOS", "P-MOS"],
                    "集电极电流": ["100mA", "500mA", "1A", "2A", "5A", "10A"],
                    "集射极电压": ["20V", "40V", "60V", "80V", "100V", "200V"],
                    "功率": ["0.5W", "1W", "2W", "5W", "10W", "25W"],
                    "封装": ["TO-92", "TO-220", "SOT-23", "SOT-89", "TO-263"]
                }
            }
        }
        
        sample_data = []
        categories = [category] if category != "all" else list(part_templates.keys())
        
        for i in range(limit):
            # 随机选择类别
            selected_category = random.choice(categories)
            template = part_templates[selected_category]
            
            # 生成零件数据
            part_name = random.choice(template["names"])
            part_id = f"{selected_category}_{random.randint(1000, 9999)}"
            
            # 生成属性
            properties = {}
            for prop_name, prop_values in template["properties"].items():
                if random.random() < 0.8:  # 80% 概率有这个属性
                    properties[prop_name] = random.choice(prop_values)
            
            # 生成价格
            base_price = random.uniform(0.1, 50.0)
            if max_price and base_price > max_price:
                base_price = random.uniform(0.1, max_price)
            
            # 生成图片URL
            image_url = None
            if include_images and random.random() < 0.7:  # 70% 概率有图片
                image_url = f"https://img.test-electronics.com/{selected_category}/{part_id}.jpg"
            
            part_data = {
                "id": part_id,
                "name": f"{part_name} {random.choice(list(properties.values()))}",
                "category": self._get_category_name(selected_category),
                "description": f"高质量{part_name}，适用于各种电子项目",
                "properties": properties,
                "price": round(base_price, 2),
                "availability": random.choice(["现货", "有货", "预订", "缺货"]),
                "source_url": f"https://test-electronics.com/product/{part_id}",
                "image_url": image_url
            }
            
            sample_data.append(part_data)
        
        return sample_data
    
    def _get_category_name(self, category_key: str) -> str:
        """获取类别中文名称"""
        category_names = {
            "resistor": "电阻器",
            "capacitor": "电容器", 
            "inductor": "电感器",
            "diode": "二极管",
            "transistor": "三极管"
        }
        return category_names.get(category_key, category_key)
    
    def get_allowed_domains(self) -> List[str]:
        """返回允许访问的域名"""
        return [
            "test-electronics.com",
            "api.test-electronics.com",
            "img.test-electronics.com"
        ]
    
    def get_required_permissions(self) -> List[str]:
        """返回需要的权限"""
        return ["network"]
    
    def cleanup(self):
        """清理资源"""
        # 这里可以释放资源，关闭连接等
        pass

# 插件实例 - 系统会自动加载
plugin = TestElectronicsPlugin()

# 插件元数据
__plugin_name__ = "test_electronics"
__plugin_version__ = "1.0.0"
__plugin_author__ = "OpenPart Team"