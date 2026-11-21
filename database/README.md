# 数据库与演示数据

本目录包含后端使用的 MySQL 表结构和演示数据。

## 文件

| 文件 | 说明 |
| --- | --- |
| `schema.sql` | 后端完整表结构，包含用户、商家、登录会话、订单、工单、Agent 日志、会话和消息 |
| `seed_orders_50.sql` | 50 条订单 + 72 条订单明细的 MySQL 种子数据 |
| `orders_seed_data.json` | 后端启动时自动写入 50 条订单所使用的 JSON 快照 |
| `generate_orders_seed.py` | 同时生成 SQL 和 JSON 的订单种子生成器 |

## 数据表

```text
users                 三端账号（consumer / platform / merchant）
auth_sessions         72 小时登录会话，只保存 token 哈希
merchants             商家店铺资料
orders                订单主表；演示买家 user_id = 10001
order_items           订单商品明细快照
tickets               售后工单
ticket_agent_runs     分类 / 检索 / 回复 / 转人工执行日志
conversations         人工会话，仅转人工后创建
conversation_messages 消费者、平台客服、商家、系统消息
```

关系：

```text
users 1 ── N conversations
users 1 ── N orders
users 1 ── N tickets

conversations 1 ── N tickets
conversations 1 ── N conversation_messages
conversations 0..1 ── 1 merchants（受邀商家）

tickets 1 ── N ticket_agent_runs
```

### 工单和会话

- 一个会话可以关联多张工单
- 每张工单聚焦一个售后问题
- 同一用户再次转人工时，会优先复用已有的人工会话
- 商家可以看到会话消息，但后端不会向商家返回任何工单数据

## 演示账号

后端首次启动会自动创建：

| 角色 | 账号 | 密码 |
| --- | --- | --- |
| 消费者 | `13812345678` | `Demo1234` |
| 平台客服 | `agent01` | `Platform1234` |
| 商家 | `merchant01` | `Merchant1234` |

演示消费者 ID 为 `10001`，演示商家 ID 为 `1`。后端会自动给所有 50 条订单设置 `user_id=10001`、`shop_id=1`。

账号密码以 Argon2 哈希写入 `users.password_hash`。

## 推荐初始化方式

直接启动后端即可。后端会：

1. 自动 `create_all()` 建表
2. 自动创建演示账号、商家
3. 订单表为空时读取 `orders_seed_data.json` 写入 50 条订单
4. 创建 AI 处理中、转人工、人工处理中、已完成等演示工单和会话

```bash
uv run uvicorn app.main:app --reload --port 8000
```

## 手动导入 MySQL

如果你的 MySQL 需要手动初始化：

1. 在 DataGrip 中执行 `schema.sql`
2. 再执行 `seed_orders_50.sql`
3. 启动后端，后端仍会自动补齐演示账号、商家、工单和会话

两个脚本都包含 `CREATE DATABASE IF NOT EXISTS after_sale_agent` 和 `USE after_sale_agent;`，不需要手动选择 schema。

```bash
mysql -h 192.168.100.132 -P 3306 -u root -p \
  --default-character-set=utf8mb4 \
  < database/schema.sql

mysql -h 192.168.100.132 -P 3306 -u root -p \
  --default-character-set=utf8mb4 \
  < database/seed_orders_50.sql
```

> 后端通过根目录 `.env` 中的 `DATABASE_URL` 连接数据库。
>
> `schema.sql` 由 SQLAlchemy 模型按 MySQL 方言生成，包含索引和外键；SQLite 测试会自动使用同一套 ORM 模型。

## 重新生成订单数据

```bash
python database/generate_orders_seed.py
```

会重新生成：

- `seed_orders_50.sql`
- `orders_seed_data.json`

## 本地 SQLite 快速演示

不配置 MySQL 时，可以直接用 SQLite 启动后端：

```bash
DATABASE_URL="sqlite:///./dev_demo.db" uv run uvicorn app.main:app --reload
```

SQLite 文件已被 `.gitignore` 忽略，仅用于课程演示。
