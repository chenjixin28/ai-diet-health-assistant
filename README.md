# AI 饮食健康助手

一个基于 AI 的饮食健康管理应用，包含食物识别、营养分析、用餐记录等功能。

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 本地开发

#### 1. 克隆项目

```bash
git clone <你的仓库地址>
cd ai-diet-health-assistant
```

#### 2. 后端设置

```bash
cd backend

# 创建 .env 文件（参考 .env.example）
cp .env.example .env
# 编辑 .env，填入你的 MySQL 配置

# 安装依赖
pip install -r requirements.txt

# 启动后端
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 项目结构

```
ai-diet-health-assistant/
├── backend/              # 后端（FastAPI + Python）
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 模式
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   └── requirements.txt
├── frontend/            # 前端（React + TypeScript + Vite）
│   ├── src/
│   │   ├── api/        # API 调用
│   │   ├── components/ # 组件
│   │   ├── pages/      # 页面
│   │   └── stores/     # 状态管理
│   └── package.json
└── food_training/      # 食物识别训练相关
```

## 协作开发指南

### 1. 开发流程

```bash
# 创建新分支
git checkout -b feature/your-feature-name

# 开发并提交
git add .
git commit -m "feat: 添加功能描述"

# 推送到远程
git push origin feature/your-feature-name

# 提交 Pull Request
```

### 2. 提交规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 3. 分支策略

- `main` 主分支（稳定版）
- `develop` 开发分支
- `feature/*` 功能分支
- `fix/*` 修复分支

## 配置说明

### 环境变量

后端 `.env` 文件示例：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_diet_health

SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

DEEPSEEK_API_KEY=your-deepseek-api-key
YOLO_MODEL_PATH=models/yolov8_food.pt
```

## 许可证

MIT
