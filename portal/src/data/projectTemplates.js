// portal/src/data/projectTemplates.js (新文件 - 硬编码项目模板)

export const projectTemplates = [
  {
    id: 1,
    name: "Arduino基础入门套件",
    description: "适合初学者的Arduino项目套件，包含基本的电子元件",
    category: "Arduino",
    difficulty: "初级",
    estimated_cost: 150.00,
    estimated_time: "2-3小时",
    image: "/static/templates/arduino-basic.jpg",
    items: [
      {
        id: 1,
        category: "微控制器",
        name: "Arduino开发板",
        description: "项目核心控制器",
        is_required: true,
        quantity: 1,
        estimated_price: 25.00,
        suggested_specs: {
          "电压": "5V",
          "接口": "USB",
          "GPIO数量": "14+"
        },
        notes: "推荐Arduino Uno R3或兼容版本"
      },
      {
        id: 2,
        category: "面包板",
        name: "实验面包板",
        description: "用于搭建电路的实验板",
        is_required: true,
        quantity: 1,
        estimated_price: 8.00,
        suggested_specs: {
          "孔数": "400+",
          "尺寸": "标准半尺寸"
        },
        notes: "建议选择带电源分配线的版本"
      },
      {
        id: 3,
        category: "跳线",
        name: "连接跳线",
        description: "连接电路各部分的导线",
        is_required: true,
        quantity: 1,
        estimated_price: 5.00,
        suggested_specs: {
          "类型": "公对公",
          "长度": "多种规格"
        },
        notes: "建议购买多色跳线套装"
      },
      {
        id: 4,
        category: "LED",
        name: "发光二极管",
        description: "基础指示灯组件",
        is_required: false,
        quantity: 10,
        estimated_price: 3.00,
        suggested_specs: {
          "颜色": "红、绿、蓝",
          "电压": "3.3V",
          "电流": "20mA"
        },
        notes: "多色LED套装更实用"
      },
      {
        id: 5,
        category: "电阻",
        name: "限流电阻",
        description: "保护电路的电阻组件",
        is_required: true,
        quantity: 20,
        estimated_price: 2.00,
        suggested_specs: {
          "阻值": "220Ω-10kΩ",
          "功率": "1/4W",
          "精度": "5%"
        },
        notes: "建议购买电阻包，包含常用阻值"
      },
      {
        id: 6,
        category: "传感器",
        name: "温湿度传感器",
        description: "环境监测传感器",
        is_required: false,
        quantity: 1,
        estimated_price: 12.00,
        suggested_specs: {
          "类型": "DHT22",
          "精度": "±0.5°C",
          "接口": "数字"
        },
        notes: "可选组件，用于进阶项目"
      }
    ]
  },
  {
    id: 2,
    name: "智能家居控制系统",
    description: "构建基本的智能家居控制项目，支持远程控制和自动化",
    category: "IoT",
    difficulty: "中级",
    estimated_cost: 280.00,
    estimated_time: "1-2天",
    image: "/static/templates/smart-home.jpg",
    items: [
      {
        id: 1,
        category: "微控制器",
        name: "WiFi开发板",
        description: "支持无线连接的控制器",
        is_required: true,
        quantity: 1,
        estimated_price: 35.00,
        suggested_specs: {
          "WiFi": "802.11 b/g/n",
          "电压": "3.3V",
          "闪存": "4MB+"
        },
        notes: "推荐ESP32或NodeMCU"
      },
      {
        id: 2,
        category: "继电器",
        name: "继电器模块",
        description: "控制高压电器设备",
        is_required: true,
        quantity: 4,
        estimated_price: 15.00,
        suggested_specs: {
          "电压": "5V",
          "负载": "10A",
          "触点": "常开/常闭"
        },
        notes: "4路继电器模块更方便"
      },
      {
        id: 3,
        category: "传感器",
        name: "人体感应传感器",
        description: "检测人员活动",
        is_required: true,
        quantity: 2,
        estimated_price: 8.00,
        suggested_specs: {
          "类型": "PIR",
          "检测距离": "3-7米",
          "角度": "120°"
        },
        notes: "用于自动照明控制"
      },
      {
        id: 4,
        category: "传感器",
        name: "温湿度传感器",
        description: "环境监测",
        is_required: true,
        quantity: 1,
        estimated_price: 12.00,
        suggested_specs: {
          "类型": "DHT22",
          "精度": "±0.5°C",
          "通信": "数字信号"
        },
        notes: "用于环境自动化控制"
      },
      {
        id: 5,
        category: "显示器",
        name: "OLED显示屏",
        description: "状态显示屏幕",
        is_required: false,
        quantity: 1,
        estimated_price: 18.00,
        suggested_specs: {
          "尺寸": "0.96寸",
          "分辨率": "128x64",
          "接口": "I2C"
        },
        notes: "可选，用于显示系统状态"
      },
      {
        id: 6,
        category: "电源",
        name: "电源适配器",
        description: "系统供电",
        is_required: true,
        quantity: 1,
        estimated_price: 15.00,
        suggested_specs: {
          "输出": "5V 2A",
          "接口": "DC头",
          "稳定性": "高"
        },
        notes: "确保功率充足且稳定"
      }
    ]
  },
  {
    id: 3,
    name: "机器人小车基础版",
    description: "构建一个可遥控的机器人小车，支持避障和循迹功能",
    category: "机器人",
    difficulty: "中级",
    estimated_cost: 320.00,
    estimated_time: "2-3天",
    image: "/static/templates/robot-car.jpg",
    items: [
      {
        id: 1,
        category: "微控制器",
        name: "Arduino开发板",
        description: "机器人控制核心",
        is_required: true,
        quantity: 1,
        estimated_price: 25.00,
        suggested_specs: {
          "型号": "Arduino Uno R3",
          "GPIO": "14个数字IO",
          "PWM": "6个PWM输出"
        },
        notes: "确保有足够的PWM输出控制电机"
      },
      {
        id: 2,
        category: "底盘",
        name: "机器人底盘",
        description: "小车的机械结构框架",
        is_required: true,
        quantity: 1,
        estimated_price: 45.00,
        suggested_specs: {
          "材质": "亚克力或铝合金",
          "轮子": "4轮驱动",
          "尺寸": "20x15cm"
        },
        notes: "选择带电机安装孔的底盘"
      },
      {
        id: 3,
        category: "电机",
        name: "减速电机",
        description: "驱动轮子的动力源",
        is_required: true,
        quantity: 4,
        estimated_price: 60.00,
        suggested_specs: {
          "电压": "6V",
          "转速": "200RPM",
          "减速比": "1:48"
        },
        notes: "建议购买带编码器的电机"
      },
      {
        id: 4,
        category: "驱动器",
        name: "电机驱动板",
        description: "控制电机转速和方向",
        is_required: true,
        quantity: 1,
        estimated_price: 25.00,
        suggested_specs: {
          "通道": "4路",
          "电流": "1.2A/通道",
          "控制": "PWM"
        },
        notes: "L298N驱动板是经典选择"
      },
      {
        id: 5,
        category: "传感器",
        name: "超声波传感器",
        description: "测距避障传感器",
        is_required: true,
        quantity: 1,
        estimated_price: 8.00,
        suggested_specs: {
          "型号": "HC-SR04",
          "距离": "2-400cm",
          "精度": "3mm"
        },
        notes: "用于实现避障功能"
      },
      {
        id: 6,
        category: "传感器",
        name: "循迹传感器",
        description: "黑白线检测传感器",
        is_required: false,
        quantity: 3,
        estimated_price: 12.00,
        suggested_specs: {
          "类型": "红外反射",
          "检测距离": "1-3cm",
          "输出": "数字信号"
        },
        notes: "可选，用于循迹功能"
      },
      {
        id: 7,
        category: "电源",
        name: "锂电池组",
        description: "机器人供电电池",
        is_required: true,
        quantity: 1,
        estimated_price: 35.00,
        suggested_specs: {
          "电压": "7.4V",
          "容量": "2200mAh",
          "类型": "18650锂电池"
        },
        notes: "包含充电器和保护板"
      },
      {
        id: 8,
        category: "通信",
        name: "蓝牙模块",
        description: "无线通信控制",
        is_required: false,
        quantity: 1,
        estimated_price: 15.00,
        suggested_specs: {
          "版本": "HC-05",
          "距离": "10米",
          "波特率": "9600"
        },
        notes: "可选，用于手机遥控"
      }
    ]
  },
  {
    id: 4,
    name: "环境监测站",
    description: "构建一个多功能环境监测系统，监控温湿度、空气质量、光照等",
    category: "环境监测",
    difficulty: "高级",
    estimated_cost: 450.00,
    estimated_time: "3-5天",
    image: "/static/templates/environment-monitor.jpg",
    items: [
      {
        id: 1,
        category: "微控制器",
        name: "ESP32开发板",
        description: "支持WiFi和蓝牙的高性能控制器",
        is_required: true,
        quantity: 1,
        estimated_price: 35.00,
        suggested_specs: {
          "CPU": "双核240MHz",
          "WiFi": "802.11 b/g/n",
          "蓝牙": "4.2",
          "GPIO": "30个"
        },
        notes: "强烈推荐ESP32-DevKitC"
      },
      {
        id: 2,
        category: "传感器",
        name: "温湿度传感器",
        description: "高精度温湿度检测",
        is_required: true,
        quantity: 1,
        estimated_price: 18.00,
        suggested_specs: {
          "型号": "SHT30",
          "精度": "±0.2°C, ±2%RH",
          "接口": "I2C"
        },
        notes: "比DHT22精度更高"
      },
      {
        id: 3,
        category: "传感器",
        name: "空气质量传感器",
        description: "检测PM2.5和空气污染",
        is_required: true,
        quantity: 1,
        estimated_price: 85.00,
        suggested_specs: {
          "型号": "PMS7003",
          "检测": "PM1.0/2.5/10",
          "接口": "UART"
        },
        notes: "专业级空气质量传感器"
      },
      {
        id: 4,
        category: "传感器",
        name: "光照传感器",
        description: "环境光强度检测",
        is_required: true,
        quantity: 1,
        estimated_price: 8.00,
        suggested_specs: {
          "型号": "BH1750",
          "范围": "1-65535 lux",
          "接口": "I2C"
        },
        notes: "用于监测光照强度"
      },
      {
        id: 5,
        category: "传感器",
        name: "气压传感器",
        description: "大气压力和海拔检测",
        is_required: false,
        quantity: 1,
        estimated_price: 12.00,
        suggested_specs: {
          "型号": "BMP280",
          "精度": "±1hPa",
          "接口": "I2C/SPI"
        },
        notes: "可选，用于气象监测"
      },
      {
        id: 6,
        category: "显示器",
        name: "彩色TFT屏幕",
        description: "实时数据显示",
        is_required: true,
        quantity: 1,
        estimated_price: 25.00,
        suggested_specs: {
          "尺寸": "2.4寸",
          "分辨率": "240x320",
          "接口": "SPI",
          "触摸": "电阻触摸"
        },
        notes: "用于本地数据显示和操作"
      },
      {
        id: 7,
        category: "存储",
        name: "SD卡模块",
        description: "数据存储模块",
        is_required: true,
        quantity: 1,
        estimated_price: 5.00,
        suggested_specs: {
          "接口": "SPI",
          "支持": "SDHC",
          "容量": "32GB以下"
        },
        notes: "用于本地数据备份"
      },
      {
        id: 8,
        category: "电源",
        name: "太阳能充电系统",
        description: "可持续供电系统",
        is_required: false,
        quantity: 1,
        estimated_price: 80.00,
        suggested_specs: {
          "功率": "5W",
          "电压": "5V",
          "电池": "18650锂电池"
        },
        notes: "可选，用于户外长期监测"
      },
      {
        id: 9,
        category: "外壳",
        name: "防水外壳",
        description: "保护电路的外壳",
        is_required: true,
        quantity: 1,
        estimated_price: 25.00,
        suggested_specs: {
          "防护等级": "IP65",
          "材质": "ABS工程塑料",
          "透明窗": "显示屏窗口"
        },
        notes: "户外使用必需"
      }
    ]
  }
]

// 根据分类获取模板
export function getTemplatesByCategory(category) {
  if (!category) return projectTemplates
  return projectTemplates.filter(template => template.category === category)
}

// 根据难度获取模板
export function getTemplatesByDifficulty(difficulty) {
  if (!difficulty) return projectTemplates
  return projectTemplates.filter(template => template.difficulty === difficulty)
}

// 获取所有分类
export function getAllCategories() {
  const categories = projectTemplates.map(template => template.category)
  return [...new Set(categories)].sort()
}

// 获取所有难度等级
export function getAllDifficulties() {
  const difficulties = projectTemplates.map(template => template.difficulty)
  return [...new Set(difficulties)].sort()
}

// 根据ID获取模板
export function getTemplateById(id) {
  return projectTemplates.find(template => template.id === parseInt(id))
}