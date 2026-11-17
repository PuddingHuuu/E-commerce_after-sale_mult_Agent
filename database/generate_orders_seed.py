from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20261113
rnd = random.Random(SEED)
BASE_TIME = datetime(2026, 11, 13, 21, 30, 0)
DEMO_USER_ID = 10001
SHOP_ID = 1
OUTPUT = Path(__file__).with_name('seed_orders_50.sql')

PRODUCTS = [
    {'id': 1001, 'sku': 'DIGI-EAR-001', 'name': '无线降噪耳机', 'spec': '曜石黑 / 旗舰版', 'price': 399.00},
    {'id': 1002, 'sku': 'DIGI-PHONE-001', 'name': '5G 智能手机', 'spec': '12GB+256GB / 星空蓝', 'price': 3299.00},
    {'id': 1003, 'sku': 'DIGI-LAPTOP-001', 'name': '14 英寸轻薄笔记本', 'spec': '16GB+512GB / 银灰', 'price': 4999.00},
    {'id': 1004, 'sku': 'DIGI-WATCH-001', 'name': '智能运动手表', 'spec': '46mm / 曜黑', 'price': 899.00},
    {'id': 1005, 'sku': 'DIGI-POWER-001', 'name': '20000mAh 快充充电宝', 'spec': '22.5W / 云白', 'price': 129.00},
    {'id': 1006, 'sku': 'DIGI-KEYBOARD-001', 'name': '机械键盘', 'spec': '87 键 / 茶轴', 'price': 329.00},
    {'id': 1007, 'sku': 'DIGI-MOUSE-001', 'name': '人体工学无线鼠标', 'spec': '静音版 / 灰白', 'price': 99.00},
    {'id': 1008, 'sku': 'DIGI-MONITOR-001', 'name': '27 英寸 2K 显示器', 'spec': '180Hz / IPS 屏', 'price': 1099.00},
    {'id': 1009, 'sku': 'DIGI-SPEAKER-001', 'name': '智能触屏音箱', 'spec': '触屏版 / 浅灰', 'price': 259.00},
    {'id': 1010, 'sku': 'DIGI-CAMERA-001', 'name': '4K 运动相机', 'spec': '防水套装 / 标准版', 'price': 1299.00},
    {'id': 2001, 'sku': 'HOME-CUP-001', 'name': '不锈钢真空保温杯', 'spec': '500ml / 雾蓝', 'price': 89.00},
    {'id': 2002, 'sku': 'HOME-PILLOW-001', 'name': '记忆棉护颈枕', 'spec': '标准版 / 灰色', 'price': 149.00},
    {'id': 2003, 'sku': 'HOME-BEDDING-001', 'name': '全棉四件套', 'spec': '1.8m 床 / 雾灰', 'price': 329.00},
    {'id': 2004, 'sku': 'HOME-AROMA-001', 'name': '超声波香薰机', 'spec': '300ml / 原木色', 'price': 119.00},
    {'id': 2005, 'sku': 'HOME-FRYER-001', 'name': '家用空气炸锅', 'spec': '5L / 智能款', 'price': 299.00},
    {'id': 2006, 'sku': 'HOME-RICE-001', 'name': 'IH 电饭煲', 'spec': '4L / 智能预约', 'price': 499.00},
    {'id': 2007, 'sku': 'HOME-DRYER-001', 'name': '负离子吹风机', 'spec': '1600W / 樱花粉', 'price': 269.00},
    {'id': 2008, 'sku': 'HOME-TOOTHBRUSH-001', 'name': '声波电动牙刷', 'spec': '珍珠白 / 基础款', 'price': 199.00},
    {'id': 2009, 'sku': 'HOME-LAMP-001', 'name': '国 AA 级护眼台灯', 'spec': '白色 / 无极调光', 'price': 159.00},
    {'id': 2010, 'sku': 'HOME-STORAGE-001', 'name': '折叠收纳箱', 'spec': '66L / 米白', 'price': 59.00},
    {'id': 3001, 'sku': 'CLOTH-TSHIRT-001', 'name': '纯棉基础 T 恤', 'spec': '黑色 / L', 'price': 69.00},
    {'id': 3002, 'sku': 'CLOTH-HOODIE-001', 'name': '宽松连帽卫衣', 'spec': '雾灰 / XL', 'price': 199.00},
    {'id': 3003, 'sku': 'CLOTH-DOWN-001', 'name': '轻量羽绒服', 'spec': '米白 / M', 'price': 599.00},
    {'id': 3004, 'sku': 'CLOTH-JEANS-001', 'name': '直筒牛仔裤', 'spec': '深蓝 / 30', 'price': 229.00},
    {'id': 3005, 'sku': 'SPORT-SHOES-001', 'name': '轻量跑步鞋', 'spec': '黑色 / 42', 'price': 329.00},
    {'id': 3006, 'sku': 'CLOTH-CANVAS-001', 'name': '高帮帆布鞋', 'spec': '米白 / 39', 'price': 159.00},
    {'id': 3007, 'sku': 'CLOTH-BAG-001', 'name': '城市双肩包', 'spec': '20L / 黑色', 'price': 249.00},
    {'id': 4001, 'sku': 'BEAUTY-CLEANSER-001', 'name': '氨基酸洗面奶', 'spec': '120g / 温和型', 'price': 89.00},
    {'id': 4002, 'sku': 'BEAUTY-MASK-001', 'name': '补水保湿面膜', 'spec': '10 片装', 'price': 69.00},
    {'id': 4003, 'sku': 'BEAUTY-CREAM-001', 'name': '修护面霜', 'spec': '50g / 滋润型', 'price': 199.00},
    {'id': 4004, 'sku': 'BEAUTY-PERFUME-001', 'name': '木质调淡香水', 'spec': '50ml', 'price': 359.00},
    {'id': 5001, 'sku': 'FOOD-NUTS-001', 'name': '每日坚果礼盒', 'spec': '30 袋装', 'price': 129.00},
    {'id': 5002, 'sku': 'FOOD-COFFEE-001', 'name': '精品挂耳咖啡', 'spec': '20 包 / 中度烘焙', 'price': 79.00},
    {'id': 5003, 'sku': 'FOOD-MILK-001', 'name': '全脂纯牛奶', 'spec': '250ml × 24 盒', 'price': 89.00},
    {'id': 5004, 'sku': 'FOOD-PROTEIN-001', 'name': '乳清蛋白粉', 'spec': '香草味 / 1kg', 'price': 259.00},
    {'id': 6001, 'sku': 'BABY-DIAPER-001', 'name': '婴儿纸尿裤', 'spec': 'L 码 / 48 片', 'price': 119.00},
    {'id': 6002, 'sku': 'BABY-WIPES-001', 'name': '婴儿手口湿巾', 'spec': '80 抽 × 6 包', 'price': 49.00},
    {'id': 7001, 'sku': 'SPORT-YOGA-001', 'name': '防滑瑜伽垫', 'spec': '183×61cm / 紫色', 'price': 99.00},
    {'id': 7002, 'sku': 'SPORT-MASSAGE-001', 'name': '迷你筋膜枪', 'spec': '便携款 / 灰色', 'price': 299.00},
    {'id': 7003, 'sku': 'SPORT-BADMINTON-001', 'name': '碳素羽毛球拍', 'spec': '4U / 单拍', 'price': 269.00},
    {'id': 7004, 'sku': 'SPORT-JACKET-001', 'name': '三合一户外冲锋衣', 'spec': '男款 L / 黑色', 'price': 459.00},
]

