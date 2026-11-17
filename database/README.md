# 数据库种子数据

本目录用于存放项目数据库脚本和演示数据。

## 文件

| 文件 | 说明 |
| --- | --- |
| `seed_orders_50.sql` | MySQL 8.0 建表 + 50 条演示订单 + 72 条订单明细 |
| `generate_orders_seed.py` | 种子数据生成器（固定随机种子，可重复生成） |

## 订单数据说明

- **买家用户 ID：`10001`**
  - 当前用户/客户表尚未建立，所有订单先统一归属演示买家 `10001`
  - `orders.user_id` 暂不建外键，等用户体系完成后补充
- **订单数：50**
- **明细数：72**
- **金额单位：人民币元**
- **时间范围：2026-09-03 ~ 2026-11-13**
- **商品类型：** 数码 3C、家居日用、服饰运动、美妆个护、食品、母婴等常见电商商品
- **覆盖状态：** 待付款、待发货、运输中、已签收、已完成、已取消、退款中
- **收货地址和手机号均为虚构演示数据**

## 表结构

### `orders`

订单主表，包含订单状态、支付状态、履约状态、金额快照、买家备注、收货人快照、物流信息和关键时间节点。

重点字段：

- `order_no`：业务订单号，唯一索引
- `user_id`：买家 ID
- `order_status`：订单生命周期状态
- `payment_status`：支付状态
- `shipping_status`：履约状态
- `after_sale_status`：售后状态缓存，正式数据以工单表为准
- `goods_amount / discount_amount / freight_amount / payable_amount / paid_amount / refund_amount`
- `receiver_*`：收货人信息快照
- `paid_at / shipped_at / received_at / completed_at / cancelled_at / created_at / updated_at`

### `order_items`

订单商品明细表。商品名称、SKU 规格和成交单价均作为下单快照保存，后续商品信息变更不会影响历史订单。

## 导入方式

脚本已经包含数据库创建和选择语句，**不需要提前在 IDE 中选中数据库**：

```sql
CREATE DATABASE IF NOT EXISTS after_sale_agent
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE after_sale_agent;
```

如果希望使用其他数据库名，直接修改脚本顶部的 `CREATE DATABASE` 和 `USE` 两处即可。

### 方式一：命令行

```bash
mysql -h 192.168.100.132 -P 3306 -u root -p \
  --default-character-set=utf8mb4 \
  < database/seed_orders_50.sql
```

脚本会：

1. 创建数据库 `after_sale_agent`（如果不存在）
2. 创建 `orders` 和 `order_items` 表（如果不存在）
3. 插入 50 条订单
4. 插入 72 条订单明细
5. 输出订单数、商品件数、金额合计和状态分布校验结果

### 方式二：DataGrip / IDEA

1. 连接 MySQL 数据源
2. 打开 `seed_orders_50.sql`
3. 直接执行整个文件，不需要手动选择 schema
4. 刷新数据源，展开 `after_sale_agent.orders` 和 `after_sale_agent.order_items` 查看数据

如果执行数据库连接的用户没有 `CREATE DATABASE` 权限，可以手动创建数据库后，把脚本顶部的 `CREATE DATABASE` 语句注释掉再执行。

> 脚本全部使用 `INSERT IGNORE`，同一份数据重复执行不会重复插入订单。
>
> 如需重新生成演示数据，执行 `python database/generate_orders_seed.py`。

## 与前端演示数据的关系

前端目前仍使用浏览器本地 Mock 数据，尚未连接这个 MySQL 库：

- 前端 Mock 客户 ID 是 `1`
- 数据库演示买家 ID 是 `10001`

后续接入后端时，需要确定一个统一的演示客户 ID，或者建立前端演示客户到数据库客户 ID 的映射。

## 工单与会话的关系建议

**不建议强制“一个会话只能有一张工单”。**

推荐模型：

```text
conversations 1 ── N tickets
```

- 会话是沟通上下文；工单是独立的处理单元
- 一个会话可以创建 0 张、1 张或多张工单
- 每张工单聚焦一个客户问题/诉求，例如：
  - 订单 A 申请退款
  - 订单 B 换货
  - 物流异常投诉
- 同一问题涉及同一订单的多个商品时，可以在一张工单下关联多条 `ticket_items` 明细
- 不同问题应拆分为不同工单，避免状态、优先级、处理人和 SLA 被混在一起

建议工单表至少包含：

```text
ticket_no
conversation_id  -- 可空，非唯一，允许多张工单来自同一会话
order_id
subject          -- 工单主题/问题摘要
type             -- 售后类型
description
priority
status
assignee
source
created_at / updated_at / resolved_at
```

如果后续存在“同一事件导致多个客户问题”的场景，可以增加：

```text
parent_ticket_id  -- 主工单 / 子工单
ticket_items      -- 工单关联的订单商品明细
```

这样既支持“一个会话多个不同问题”，也支持“一张工单覆盖同一问题的多个商品”。
