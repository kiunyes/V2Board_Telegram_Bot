SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
INSERT INTO enhncd_v2_order_notice (`id`,`tg_send_mask`) SELECT `id`,0 FROM v2_order WHERE NOT EXISTS(SELECT `id` from enhncd_v2_order_notice where `id`=v2_order.`id`);
UPDATE enhncd_v2_order_notice SET tg_send_mask = -2