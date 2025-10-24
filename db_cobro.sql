DROP DATABASE IF EXISTS cobro_db;
CREATE DATABASE cobro_db;
USE cobro_db;

CREATE TABLE `examples` (
  `id_example` INT AUTO_INCREMENT,
  `nombre` VARCHAR(50) NULL DEFAULT '-',
  PRIMARY KEY (`id_example`)
);

CREATE TABLE `usuario` (
  `nombre` VARCHAR(40) NOT NULL,
  `email` VARCHAR(40) NOT NULL,
  `contraseña` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`email`)
);

CREATE TABLE `verificacion` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(40) NOT NULL,
  `codigo` VARCHAR(20) NOT NULL,
  `contra_codificada` VARCHAR(200) NOT NULL,
  `nombre` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`id`)
);


CREATE TABLE `Products` (
  `product_id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `descripcion` varchar(255),
  `precio` decimal,
  `stock` int,
  `merchant_email` VARCHAR(40),
  `descuentos` decimal,
  `tipo` VARCHAR(50),
  `tamano` BIGINT,
  `pixel` LONGBLOB
);

CREATE TABLE `Orders` (
  `order_id` int PRIMARY KEY AUTO_INCREMENT,
  `email` VARCHAR(40) NOT NULL,
  `merchant_email` VARCHAR(40),
  `total` decimal,
  `estado` varchar(255),
  `fecha_creacion` datetime
);

CREATE TABLE `Order_Items` (
  `order_item_id` int PRIMARY KEY AUTO_INCREMENT,
  `order_id` int,
  `product_id` int,
  `cantidad` int
);

CREATE TABLE `Payments` (
  `payment_id` int PRIMARY KEY AUTO_INCREMENT,
  `order_id` int,
  `monto` decimal,
  `moneda` varchar(255),
  `estado` varchar(255),
  `referencia_gateway` varchar(255),
  `fecha` datetime
);


CREATE TABLE `Notifications` (
  `notification_id` int PRIMARY KEY AUTO_INCREMENT,
  `email` VARCHAR(40),
  `tipo` varchar(255),
  `mensaje` text,
  `estado` varchar(255),
  `fecha` datetime
);

CREATE TABLE `Tickets` (
  `ticket_id` int PRIMARY KEY AUTO_INCREMENT,
  `email` VARCHAR(40),
  `payment_id` int,
  `asunto` varchar(255),
  `descripcion` text,
  `estado` varchar(255),
  `fecha_creacion` datetime
);



ALTER TABLE `Products` ADD FOREIGN KEY (`merchant_email`) REFERENCES `usuario` (`email`);

ALTER TABLE `Orders` ADD FOREIGN KEY (`email`) REFERENCES `usuario` (`email`);

ALTER TABLE `Orders` ADD FOREIGN KEY (`merchant_email`) REFERENCES `usuario` (`email`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`product_id`) REFERENCES `Products` (`product_id`);

ALTER TABLE `Payments` ADD FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`);

ALTER TABLE `Notifications` ADD FOREIGN KEY (`email`) REFERENCES `usuario` (`email`);

ALTER TABLE `Tickets` ADD FOREIGN KEY (`email`) REFERENCES `usuario` (`email`);

ALTER TABLE `Tickets` ADD FOREIGN KEY (`payment_id`) REFERENCES `Payments` (`payment_id`);

