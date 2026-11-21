# 橙心售后 · 多角色售后工单与 Agent 系统

课程实践项目：面向电商售后场景的三端协同系统。

消费者提交售后申请后，由三个 Agent 依次完成分类、订单数据检索和回复。消费者满意则工单结束；不满意或 Agent 无法处理时转平台人工。进入人工阶段后才创建会话并开放对话框，平台客服还可以邀请商家加入会话。

> **商家端只能参与被邀请的会话，工单、AI 分析和平台订单数据对商家不可见。**

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Vue Router、Pinia、Element Plus |
| 后端 | FastAPI、Pydantic v2、SQLAlchemy 2、PyMySQL |
| 数据库 | MySQL 8（本地演示可切换 SQLite） |
| Agent | 简单顺序编排 + DeepSeek（OpenAI 兼容 API），后续替换为 LangGraph |
| 认证 | 服务端 session token、Argon2 密码哈希、72 小时有效期 |

## 已实现功能

### 消费者端

- 注册、登录、3 天内免登录
- 我的订单按状态分类：待付款、待发货、待收货、待评价、已完成、退款/售后、已取消
- 提交售后申请，用户侧统一使用「售后」而不是「工单」
- 三个 Agent 自动处理售后，展示 AI 建议
- 用户确认已解决，或将结果转人工
- 只有转人工后，才开放与平台客服的人工会话
- 商家被邀请后，消费者可以看到商家客服消息

### 平台客服端

- 工单中心：AI 处理中 / 转人工 / 已结束分类，支持搜索
- 查看 AI Agent 完整处理链路、关联订单、用户反馈
- 订单查询：按订单号、消费者、手机号、商品搜索
- 用户会话：只在转人工后出现
- 接入会话、回复消费者、结束会话
- 搜索商家并邀请商家加入会话

### 商家端

- 只展示平台邀请加入的会话
- 可以和消费者、平台客服共同沟通
- 无工单、订单、AI 分析入口
- 后端接口同样禁止访问工单和平台数据

## 项目目录

```text
.
├─ app/                              # FastAPI 后端
│  ├─ api/
│  │  ├─ deps.py                     # Bearer session、角色权限依赖
│  │  └─ v1/
│  │     ├─ router.py
│  │     └─ endpoints/               # auth / buyer / platform / merchant API
│  ├─ agents/                        # 三个 Agent 和顺序编排器
│  │  ├─ llm_client.py               # DeepSeek / OpenAI 兼容客户端
│  │  ├─ rules.py                    # 无 Key 时的规则降级
│  │  ├─ orchestrator.py             # 分类 → 检索 → 回复 → 转人工
│  │  └─ prompts/                    # 分类与回复 Prompt
│  ├─ core/                          # 配置、安全、枚举常量
│  ├─ db/                            # engine / session / 演示数据种子
│  ├─ models/                        # SQLAlchemy 模型
│  ├─ schemas/                       # Pydantic 接口模型
│  ├─ services/                      # 认证、工单、会话、序列化
│  └─ main.py                        # FastAPI 入口
├─ database/
│  ├─ schema.sql                     # 完整 MySQL 表结构
│  ├─ seed_orders_50.sql             # 50 条订单和 72 条明细种子
│  ├─ orders_seed_data.json          # 后端自动种子使用的订单快照
│  ├─ generate_orders_seed.py
│  └─ README.md
├─ frontend/                         # Vue 3 前端
├─ tests/                            # FastAPI + SQLite 测试
├─ .env                              # 本地密钥配置（不提交）
├─ .env.example                      # 可提交的环境变量模板
├─ main.py                           # 兼容入口：from app.main import app
└─ pyproject.toml
```

## 快速启动

### 1. 配置环境变量

复制模板：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

至少需要配置：

```env
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/after_sale_agent?charset=utf8mb4
PLATFORM_REGISTER_INVITE_CODE=你的平台邀请码
```

DeepSeek 另填：

```env
LLM_PROVIDER=deepseek
LLM_API_KEY=你的 DeepSeek API Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-flash
```

说明：

- `.env` 已被 `.gitignore` 忽略，不会提交
- `.env.example` 不包含任何真实密钥
- 未配置 `LLM_API_KEY` 时，Agent 自动使用规则降级，流程仍可运行
- 目前前端和后端都只使用后端的 Key，密钥不会进入浏览器