ADDRESSES = [
    ('林晓', '13812345678', '浙江省', '杭州市', '西湖区', '文三路 90 号 2 幢 502 室'),
    ('林晓', '13812345678', '上海市', '上海市', '浦东新区', '张杨路 1288 号 A 座 1203 室'),
    ('林晓', '13812345678', '江苏省', '南京市', '建邺区', '江东中路 188 号 6 栋 901 室'),
    ('林晓', '13812345678', '浙江省', '杭州市', '滨江区', '江南大道 228 号 3 幢 1102 室'),
]

PAYMENT_METHODS = ['wechat', 'alipay', 'bank_card']
SOURCES = ['app', 'app', 'app', 'mini_program', 'mini_program', 'web', 'h5', 'customer_service']
COMPANIES = ['顺丰速运', '京东物流', '中通快递', '圆通速递', '韵达快递', '菜鸟速递']
LOGISTICS_PREFIX = {
    '顺丰速运': 'SF',
    '京东物流': 'JDVA',
    '中通快递': 'ZT',
    '圆通速递': 'YT',
    '韵达快递': 'YD',
    '菜鸟速递': 'CN',
}
BUYER_NOTES = [
    None,
    None,
    None,
    '请尽量工作日送达',
    '需要开具电子发票',
    '请放快递柜，谢谢',
    '易碎品请轻拿轻放',
    '送到后电话联系',
    '不要用有异味的外包装',
]
CANCEL_REASONS = ['超时未支付', '用户主动取消', '重复下单', '收货地址填写错误']

