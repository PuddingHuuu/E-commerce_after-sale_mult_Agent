# 橙心售后 · 前端

三端售后协同系统前端：

- **消费者端**：订单、售后服务、转人工后的在线客服
- **平台客服端**：工单、订单、用户会话
- **商家端**：仅受邀会话

前端通过 Vite proxy 访问 `/api/v1`，完整启动方式见仓库根目录 [`README.md`](../README.md)。

## 启动

先确保 FastAPI 后端运行在 `127.0.0.1:8000`，然后：

```bash
cd frontend
npm install
npm run dev
```

访问：<http://127.0.0.1:5173>

## 路由

| 路由 | 角色 | 页面 |
| --- | --- | --- |
| `/auth/consumer` | 消费者 | 登录/注册 |
| `/consumer/orders` | 消费者 | 我的订单 |
| `/consumer/after-sales` | 消费者 | 售后服务 |
| `/consumer/after-sales/:id` | 消费者 | 售后详情、AI 结果、结果反馈 |
| `/consumer/chat` | 消费者 | 转人工后的人工会话 |
| `/auth/platform` | 平台客服 | 登录/注册 |
| `/platform/tickets` | 平台客服 | 工单中心 |
| `/platform/orders` | 平台客服 | 订单查询 |
| `/platform/conversations` | 平台客服 | 用户会话、接入、邀请商家 |
| `/auth/merchant` | 商家 | 登录/注册 |
| `/merchant/conversations` | 商家 | 受邀协同会话 |

## 登录态

- 三个角色各自存储独立的 3 天 session
- 「3 天内免登录」勾选时 token 存在 localStorage；取消时存在 sessionStorage
- 不会保存明文密码
- 账号名会被记住用于下次登录回填
- 会话过期后调用 API 会跳回对应端的登录页

右侧固定竖排「消费者 / 平台客服 / 商家」切换栏，三个端互不影响。

## 目录结构

```text
src/
├─ api/                 # Axios 封装和三个角色的 API 模块
├─ components/
│  ├─ buyer/            # 订单卡片、申请售后弹窗
│  ├─ chat/             # 消息流、输入框
│  ├─ common/           # 状态标签、空状态
│  ├─ layout/           # 右侧角色切换栏
│  └─ platform/         # 平台工单详情抽屉
├─ layouts/             # 消费者 / 平台客服 / 商家布局
├─ pages/
│  ├─ auth/             # 三端登录注册
│  ├─ buyer/
│  ├─ platform/
│  └─ merchant/
├─ router/              # 角色路由守卫
├─ stores/auth.ts       # 三端独立登录态
├─ styles/              # 设计变量和基础样式
├─ types/api.ts         # 后端接口类型
└─ utils/               # 状态文案、日期金额格式化
```

## 关键交互

### 消费者

1. 登录后浏览按状态分类的订单
2. 点击「申请售后」，选择订单并填写完整问题
3. 后端三个 Agent 自动处理，前端轮询售后状态
4. 查看 AI 处理建议
5. 点击「问题已解决」结束，或「不满意，转人工」
6. 只有转人工后才进入人工会话页

### 平台客服

1. 工单中心按 AI 处理中 / 转人工 / 已结束分类
2. 打开工单查看 AI Agent 执行链路
3. 在用户会话中接入等待中的消费者
4. 接入后回复消息，并可邀请商家加入
5. 工单数据仅平台可见

### 商家

1. 只能看到平台邀请加入的会话
2. 与消费者和平台客服沟通
3. 页面和 API 均不提供工单数据

## 构建

```bash
npm run build
```

> 当前令牌保存在 Web Storage 中，适用于课程演示；生产环境建议使用 HttpOnly Cookie 和服务端会话。
