SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
CREATE TABLE IF NOT EXISTS `enhncd_v2_order_notice` (`id` int(11) NOT NULL AUTO_INCREMENT,`tg_send_mask` tinyint(1) NOT NULL DEFAULT '0' COMMENT '-2旧数据 -1无需推送消息 0未推送消息 1已推送消息',PRIMARY KEY (`id`)) ENGINE = InnoDB DEFAULT CHARSET = utf8;