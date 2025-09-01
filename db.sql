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
  `rango`  VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`email`)
);

CREATE TABLE `verificacion` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(40) NOT NULL,
  `codigo` VARCHAR(20) NOT NULL,
  `contra_codificada` VARCHAR(200) NOT NULL,
  `nombre` VARCHAR(40) NOT NULL,
  `rango` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `Users` (
  `user_id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `email` varchar(255) UNIQUE,
  `telefono` varchar(255),
  `contraseña_hash` varchar(255),
  `rol` varchar(255),
  `estado` varchar(255),
  `fecha_creacion` datetime
);

CREATE TABLE `Roles` (
  `role_id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `permisos` text
);

CREATE TABLE `Products` (
  `product_id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `descripcion` text,
  `precio` decimal,
  `stock` int,
  `merchant_id` int,
  `impuestos` decimal,
  `descuentos` decimal,
  `imagen_url` varchar(255)
);

CREATE TABLE `Orders` (
  `order_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `merchant_id` int,
  `total` decimal,
  `estado` varchar(255),
  `fecha_creacion` datetime
);

CREATE TABLE `Order_Items` (
  `order_item_id` int PRIMARY KEY AUTO_INCREMENT,
  `order_id` int,
  `product_id` int,
  `cantidad` int,
  `precio_unitario` decimal
);

CREATE TABLE `Payment_Methods` (
  `method_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `tipo` varchar(255),
  `detalles` text,
  `activo` boolean
);

CREATE TABLE `Payments` (
  `payment_id` int PRIMARY KEY AUTO_INCREMENT,
  `order_id` int,
  `method_id` int,
  `monto` decimal,
  `moneda` varchar(255),
  `estado` varchar(255),
  `referencia_gateway` varchar(255),
  `fecha` datetime
);

CREATE TABLE `Invoices` (
  `invoice_id` int PRIMARY KEY AUTO_INCREMENT,
  `order_id` int,
  `numero_factura` varchar(255),
  `archivo_pdf` varchar(255),
  `fecha_emision` datetime,
  `estado` varchar(255)
);

CREATE TABLE `Customers` (
  `customer_id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `email` varchar(255),
  `telefono` varchar(255),
  `historial_puntos` int
);

CREATE TABLE `Notifications` (
  `notification_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `tipo` varchar(255),
  `mensaje` text,
  `estado` varchar(255),
  `fecha` datetime
);

CREATE TABLE `Tickets` (
  `ticket_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `payment_id` int,
  `asunto` varchar(255),
  `descripcion` text,
  `estado` varchar(255),
  `fecha_creacion` datetime
);

ALTER TABLE `Products` ADD FOREIGN KEY (`merchant_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Orders` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Orders` ADD FOREIGN KEY (`merchant_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`);

ALTER TABLE `Order_Items` ADD FOREIGN KEY (`product_id`) REFERENCES `Products` (`product_id`);

ALTER TABLE `Payment_Methods` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Payments` ADD FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`);

ALTER TABLE `Payments` ADD FOREIGN KEY (`method_id`) REFERENCES `Payment_Methods` (`method_id`);

ALTER TABLE `Invoices` ADD FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`);

ALTER TABLE `Notifications` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Tickets` ADD FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`);

ALTER TABLE `Tickets` ADD FOREIGN KEY (`payment_id`) REFERENCES `Payments` (`payment_id`);