STATUS_PLAN = [
    ('pending_payment', 3),
    ('pending_shipment', 9),
    ('shipped', 9),
    ('received', 8),
    ('completed', 12),
    ('cancelled', 4),
    ('refunding', 5),
]


def money(value: float) -> str:
    return f'{value:.2f}'


def sql_str(value: str | None) -> str:
    if value is None:
        return 'NULL'
    return "'" + value.replace("'", "''") + "'"


def sql_dt(value: datetime | None) -> str:
    if value is None:
        return 'NULL'
    return "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"


def at(days_ago: int, hour: int, minute: int) -> datetime:
    day = (BASE_TIME - timedelta(days=days_ago)).date()
    return datetime(day.year, day.month, day.day, hour, minute, 0)


def clamp_future(value: datetime) -> datetime:
    return min(value, BASE_TIME - timedelta(minutes=4))


def build_orders() -> list[dict]:
    statuses: list[str] = []
    for status, count in STATUS_PLAN:
        statuses.extend([status] * count)
    rnd.shuffle(statuses)

    orders: list[dict] = []
    for index, status in enumerate(statuses):
        if index < 6:
            address = ADDRESSES[index % len(ADDRESSES)]
        else:
            address = rnd.choice(ADDRESSES)

        if status == 'pending_payment':
            created = clamp_future(BASE_TIME - timedelta(hours=rnd.randint(1, 30), minutes=rnd.randint(0, 59)))
            payment_status = 'unpaid'
            shipping_status = 'unshipped'
            after_sale_status = 'none'
            paid_at = shipped_at = received_at = completed_at = cancelled_at = None
            payment_method = None
            logistics_company = tracking_no = None
            order_note = rnd.choice(BUYER_NOTES[:4])
            cancel_reason = None
            refund_amount = 0.0
        elif status == 'pending_shipment':
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(1, 4), hours=rnd.randint(1, 10)))
            paid_at = created + timedelta(minutes=rnd.randint(1, 90))
            payment_status = 'paid'
            shipping_status = 'unshipped'
            after_sale_status = 'none'
            shipped_at = received_at = completed_at = cancelled_at = None
            payment_method = rnd.choice(PAYMENT_METHODS)
            logistics_company = tracking_no = None
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = None
            refund_amount = 0.0
        elif status == 'shipped':
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(2, 8), hours=rnd.randint(0, 20)))
            paid_at = created + timedelta(minutes=rnd.randint(2, 120))
            shipped_at = clamp_future(paid_at + timedelta(hours=rnd.randint(3, 24)))
            payment_status = 'paid'
            shipping_status = 'shipped'
            after_sale_status = 'none'
            received_at = completed_at = cancelled_at = None
            payment_method = rnd.choice(PAYMENT_METHODS)
            logistics_company = rnd.choice(COMPANIES)
            tracking_no = f"{LOGISTICS_PREFIX[logistics_company]}{rnd.randint(10**12, 10**13 - 1)}"
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = None
            refund_amount = 0.0
        elif status == 'received':
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(8, 20), hours=rnd.randint(0, 20)))
            paid_at = created + timedelta(minutes=rnd.randint(2, 120))
            shipped_at = clamp_future(paid_at + timedelta(hours=rnd.randint(4, 30)))
            received_at = clamp_future(shipped_at + timedelta(hours=rnd.randint(18, 72)))
            payment_status = 'paid'
            shipping_status = 'delivered'
            after_sale_status = 'none'
            completed_at = cancelled_at = None
            payment_method = rnd.choice(PAYMENT_METHODS)
            logistics_company = rnd.choice(COMPANIES)
            tracking_no = f"{LOGISTICS_PREFIX[logistics_company]}{rnd.randint(10**12, 10**13 - 1)}"
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = None
            refund_amount = 0.0
        elif status == 'completed':
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(18, 72), hours=rnd.randint(0, 20)))
            paid_at = created + timedelta(minutes=rnd.randint(2, 180))
            shipped_at = clamp_future(paid_at + timedelta(hours=rnd.randint(4, 30)))
            received_at = clamp_future(shipped_at + timedelta(hours=rnd.randint(18, 72)))
            completed_at = clamp_future(received_at + timedelta(days=rnd.randint(1, 4)))
            payment_status = 'paid'
            shipping_status = 'delivered'
            after_sale_status = 'none'
            cancelled_at = None
            payment_method = rnd.choice(PAYMENT_METHODS)
            logistics_company = rnd.choice(COMPANIES)
            tracking_no = f"{LOGISTICS_PREFIX[logistics_company]}{rnd.randint(10**12, 10**13 - 1)}"
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = None
            refund_amount = 0.0
        elif status == 'cancelled':
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(2, 28), hours=rnd.randint(0, 20)))
            cancelled_at = clamp_future(created + timedelta(minutes=rnd.randint(15, 240)))
            if rnd.random() < 0.5:
                paid_at = None
                payment_status = 'closed'
                payment_method = None
                refund_amount = 0.0
            else:
                paid_at = created + timedelta(minutes=rnd.randint(1, 60))
                payment_status = 'refunded'
                payment_method = rnd.choice(PAYMENT_METHODS)
                refund_amount = None
            shipping_status = 'unshipped'
            after_sale_status = 'none'
            shipped_at = received_at = completed_at = None
            logistics_company = tracking_no = None
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = rnd.choice(CANCEL_REASONS)
        else:  # refunding
            created = clamp_future(BASE_TIME - timedelta(days=rnd.randint(6, 32), hours=rnd.randint(0, 20)))
            paid_at = created + timedelta(minutes=rnd.randint(2, 180))
            shipped_at = clamp_future(paid_at + timedelta(hours=rnd.randint(4, 30)))
            received_at = clamp_future(shipped_at + timedelta(hours=rnd.randint(24, 80)))
            payment_status = 'refunding'
            shipping_status = 'delivered'
            after_sale_status = 'processing'
            completed_at = cancelled_at = None
            payment_method = rnd.choice(PAYMENT_METHODS)
            logistics_company = rnd.choice(COMPANIES)
            tracking_no = f"{LOGISTICS_PREFIX[logistics_company]}{rnd.randint(10**12, 10**13 - 1)}"
            order_note = rnd.choice(BUYER_NOTES)
            cancel_reason = None
            refund_amount = None

        orders.append({
            'status': status,
            'created_at': created,
            'paid_at': paid_at,
            'shipped_at': shipped_at,
            'received_at': received_at,
            'completed_at': completed_at,
            'cancelled_at': cancelled_at,
            'payment_status': payment_status,
            'shipping_status': shipping_status,
            'after_sale_status': after_sale_status,
            'payment_method': payment_method,
            'source': rnd.choice(SOURCES),
            'buyer_note': order_note,
            'cancel_reason': cancel_reason,
            'receiver': address,
            'logistics_company': logistics_company,
            'tracking_no': tracking_no,
            'refund_amount': refund_amount,
        })

    orders.sort(key=lambda item: item['created_at'])
    return orders


