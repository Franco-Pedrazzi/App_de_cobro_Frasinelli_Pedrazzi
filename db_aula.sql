DROP DATABASE IF EXISTS Copa_Renault;
CREATE DATABASE Copa_Renault;
USE Copa_Renault;

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