### 2. 启动后端

```bash
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

接口文档：<http://127.0.0.1:8000/docs>

后端启动时会：

1. 自动建表
2. 创建三个演示账号和演示商家
3. 如果订单表为空，自动写入 50 条演示订单
4. 创建 AI/人工阶段的演示工单和会话

如果 MySQL 暂时不可用，可以使用 SQLite 快速演示。

PowerShell（项目当前默认终端）：

```powershell
$env:DATABASE_URL = "sqlite:///./dev_demo.db"
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Git Bash / macOS：

```bash
DATABASE_URL="sqlite:///./dev_demo.db" uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> 如果启动时报 `WinError 10013` 或端口占用，先用
> `netstat -ano | findstr :8000` 检查 8000 是否已被另一个服务占用。
> 本项目开发时请确保只启动一个后端实例。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：<http://127.0.0.1:5173>

## 演示账号

| 端 | 账号 | 密码 |
| --- | --- | --- |
| 消费者 | `13812345678` | `Demo1234` |
| 平台客服 | `agent01` | `Platform1234` |
| 商家 | `merchant01` | `Merchant1234` |

平台客服注册邀请码由 `.env` 中的 `PLATFORM_REGISTER_INVITE_CODE` 决定；本地默认示例值为 `ORANGE-PLATFORM-2026`，建议自行替换。

右侧固定竖排三个角色选项卡，分别进入三个独立端。三个端登录状态相互独立，可在同一个浏览器中同时打开三个标签页完成联动演示。

## 核心流程图

```text
消费者提交完整售后表单
        ↓
创建工单（AI 处理中）
        ↓
分类 Agent
  ├─ 低置信度 / 无法识别 → 转人工
  └─ 数据检索 Agent
        ├─ 数据异常 → 转人工
        └─ 回复 Agent
              ├─ 信息不足 → 转人工
              └─ AI 处理建议
                    ↓
              用户反馈
              ├─ 已解决 → 工单结束
              └─ 不满意 → 转人工
                        ↓
              创建/复用人工会话
                        ↓
              平台客服接入
                        ↓
              平台邀请商家（可选）
                        ↓
              消费者 + 平台 + 商家协同对话
```

## AI Agent 说明

当前版本使用简单顺序编排，不依赖 LangGraph：

1. **分类 Agent**：使用 DeepSeek 或规则识别售后类型和置信度，输出处理步骤
2. **数据检索 Agent**：只从 MySQL 检索订单、商品、物流等事实，不让模型编造订单数据
3. **回复 Agent**：把分类和事实整合成消费者可读的处理建议

任何 Agent 失败、低置信度或信息不足都会自动转人工。所有 Agent 执行记录会保存到 `ticket_agent_runs`，平台可在工单详情查看。

后续会把 `AgentOrchestrator` 替换为 LangGraph 状态图，保留现有 Agent 接口、Prompt、工单状态和 API：

```env
AGENT_ORCHESTRATOR=langgraph
```

## 测试

后端测试使用独立 SQLite 数据库，不依赖本地 MySQL：

```bash
uv run pytest -q
```

当前覆盖：

- 三端登录和角色隔离
- 订单列表与平台搜索
- 售后提交、三个 Agent 执行
- 用户反馈后转人工
- 平台接入、发送消息、邀请商家
- 商家会话数据中不包含工单、订单字段
- 转人工自动升级
- 注册和平台邀请码

前端构建：

```bash
cd frontend
npm run build
```

## 数据库脚本

- [`database/schema.sql`](./database/schema.sql)：完整 MySQL 表结构
- [`database/seed_orders_50.sql`](./database/seed_orders_50.sql)：50 条订单和 72 条订单明细
- 数据库启动时也会自动创建表并写入演示数据，详见 [`database/README.md`](./database/README.md)

## 安全边界与演示限制

- 这是课程 Demo，不应直接用于生产环境
- 应用 session token 存储在浏览器本地，有效期 72 小时；生产建议改成 HttpOnly Cookie
- 应用不保存明文密码，密码使用 Argon2 哈希
- 当前没有邮箱/短信验证、忘记密码、商家资质审核
- 当前使用轮询同步，不包含 WebSocket
- 商家看不到工单信息和平台订单模块，但三方会话内容对消费者和平台可见
