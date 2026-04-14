-- 单容器 MariaDB：关卡库 lv_0 … lv_13，Flag 仅在 flag_store
-- root 密码末尾设为 root_change_me

CREATE DATABASE IF NOT EXISTS `sqli_lab` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE USER IF NOT EXISTS 'sqli_app'@'localhost' IDENTIFIED BY 'sqli_app_change_me';
CREATE USER IF NOT EXISTS 'sqli_admin'@'localhost' IDENTIFIED BY 'sqli_admin_change_me';

-- ========== 模板库 lv_1（单引号等同关数据）==========
CREATE DATABASE IF NOT EXISTS `lv_1` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_1`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `col2` varchar(255) DEFAULT NULL,
  `col3` varchar(255) DEFAULT NULL,
  `col4` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `users` (`id`,`name`,`col2`,`col3`,`col4`) VALUES
 (1,'alice','a','b','c'),
 (2,'bob','x','y','z');
CREATE TABLE `flag_store` (
  `id` int NOT NULL,
  `flag` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `flag_store` (`id`,`flag`) VALUES (1,'PLACEHOLDER_FLAG');

-- ========== lv_0 数字型（结构同 lv_1）==========
CREATE DATABASE IF NOT EXISTS `lv_0` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_0`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

-- ========== 克隆 lv_1 → lv_2,3,4,5,7,8,9,11 ==========
CREATE DATABASE IF NOT EXISTS `lv_2` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_2`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_3` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_3`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_4` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_4`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_5` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_5`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_7` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_7`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_8` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_8`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_9` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_9`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

CREATE DATABASE IF NOT EXISTS `lv_11` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_11`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;

-- ========== lv_6 宽字节 GBK ==========
CREATE DATABASE IF NOT EXISTS `lv_6` DEFAULT CHARACTER SET gbk COLLATE gbk_chinese_ci;
USE `lv_6`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `col2` varchar(255) DEFAULT NULL,
  `col3` varchar(255) DEFAULT NULL,
  `col4` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
INSERT INTO `users` (`id`,`name`,`col2`,`col3`,`col4`) VALUES
 (1,'alice','a','b','c'),
 (2,'bob','x','y','z');
CREATE TABLE `flag_store` (
  `id` int NOT NULL,
  `flag` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
INSERT INTO `flag_store` (`id`,`flag`) VALUES (1,'PLACEHOLDER_FLAG');

-- ========== lv_10 POST 登录 ==========
CREATE DATABASE IF NOT EXISTS `lv_10` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_10`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `password` varchar(128) NOT NULL,
  `col3` varchar(255) DEFAULT NULL,
  `col4` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `users` (`username`,`password`,`col3`,`col4`) VALUES
 ('admin','impossible','x','y'),
 ('guest','guest','a','b');
CREATE TABLE `flag_store` (
  `id` int NOT NULL,
  `flag` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `flag_store` (`id`,`flag`) VALUES (1,'PLACEHOLDER_FLAG');

-- ========== lv_12 UA ==========
CREATE DATABASE IF NOT EXISTS `lv_12` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_12`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `ua_logs`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;
CREATE TABLE `ua_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ua` varchar(1024) NOT NULL,
  `hit` int DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========== lv_13 Referer ==========
CREATE DATABASE IF NOT EXISTS `lv_13` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `lv_13`;
DROP TABLE IF EXISTS `flag_store`;
DROP TABLE IF EXISTS `ref_logs`;
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` LIKE `lv_1`.`users`;
INSERT INTO `users` SELECT * FROM `lv_1`.`users`;
CREATE TABLE `flag_store` LIKE `lv_1`.`flag_store`;
INSERT INTO `flag_store` SELECT * FROM `lv_1`.`flag_store`;
CREATE TABLE `ref_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ref` varchar(1024) NOT NULL,
  `hit` int DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========== 权限 ==========
GRANT SELECT ON `sqli_lab`.* TO 'sqli_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_0`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_1`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_2`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_3`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_4`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_5`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_6`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_7`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_8`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_9`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_10`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_11`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_12`.* TO 'sqli_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lv_13`.* TO 'sqli_app'@'localhost';

GRANT ALL PRIVILEGES ON `sqli_lab`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_0`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_1`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_2`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_3`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_4`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_5`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_6`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_7`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_8`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_9`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_10`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_11`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_12`.* TO 'sqli_admin'@'localhost';
GRANT ALL PRIVILEGES ON `lv_13`.* TO 'sqli_admin'@'localhost';

FLUSH PRIVILEGES;

ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_change_me';
FLUSH PRIVILEGES;
