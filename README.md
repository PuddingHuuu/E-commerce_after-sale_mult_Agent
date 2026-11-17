# 电商售后工单处理 Agent

课程实践项目：面向电商售后场景的客服工作台与 AI 对话 Demo。

当前进度：**前端已完成（Mock 数据驱动）**，后端尚未接入。

## 项目结构

```text
.
├─ frontend/      # Vue 3 前端
├─ database/      # MySQL 建表脚本和演示数据
├─ main.py        # FastAPI 入口（后端待开发）
├─ pyproject.toml
└─ README.md
```

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

- 客户页：<http://127.0.0.1:5173/service>
- 客服工作台：<http://127.0.0.1:5173/admin/workbench>

完整演示说明请查看 [`frontend/README.md`](./frontend/README.md)。

## 已实现

- 客户历史会话、新会话、AI 模拟对话
- 转人工、客服接入、人工回复、结束会话
- 客服统一工作台与客户上下文
- 订单查询、订单详情、关联售后工单
- 售后工单查询、创建、优先级与状态流转
- 订单 / 工单 / 会话互相跳转
- 同一浏览器双标签页实时同步（Mock 方案）
- 桌面端与客户移动端响应式布局
- MySQL 8 订单库建表脚本与 50 条演示订单 / 72 条商品明细种子数据

数据库说明见 [`database/README.md`](./database/README.md)。

## 规划中的后端

技术栈：

- Python + FastAPI
- LangGraph（单 Agent 对话起步，后续扩展多 Agent）
- MySQL 8
- SQLAlchemy

计划中的最小闭环：

1. 客户与 AI 的简单对话
2. MySQL 持久化会话与消息
3. 客户转人工
4. 客服工作台接入与回复
5. 订单、售后工单查询与处理

前后端接口契约与数据库设计已经在项目讨论中确定，下一步进入 FastAPI 后端实现。
