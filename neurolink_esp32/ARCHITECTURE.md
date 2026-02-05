# Neurolink ESP32 系统结构设计文档

## 版本信息
- 版本: 1.0
- 日期: 2026-02-05
- 状态: 第二层设计完成

## 系统概述
Neurolink 是一款基于 ESP32-S3 的战术指控终端系统，采用四层子系统架构。

---

## 第一层：四大子系统

### 1. 硬件子系统 (Hardware Subsystem)
负责所有物理设备与外设的管理

**第二层组件（6个）：**
- **防护结构** (Protection Structure)
  - 用途：机械防护、EMI/RFI防护等
  - 职责：防护状态监测

- **电源管理系统** (Power Management System)
  - 用途：电池/电源管理、电压调理
  - 职责：功耗控制、供电监测

- **人机交互单元** (HMI Unit)
  - 用途：按键、显示屏、LED、蜂鸣器等
  - 职责：用户输入采集、反馈输出

- **通信模块** (Communication Module)
  - 用途：Wi-Fi、蓝牙、LoRa 等通信硬件
  - 职责：通信芯片初始化与状态管理

- **传感器套件** (Sensor Suite)
  - 用途：温度、湿度、加速度、GPS 等多种传感器
  - 职责：传感器驱动、数据采集

- **核心处理单元** (Core Processing Unit)
  - 用途：ESP32-S3 MCU 本身
  - 职责：CPU状态监测、资源管理

---

### 2. 软件子系统 (Software Subsystem)
实现应用逻辑与系统框架

**第二层分层（4层）：**

- **操作系统层** (OS Layer)
  - 用途：基础的任务调度、内存管理、中断处理
  - 职责：提供OS级别的原语

- **安全框架** (Security Framework)
  - 用途：身份验证、授权、加密、防护
  - 职责：安全策略执行

- **中间件层** (Middleware Layer)
  - 用途：日志系统、消息总线、配置管理
  - 职责：各子系统之间的通信与协调

- **应用软件层** (Application Layer)
  - 用途：业务逻辑、状态机、指挥控制应用
  - 职责：具体功能实现

---

### 3. 保障子系统 (Support Subsystem)
提供系统的后勤、维护和培训支持

**第二层组件（3个）：**

- **后勤系统** (Logistics System)
  - 用途：物资库存、补给管理、配置备份
  - 职责：资源跟踪与管理

- **维护系统** (Maintenance System)
  - 用途：自诊断、故障检测、修复工具
  - 职责：系统健康检查与维护

- **训练系统** (Training System)
  - 用途：模式识别培训、演习模式、操作指南
  - 职责：培训数据管理与模拟环境

---

### 4. 网络子系统 (Network Subsystem)
管理网络通信与数据交换

**第二层组件（3个）：**

- **通信协议栈** (Protocol Stack)
  - 用途：TCP/IP、LoRaWAN、蓝牙等协议实现
  - 职责：协议处理与报文转发

- **网络管理** (Network Management)
  - 用途：连接管理、QoS、带宽控制
  - 职责：网络状态监控与优化

- **数据分发服务** (Data Distribution Service)
  - 用途：发布-订阅、消息路由、负载均衡
  - 职责：数据在各子系统间的分发

---

## 代码结构树

```
src/
└── main.cpp (主程序入口，调用四大子系统)
└── subsystems/
    ├── hardware/
    │   ├── hardware_subsystem.h/.cpp (硬件子系统主类)
    │   ├── protection_structure/
    │   │   ├── protection_structure.h/.cpp
    │   ├── power_management/
    │   │   ├── power_management.h/.cpp
    │   ├── hmi_unit/
    │   │   ├── hmi_unit.h/.cpp
    │   ├── communication_module/
    │   │   ├── communication_module.h/.cpp
    │   ├── sensor_suite/
    │   │   ├── sensor_suite.h/.cpp
    │   ├── core_processing_unit/
    │   │   ├── core_processing_unit.h/.cpp
    │   └── README.md
    │
    ├── software/
    │   ├── software_subsystem.h/.cpp (软件子系统主类)
    │   ├── os_layer/
    │   │   ├── os_layer.h/.cpp
    │   ├── security_framework/
    │   │   ├── security_framework.h/.cpp
    │   ├── middleware/
    │   │   ├── middleware.h/.cpp
    │   ├── app_layer/
    │   │   ├── app_layer.h/.cpp
    │   └── README.md
    │
    ├── support/
    │   ├── support_subsystem.h/.cpp (保障子系统主类)
    │   ├── logistics_system/
    │   │   ├── logistics_system.h/.cpp
    │   ├── maintenance_system/
    │   │   ├── maintenance_system.h/.cpp
    │   ├── training_system/
    │   │   ├── training_system.h/.cpp
    │   └── README.md
    │
    └── network/
        ├── network_subsystem.h/.cpp (网络子系统主类)
        ├── protocol_stack/
        │   ├── protocol_stack.h/.cpp
        ├── network_management/
        │   ├── network_management.h/.cpp
        ├── data_distribution/
        │   ├── data_distribution.h/.cpp
        └── README.md
```

---

## 调用顺序

### 启动阶段 (begin())
1. HardwareSubsystem::begin()
   - protection_structure → power_management → hmi_unit → communication_module → sensor_suite → cpu
2. SoftwareSubsystem::begin()
   - os_layer → security_framework → middleware → app_layer
3. SupportSubsystem::begin()
   - logistics → maintenance → training
4. NetworkSubsystem::begin()
   - protocol_stack → network_management → data_distribution

### 运行阶段 (tick())
每个子系统及其下层组件的 tick() 方法被周期性调用

---

## 技术栈

- **开发板**: ESP32-S3 DevKitC-1
- **开发框架**: Arduino (PlatformIO)
- **编程语言**: C++11/14
- **命名空间结构**: neurolink::{subsystem}::{component}

---

## 下一步计划（第三层及以下）

- [ ] 硬件组件的具体传感器驱动（I2C/SPI接口）
- [ ] 应用层的具体指挥控制逻辑
- [ ] 安全框架的加密与认证实现
- [ ] 网络协议的具体实现（Wi-Fi/BLE）
- [ ] 保障系统的故障诊断与恢复机制
