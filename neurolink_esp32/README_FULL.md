# Neurolink ESP32 Tactical Command Terminal

## 项目简介
Neurolink 是一款基于 ESP32-S3 的战术指控终端系统设计项目。采用模块化四层子系统架构，支持硬件、软件、保障和网络的完整集成。

## 系统架构（第二层设计）

```
┌─────────────────────────────────────────────┐
│     Main Application (main.cpp)              │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    │                 │          │          │
    ▼                 ▼          ▼          ▼
┌─────────┐   ┌──────────┐ ┌─────────┐ ┌───────┐
│Hardware │   │Software  │ │Support  │ │Network│
│Subsystem│   │Subsystem │ │Subsystem│ │System │
└────┬────┘   └─────┬────┘ └────┬────┘ └───┬───┘
     │              │           │          │
   6个             4层         3个         3个
   组件            分层        组件        组件
```

### 四大子系统

1. **硬件子系统** - 6个组件
   - 防护结构
   - 电源管理系统
   - 人机交互单元
   - 通信模块
   - 传感器套件
   - 核心处理单元

2. **软件子系统** - 4层分层
   - 操作系统层
   - 安全框架
   - 中间件层
   - 应用软件层

3. **保障子系统** - 3个组件
   - 后勤系统
   - 维护系统
   - 训练系统

4. **网络子系统** - 3个组件
   - 通信协议栈
   - 网络管理
   - 数据分发服务

## 项目结构

```
neurolink_esp32/
├── src/
│   ├── main.cpp
│   └── subsystems/
│       ├── hardware/
│       ├── software/
│       ├── support/
│       └── network/
├── platformio.ini
├── README.md
├── ARCHITECTURE.md
└── .gitignore
```

## 快速开始

### 环境要求
- PlatformIO CLI / VSCode PlatformIO 插件
- ESP32-S3 开发板
- USB 数据线

### 编译与上传

```bash
# 编译
pio run

# 上传到开发板
pio run -t upload

# 打开串口监视器
pio device monitor
```

## 详细架构

请参考 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统第二层设计的完整细节。

## 许可证

MIT License

## 贡献者

Neurolink Development Team
