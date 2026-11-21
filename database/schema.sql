-- ============================================================
-- 橙心售后 · 完整 MySQL 8 表结构
-- 说明：
--   1. 本脚本创建后端运行所需的全部表，可重复执行；
--   2. 后端启动时也会自动 create_all 并写入演示账号与演示数据；
--   3. 订单种子数据可另行执行 seed_orders_50.sql；
--   4. DeepSeek 配置放在根目录 .env，不要提交到 Git。
-- ============================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS after_sale_agent
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE after_sale_agent;

-- orders
CREATE TABLE IF NOT EXISTS orders (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, 
	order_no VARCHAR(32) NOT NULL, 
	user_id BIGINT NOT NULL, 
	shop_id BIGINT NOT NULL, 
	order_status VARCHAR(32) NOT NULL, 
	payment_status VARCHAR(32) NOT NULL, 
	shipping_status VARCHAR(32) NOT NULL, 
	after_sale_status VARCHAR(32) NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	goods_amount NUMERIC(12, 2) NOT NULL, 
	discount_amount NUMERIC(12, 2) NOT NULL, 
	freight_amount NUMERIC(12, 2) NOT NULL, 
	payable_amount NUMERIC(12, 2) NOT NULL, 
	paid_amount NUMERIC(12, 2) NOT NULL, 
	refund_amount NUMERIC(12, 2) NOT NULL, 
	payment_method VARCHAR(20), 
	order_source VARCHAR(24) NOT NULL, 
	buyer_note VARCHAR(500), 
	cancel_reason VARCHAR(200), 
	receiver_name VARCHAR(50) NOT NULL, 
	receiver_phone VARCHAR(30) NOT NULL, 
	receiver_province VARCHAR(50) NOT NULL, 
	receiver_city VARCHAR(50) NOT NULL, 
	receiver_district VARCHAR(50) NOT NULL, 
	receiver_address VARCHAR(255) NOT NULL, 
	logistics_company VARCHAR(50), 
	tracking_no VARCHAR(64), 
	item_count INTEGER NOT NULL, 
	paid_at DATETIME, 
	shipped_at DATETIME, 
	received_at DATETIME, 
	completed_at DATETIME, 
	cancelled_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (id),
  UNIQUE KEY `ix_orders_order_no` (`order_no`),
  KEY `ix_orders_order_status` (`order_status`),
  KEY `ix_orders_shop_id` (`shop_id`),
  KEY `ix_orders_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- users
CREATE TABLE IF NOT EXISTS users (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	`role` VARCHAR(16) NOT NULL, 
	login_name VARCHAR(64) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	display_name VARCHAR(80) NOT NULL, 
	phone VARCHAR(30), 
	status VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	last_login_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT uk_users_role_login_name UNIQUE (`role`, login_name),
  KEY `ix_users_login_name` (`login_name`),
  KEY `ix_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- auth_sessions
CREATE TABLE IF NOT EXISTS auth_sessions (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	user_id BIGINT NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	`role` VARCHAR(16) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	revoked_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
  KEY `ix_auth_sessions_expires_at` (`expires_at`),
  UNIQUE KEY `ix_auth_sessions_token_hash` (`token_hash`),
  KEY `ix_auth_sessions_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- merchants
CREATE TABLE IF NOT EXISTS merchants (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	user_id BIGINT NOT NULL, 
	store_name VARCHAR(120) NOT NULL, 
	contact_name VARCHAR(80), 
	phone VARCHAR(30), 
	status VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- order_items
CREATE TABLE IF NOT EXISTS order_items (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, 
	order_id BIGINT UNSIGNED NOT NULL, 
	product_id BIGINT, 
	sku_id VARCHAR(64), 
	product_name VARCHAR(200) NOT NULL, 
	sku_spec VARCHAR(200), 
	unit_price NUMERIC(12, 2) NOT NULL, 
	quantity INTEGER NOT NULL, 
	item_amount NUMERIC(12, 2) NOT NULL, 
	discount_amount NUMERIC(12, 2) NOT NULL, 
	pay_amount NUMERIC(12, 2) NOT NULL, 
	refund_quantity INTEGER NOT NULL, 
	refund_amount NUMERIC(12, 2) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE,
  KEY `ix_order_items_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- conversations
CREATE TABLE IF NOT EXISTS conversations (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	customer_id BIGINT NOT NULL, 
	order_id BIGINT UNSIGNED, 
	status VARCHAR(20) NOT NULL, 
	assigned_agent_id BIGINT, 
	merchant_id BIGINT, 
	merchant_invited_at DATETIME, 
	merchant_invited_by BIGINT, 
	last_message VARCHAR(500), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	closed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE SET NULL, 
	FOREIGN KEY(assigned_agent_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(merchant_id) REFERENCES merchants (id) ON DELETE SET NULL, 
	FOREIGN KEY(merchant_invited_by) REFERENCES users (id) ON DELETE SET NULL,
  KEY `ix_conversations_assigned_agent_id` (`assigned_agent_id`),
  KEY `ix_conversations_customer_id` (`customer_id`),
  KEY `ix_conversations_merchant_id` (`merchant_id`),
  KEY `ix_conversations_order_id` (`order_id`),
  KEY `ix_conversations_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- conversation_messages
CREATE TABLE IF NOT EXISTS conversation_messages (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	conversation_id BIGINT NOT NULL, 
	sender_type VARCHAR(16) NOT NULL, 
	sender_id BIGINT, 
	content TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
  KEY `ix_conversation_messages_conversation_id` (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- tickets
CREATE TABLE IF NOT EXISTS tickets (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	ticket_no VARCHAR(32) NOT NULL, 
	customer_id BIGINT NOT NULL, 
	order_id BIGINT UNSIGNED NOT NULL, 
	conversation_id BIGINT, 
	subject VARCHAR(200) NOT NULL, 
	description TEXT NOT NULL, 
	expected_resolution VARCHAR(500), 
	category VARCHAR(32), 
	confidence FLOAT, 
	status VARCHAR(32) NOT NULL, 
	priority VARCHAR(16) NOT NULL, 
	ai_reply TEXT, 
	ai_result_json JSON, 
	escalation_reason VARCHAR(500), 
	feedback_result VARCHAR(20), 
	feedback_reason VARCHAR(500), 
	assignee_id BIGINT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	resolved_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE RESTRICT, 
	FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE SET NULL, 
	FOREIGN KEY(assignee_id) REFERENCES users (id) ON DELETE SET NULL,
  KEY `ix_tickets_assignee_id` (`assignee_id`),
  KEY `ix_tickets_category` (`category`),
  KEY `ix_tickets_conversation_id` (`conversation_id`),
  KEY `ix_tickets_customer_id` (`customer_id`),
  KEY `ix_tickets_order_id` (`order_id`),
  KEY `ix_tickets_status` (`status`),
  UNIQUE KEY `ix_tickets_ticket_no` (`ticket_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ticket_agent_runs
CREATE TABLE IF NOT EXISTS ticket_agent_runs (
	id BIGINT NOT NULL AUTO_INCREMENT, 
	ticket_id BIGINT NOT NULL, 
	agent_name VARCHAR(32) NOT NULL, 
	sequence INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	model_name VARCHAR(80), 
	prompt_version VARCHAR(32), 
	input_json JSON, 
	output_json JSON, 
	error_message VARCHAR(1000), 
	prompt_tokens INTEGER, 
	completion_tokens INTEGER, 
	duration_ms INTEGER, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(ticket_id) REFERENCES tickets (id) ON DELETE CASCADE,
  KEY `ix_ticket_agent_runs_ticket_id` (`ticket_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