def enrich_items(orders: list[dict]) -> None:
    for index, order in enumerate(orders):
        order['id'] = 100001 + index
        order['order_no'] = f"SO{order['created_at'].strftime('%Y%m%d')}{index + 1:04d}"

        item_count = rnd.choices([1, 2], weights=[6, 4], k=1)[0]
        selected_products = rnd.sample(PRODUCTS, item_count)
        items = []
        goods_amount = 0.0
        for product in selected_products:
            quantity = 1 if product['price'] >= 300 else rnd.randint(1, 3)
            item_amount = round(product['price'] * quantity, 2)
            goods_amount += item_amount
            items.append({
                'product': product,
                'quantity': quantity,
                'item_amount': item_amount,
            })

        goods_amount = round(goods_amount, 2)
        discount_amount = rnd.choices(
            [0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 80.0],
            weights=[50, 12, 14, 10, 7, 4, 3],
            k=1,
        )[0]
        discount_amount = min(discount_amount, max(0.0, goods_amount - 0.01))
        freight_amount = 0.0 if goods_amount >= 99 else float(rnd.choice([6, 8, 10, 12]))
        payable_amount = round(goods_amount - discount_amount + freight_amount, 2)
        order['goods_amount'] = goods_amount
        order['discount_amount'] = round(discount_amount, 2)
        order['freight_amount'] = round(freight_amount, 2)
        order['payable_amount'] = payable_amount
        order['paid_amount'] = 0.0 if order['payment_status'] in ('unpaid', 'closed') else payable_amount
        order['item_count'] = sum(item['quantity'] for item in items)
        order['items'] = items

        if order['payment_status'] == 'refunded':
            order['refund_amount'] = order['paid_amount']
        elif order['payment_status'] == 'refunding':
            refund_ratio = rnd.choice([0.3, 0.5, 0.8, 1.0])
            order['refund_amount'] = round(order['paid_amount'] * refund_ratio, 2)
        else:
            order['refund_amount'] = 0.0

        updated_candidates = [
            order['created_at'],
            order['paid_at'],
            order['shipped_at'],
            order['received_at'],
            order['completed_at'],
            order['cancelled_at'],
        ]
        if order['payment_status'] == 'refunding' and order['received_at']:
            updated_candidates.append(clamp_future(order['received_at'] + timedelta(days=1)))
        order['updated_at'] = max(value for value in updated_candidates if value is not None)
        if order['updated_at'] > BASE_TIME:
            order['updated_at'] = BASE_TIME - timedelta(minutes=5)

        # Allocate the order-level discount across line items so order item pay_amount adds up.
        remaining_discount = order['discount_amount']
        for item_index, item in enumerate(items):
            if item_index == len(items) - 1:
                line_discount = remaining_discount
            else:
                line_discount = round(
                    order['discount_amount'] * item['item_amount'] / goods_amount, 2
                )
                remaining_discount = round(remaining_discount - line_discount, 2)
            item['discount_amount'] = round(line_discount, 2)
            item['pay_amount'] = round(item['item_amount'] - line_discount, 2)
            if order['payment_status'] == 'refunding' and order['refund_amount'] > 0:
                item['refund_quantity'] = item['quantity'] if rnd.random() < 0.35 else 1
                item['refund_amount'] = round(
                    min(item['pay_amount'], order['refund_amount'] * item['pay_amount'] / (goods_amount - order['discount_amount'])),
                    2,
                )
            else:
                item['refund_quantity'] = 0
                item['refund_amount'] = 0.0


