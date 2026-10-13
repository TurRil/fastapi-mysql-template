CREATE TABLE IF NOT EXISTS items (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `transactions` (
  `transaction_id` varchar(50) NOT NULL,
  `amount` decimal(10,0) NOT NULL DEFAULT '0',
  `transaction_date` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(255) NOT NULL DEFAULT '',
  `transaction_type` enum('debit','credit') NOT NULL,
  `account_number` varchar(255) NOT NULL,
  `classification` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`transaction_id`),
  KEY `idx_type` (`transaction_type`) /*!80000 INVISIBLE */,
  KEY `idx_classification` (`classification`) /*!80000 INVISIBLE */,
  KEY `idx_transaction_date` (`transaction_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int NOT NULL,
  `category` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

