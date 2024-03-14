/*
 Navicat Premium Data Transfer

 Source Server         : 云数据库1-mariadb1
 Source Server Type    : MariaDB
 Source Server Version : 110302 (11.3.2-MariaDB-1:11.3.2+maria~ubu2204)
 Source Host           : 47.108.39.50:10023
 Source Schema         : legal_doc_db

 Target Server Type    : MariaDB
 Target Server Version : 110302 (11.3.2-MariaDB-1:11.3.2+maria~ubu2204)
 File Encoding         : 65001

 Date: 14/03/2024 17:02:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for legal_documents
-- ----------------------------
DROP TABLE IF EXISTS `legal_documents`;
CREATE TABLE `legal_documents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `original_link` varchar(255) DEFAULT NULL,
  `court` varchar(255) DEFAULT NULL,
  `case_number` varchar(255) DEFAULT NULL,
  `document_date` date DEFAULT NULL,
  `progress` varchar(255) DEFAULT NULL,
  `html_content` longtext DEFAULT NULL,
  `is_finally` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `document_date` (`document_date`),
  KEY `court` (`court`)
) ENGINE=InnoDB AUTO_INCREMENT=196 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET FOREIGN_KEY_CHECKS = 1;