def build_sql(orders: list[dict]) -> str:
    ddl = """-- ============================================================
-- 电商售后工单处理 Agent · 50 条演示订单数据
-- 目标数据库：MySQL 8.0+
-- 演示买家 user_id：10001（当前用户体系尚未建立，统一使用该 ID）
-- 说明：
--   1. 脚本会自动创建并选择数据库 after_sale_agent，不依赖 IDE 当前选中的 schema；
--   2. 金额单位为人民币元，时间使用 DATETIME；
--   3. 采用订单主表 + 订单明细表，商品信息为下单时快照；
--   4. user_id 暂不建外键，待用户/客户表建立后补充；
--   5. INSERT 使用 INSERT IGNORE，重复执行不会重复插入相同 ID/订单号。
-- ============================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS after_sale_agent
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE after_sale_agent;

CREATE TABLE IF NOT EXISTS orders (
  id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单主键',
  order_no          VARCHAR(32)    NOT NULL COMMENT '业务订单号',
  user_id           BIGINT UNSIGNED NOT NULL COMMENT '买家用户ID；当前演示统一为10001',
  shop_id           BIGINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '店铺ID',
  order_status      VARCHAR(32)    NOT NULL DEFAULT 'pending_payment' COMMENT '订单状态：pending_payment/pending_shipment/shipped/received/completed/cancelled/refunding',
  payment_status    VARCHAR(32)    NOT NULL DEFAULT 'unpaid' COMMENT '支付状态：unpaid/paid/refunding/refunded/closed',
  shipping_status   VARCHAR(32)    NOT NULL DEFAULT 'unshipped' COMMENT '履约状态：unshipped/shipped/delivered',
  after_sale_status VARCHAR(32)    NOT NULL DEFAULT 'none' COMMENT '售后状态缓存：none/processing/completed/rejected；正式数据以工单表为准',
  currency          CHAR(3)        NOT NULL DEFAULT 'CNY' COMMENT '币种',
  goods_amount      DECIMAL(12,2)  NOT NULL COMMENT '商品原价合计',
  discount_amount   DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '优惠金额',
  freight_amount    DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '运费',
  payable_amount    DECIMAL(12,2)  NOT NULL COMMENT '应付金额 = 商品金额 - 优惠 + 运费',
  paid_amount       DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '实付金额',
  refund_amount     DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '已退/退款中金额',
  payment_method    VARCHAR(20)    NULL COMMENT 'wechat/alipay/bank_card',
  order_source      VARCHAR(24)    NOT NULL DEFAULT 'app' COMMENT 'app/web/h5/mini_program/customer_service',
  buyer_note        VARCHAR(500)   NULL COMMENT '买家备注',
  cancel_reason     VARCHAR(200)   NULL COMMENT '取消原因',
  receiver_name     VARCHAR(50)    NOT NULL COMMENT '收货人快照',
  receiver_phone    VARCHAR(30)    NOT NULL COMMENT '收货手机号快照',
  receiver_province VARCHAR(50)    NOT NULL COMMENT '省',
  receiver_city     VARCHAR(50)    NOT NULL COMMENT '市',
  receiver_district VARCHAR(50)    NOT NULL COMMENT '区县',
  receiver_address  VARCHAR(255)   NOT NULL COMMENT '详细地址',
  logistics_company VARCHAR(50)    NULL COMMENT '承运商',
  tracking_no       VARCHAR(64)    NULL COMMENT '物流单号',
  item_count        INT UNSIGNED   NOT NULL DEFAULT 0 COMMENT '商品件数合计',
  paid_at           DATETIME       NULL COMMENT '支付时间',
  shipped_at        DATETIME       NULL COMMENT '发货时间',
  received_at       DATETIME       NULL COMMENT '签收时间',
  completed_at      DATETIME       NULL COMMENT '完成时间',
  cancelled_at      DATETIME       NULL COMMENT '取消时间',
  created_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
  updated_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  version           INT UNSIGNED   NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
  PRIMARY KEY (id),
  UNIQUE KEY uk_orders_order_no (order_no),
  KEY idx_orders_user_created (user_id, created_at),
  KEY idx_orders_status_created (order_status, created_at),
  KEY idx_orders_payment_status (payment_status),
  KEY idx_orders_tracking_no (tracking_no),
  KEY idx_orders_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单主表';

CREATE TABLE IF NOT EXISTS order_items (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单明细主键',
  order_id         BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
  product_id       BIGINT UNSIGNED NULL COMMENT '商品ID；商品中心建立后关联',
  sku_id           VARCHAR(64)    NULL COMMENT 'SKU编码',
  product_name     VARCHAR(200)   NOT NULL COMMENT '商品名称快照',
  sku_spec         VARCHAR(200)   NULL COMMENT '规格快照',
  unit_price       DECIMAL(12,2)  NOT NULL COMMENT '成交单价',
  quantity         INT UNSIGNED   NOT NULL COMMENT '购买数量',
  item_amount      DECIMAL(12,2)  NOT NULL COMMENT '明细原始金额 = 单价 × 数量',
  discount_amount  DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '明细分摊优惠',
  pay_amount       DECIMAL(12,2)  NOT NULL COMMENT '明细实付金额（不含运费）',
  refund_quantity  INT UNSIGNED   NOT NULL DEFAULT 0 COMMENT '已申请退款数量',
  refund_amount    DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT '明细退款金额',
  created_at       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_order_items_order_id (order_id),
  KEY idx_order_items_product_id (product_id),
  CONSTRAINT fk_order_items_order
    FOREIGN KEY (order_id) REFERENCES orders (id)
    ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单商品明细表';

START TRANSACTION;
"""

    order_columns = [
        'id', 'order_no', 'user_id', 'shop_id', 'order_status', 'payment_status',
        'shipping_status', 'after_sale_status', 'currency', 'goods_amount',
        'discount_amount', 'freight_amount', 'payable_amount', 'paid_amount',
        'refund_amount', 'payment_method', 'order_source', 'buyer_note',
        'cancel_reason', 'receiver_name', 'receiver_phone', 'receiver_province',
        'receiver_city', 'receiver_district', 'receiver_address',
        'logistics_company', 'tracking_no', 'item_count', 'paid_at', 'shipped_at',
        'received_at', 'completed_at', 'cancelled_at', 'created_at', 'updated_at',
    ]
    order_rows = []
    for order in orders:
        receiver = order['receiver']
        values = [
            str(order['id']),
            sql_str(order['order_no']),
            str(DEMO_USER_ID),
            str(SHOP_ID),
            sql_str(order['status']),
            sql_str(order['payment_status']),
            sql_str(order['shipping_status']),
            sql_str(order['after_sale_status']),
            "'CNY'",
            money(order['goods_amount']),
            money(order['discount_amount']),
            money(order['freight_amount']),
            money(order['payable_amount']),
            money(order['paid_amount']),
            money(order['refund_amount']),
            sql_str(order['payment_method']),
            sql_str(order['source']),
            sql_str(order['buyer_note']),
            sql_str(order['cancel_reason']),
            sql_str(receiver[0]),
            sql_str(receiver[1]),
            sql_str(receiver[2]),
            sql_str(receiver[3]),
            sql_str(receiver[4]),
            sql_str(receiver[5]),
            sql_str(order['logistics_company']),
            sql_str(order['tracking_no']),
            str(order['item_count']),
            sql_dt(order['paid_at']),
            sql_dt(order['shipped_at']),
            sql_dt(order['received_at']),
            sql_dt(order['completed_at']),
            sql_dt(order['cancelled_at']),
            sql_dt(order['created_at']),
            sql_dt(order['updated_at']),
        ]
        order_rows.append('  (' + ', '.join(values) + ')')

    item_columns = [
        'id', 'order_id', 'product_id', 'sku_id', 'product_name', 'sku_spec',
        'unit_price', 'quantity', 'item_amount', 'discount_amount', 'pay_amount',
        'refund_quantity', 'refund_amount', 'created_at',
    ]
    item_rows = []
    item_id = 200001
    for order in orders:
        for item in order['items']:
            product = item['product']
            if order['payment_status'] == 'refunding' and item['refund_quantity'] > 0:
                refund_quantity = item['refund_quantity']
                refund_amount = item['refund_amount']
            else:
                refund_quantity = 0
                refund_amount = 0.0
            values = [
                str(item_id),
                str(order['id']),
                str(product['id']),
                sql_str(product['sku']),
                sql_str(product['name']),
                sql_str(product['spec']),
                money(product['price']),
                str(item['quantity']),
                money(item['item_amount']),
                money(item['discount_amount']),
                money(item['pay_amount']),
                str(refund_quantity),
                money(refund_amount),
                sql_dt(order['created_at']),
            ]
            item_rows.append('  (' + ', '.join(values) + ')')
            item_id += 1

    sql_parts = [ddl]
    sql_parts.append(
        'INSERT IGNORE INTO orders (\n  ' + ', '.join(order_columns) + '\n) VALUES\n'
        + ',\n'.join(order_rows)
        + ';\n'
    )
    sql_parts.append(
        'INSERT IGNORE INTO order_items (\n  ' + ', '.join(item_columns) + '\n) VALUES\n'
        + ',\n'.join(item_rows)
        + ';\n'
    )
    sql_parts.append(
        """COMMIT;

-- 校验：订单数量、商品件数、状态分布
SELECT COUNT(*) AS order_count,
       SUM(item_count) AS total_item_count,
       SUM(payable_amount) AS total_payable_amount
FROM orders
WHERE user_id = 10001;

SELECT order_status,
       COUNT(*) AS order_count
FROM orders
WHERE user_id = 10001
GROUP BY order_status
ORDER BY order_count DESC;

-- 可选：重复演示时清理本脚本产生的数据（谨慎执行）
-- DELETE FROM order_items
-- WHERE order_id BETWEEN 100001 AND 100050;
-- DELETE FROM orders
-- WHERE id BETWEEN 100001 AND 100050 AND user_id = 10001;
"""
    )
    return ''.join(sql_parts)


orders = build_orders()
enrich_items(orders)
sql = build_sql(orders)
OUTPUT.write_text(sql, encoding='utf-8')
print(f'Wrote {OUTPUT}')
print(f'orders={len(orders)}, items={sum(len(order["items"]) for order in orders)}')
