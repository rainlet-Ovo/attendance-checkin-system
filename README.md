# 智能考勤打卡系统 (Smart Attendance Check-in System)

一个基于 **NFC 刷卡 + 人脸识别 + ESP32 硬件** 的智能考勤打卡系统，适用于企业、学校等场景的日常考勤管理。

> 🎯 本项目为个人课程设计作品，融合了前端开发、后端服务与物联网硬件编程。

---

## 技术栈

### 前端 (client/)
| 技术 | 说明 |
|------|------|
| **Nuxt 3** | Vue 3 全栈框架（SSR / SPA） |
| **Vue 3** | Composition API + `<script setup>` |
| **Element Plus** | 企业级 UI 组件库 |
| **Vue Router** | 客户端路由 |
| **Axios** | HTTP 请求封装 |
| **TypeScript** | 类型安全开发 |

### 后端 (server/)
| 技术 | 说明 |
|------|------|
| **Express** | Node.js Web 框架，RESTful API |
| **MySQL2** | MySQL 数据库驱动（连接池） |
| **JWT (jsonwebtoken)** | 用户身份认证 |
| **bcrypt** | 密码加密存储 |
| **CORS** | 跨域资源共享 |
| **Dotenv** | 环境变量管理 |

### 硬件与物联网 (esp32/)
| 技术 | 说明 |
|------|------|
| **ESP32** | 微控制器，连接 NFC 读卡器 |
| **Python (detect.py / face_operate.py)** | 人脸检测与识别 |
| **NFC** | 非接触式刷卡打卡 |
| **摄像头** | 实时人脸采集与比对 |

---

## 项目结构

```
attendance-checkin-system/
├── client/                    # 前端 (Nuxt 3)
│   ├── app/
│   │   ├── app.vue           # 根组件
│   │   └── pages/            # 页面
│   │       ├── index.vue     # 首页 / 登录
│   │       └── dashboard/
│   │           └── index.vue # 考勤仪表盘
│   ├── public/               # 静态资源
│   ├── nuxt.config.ts        # Nuxt 配置
│   ├── package.json           # 依赖管理
│   └── tsconfig.json         # TypeScript 配置
│
├── server/                    # 后端 (Express)
│   ├── app.js                # 服务入口与路由
│   ├── db.js                 # MySQL 数据库连接池
│   └── .env.example           # 环境变量模板
│
├── esp32/                     # 物联网硬件代码
│   ├── 烧录到esp32的代码.txt   # ESP32 NFC 读卡固件
│   ├── detect.py             # 人脸检测脚本
│   └── face_operate.py       # 人脸操作（注册/识别）
│
└── README.md
```

---

## 快速启动

### 前置要求

- **Node.js** >= 20.x
- **MySQL** >= 8.0
- **Python** 3.x（人脸识别模块）
- **ESP32** 开发板（可选，仅硬件打卡需要）

### 1️⃣ 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/attendance-checkin-system.git
cd attendance-checkin-system
```

### 2️⃣ 启动后端服务

```bash
cd server

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库配置

# 创建数据库
mysql -u root -p -e "CREATE DATABASE attendanceManagementSystem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 启动服务
node app.js
```

后端默认运行在 `http://localhost:8080`。

### 3️⃣ 启动前端

```bash
cd client

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

前端默认运行在 `http://localhost:3000`。

### 4️⃣ 配置 ESP32 硬件（可选）

将 `esp32/` 目录下的代码烧录到 ESP32 开发板，NFC 读卡器连接后可实现刷卡打卡。

### 5️⃣ 人脸识别（可选）

```bash
cd esp32
pip install opencv-python face_recognition
python detect.py     # 启动人脸检测
python face_operate.py  # 人脸注册/识别操作
```

---

## 功能模块

| 模块 | 说明 |
|------|------|
| 🎴 **NFC 刷卡打卡** | ESP32 + NFC 读卡器实时检测刷卡事件 |
| 👤 **人脸识别打卡** | 基于 OpenCV 的人脸检测与识别 |
| 📊 **考勤仪表盘** | 实时查看打卡记录、出勤统计 |
| 📋 **考勤记录管理** | 打卡记录的增删改查与导出 |
| 🔐 **用户认证** | JWT 登录 / 注册 / 权限管理 |
| 📱 **响应式设计** | 适配桌面与移动端 |

---

## 考勤流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  ESP32   │───>│  后端    │───>│  前端    │
│ NFC 刷卡  │    │ Express  │    │ Nuxt 3  │
│ 人脸识别  │    │  MySQL   │    │ 仪表盘   │
└──────────┘    └──────────┘    └──────────┘
```

1. **NFC 刷卡**：员工刷卡 → ESP32 读取卡号 → 发送至后端
2. **人脸识别**：摄像头采集 → Python 识别 → 比对数据库
3. **数据存储**：后端验证身份 → 写入打卡记录到 MySQL
4. **实时展示**：前端轮询 / WebSocket 推送 → 仪表盘刷新

---

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login` | 用户登录 |
| POST | `/api/register` | 用户注册 |
| GET  | `/api/attendance` | 获取打卡记录 |
| POST | `/api/attendance/card` | NFC 刷卡打卡 |
| POST | `/api/attendance/face` | 人脸识别打卡 |
| GET  | `/api/attendance/stats` | 出勤统计数据 |

---

## License

This project is for educational/demonstration purposes.
