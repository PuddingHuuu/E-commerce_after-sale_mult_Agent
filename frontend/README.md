# 橙心售后 · 前端 Demo

售后工单处理 Agent 的前端实现，包含客户咨询页和客服工作台。当前使用 **浏览器 Mock 数据**，不依赖后端即可完整演示。

## 技术栈

- Vue 3 + TypeScript + Vite
- Vue Router + Pinia
- Element Plus
- dayjs

## 启动

```bash
cd frontend
npm install
npm run dev
```

浏览器打开：

- 客户咨询：<http://127.0.0.1:5173/service>
- 客服工作台：<http://127.0.0.1:5173/admin/workbench>

生产构建：

```bash
npm run build
npm run preview
```

## 页面

| 路由 | 说明 |
| --- | --- |
| `/service` | 客户页：历史会话、新建咨询、AI 对话、转人工、结束会话 |
| `/admin/workbench` | 客服工作台：待接入/服务中/已结束队列、接入会话、聊天、客户上下文 |
| `/admin/orders` | 订单查询：搜索、状态筛选、分页、订单详情、创建工单 |
| `/admin/tickets` | 售后工单：状态/类型/优先级筛选、工单详情、状态流转 |

## 演示流程

建议在**同一个浏览器**中打开两个标签页：

1. 客户页选择或新建一个咨询，发送消息，查看 AI 回复。
2. 点击右上角「转人工」。
3. 客服工作台的「待接入」出现新会话，点击会话并「接入」。
4. 客服发送回复，客户页会在广播同步后立即收到。
5. 客服可从会话创建售后工单；工单可在「售后工单」中查看和流转状态。
6. 客服可以在右侧客户上下文或「订单查询」中查看客户订单，并通过关联会话联动查看。

> 两个标签页的同步基于 `BroadcastChannel` + `localStorage`，只用于前端演示。生产版本应替换为 WebSocket/SSE 或轮询真实后端。

客服工作台左下角的「重置数据」可以恢复初始演示数据。

## Demo 身份

- 客户固定为演示客户「林晓」（`DEMO_CUSTOMER_ID = 1`）
- 客服固定为「客服小橙」
- 未实现真实登录与权限，不能作为生产后台使用

## 目录结构

```text
src/
├─ components/
│  ├─ admin/     # 工单创建弹窗、订单/工单详情抽屉
│  ├─ chat/      # 聊天消息流、输入框
│  └─ common/    # 状态标签、空状态
├─ layouts/      # 客服端整体布局
├─ mock/         # 初始种子数据、AI 模拟回复
├─ pages/
│  ├─ customer/  # 客户咨询页
│  └─ admin/     # 工作台、订单、工单
├─ router/
├─ stores/
│  ├─ mock.ts    # 演示数据存储与业务动作（localStorage + BroadcastChannel）
│  └─ adminUi.ts # 抽屉、弹窗 UI 状态
├─ styles/
├─ types/
└─ utils/
```

## 当前实现边界

- AI 回复为本地关键词模拟，**真实 LangGraph 后端尚未接入**
- 订单、工单数据为演示种子数据，数据库尚未接入
- 没有认证与权限控制
- 图片上传、SLA、内部备注、宏/快捷回复等未实现

## 后续接后端

后端规划为 FastAPI + LangGraph + MySQL，前端预计替换以下部分：

1. `stores/mock.ts` 中的初始数据和演示动作替换为 API Service。
2. AI 回复由客户消息接口调用 LangGraph 后返回。
3. 双标签页广播同步替换为 WebSocket 或轮询。
4. 补充客户/客服身份认证。
