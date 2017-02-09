/*creates a database or if it already exists it uses*/

CREATE DATABASE IF NOT EXISTS `hindu`;

/*use the database*/

use `hindu`;

/*creating a table resolved_news_type*/

CREATE TABLE IF NOT EXISTS `resolved_news_type` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`resolved_news_type_name` VARCHAR(250) DEFAULT NULL UNIQUE, 
	CONSTRAINT pk_resolved_news_type_id PRIMARY KEY(`id`)
	) AUTO_INCREMENT=1;

/*creating a table unresolved_news_type*/

CREATE TABLE IF NOT EXISTS `unresolved_news_type` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`unresolved_news_type_name` VARCHAR(250) DEFAULT NULL, 
	CONSTRAINT pk_unresolved_news_type_id PRIMARY KEY(`id`)
	) AUTO_INCREMENT=1;

/*creating a table resolved_news_type_unresolved_news_type_map*/

CREATE TABLE IF NOT EXISTS `resolved_news_type_unresolved_news_type_map` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`resolved_news_type_id` SMALLINT UNSIGNED NOT NULL ,
	`unresolved_news_type_id` SMALLINT UNSIGNED NOT NULL UNIQUE,
	CONSTRAINT pk_unresolved_news_type_id PRIMARY KEY(`id`),
	CONSTRAINT fk_news_type FOREIGN KEY(`resolved_news_type_id`) 
	REFERENCES resolved_news_type(`id`) ON DELETE NO ACTION,
	CONSTRAINT fk_unresolved_news_type FOREIGN KEY(`unresolved_news_type_id`) 
	REFERENCES unresolved_news_type(`id`) 
	ON DELETE NO ACTION
	) AUTO_INCREMENT=1;

/*creating a table resolved_location*/

CREATE TABLE IF NOT EXISTS `resolved_location` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`resolved_location_name` VARCHAR(250) NOT NULL UNIQUE, 
	CONSTRAINT pk_resolved_location_id PRIMARY KEY(`id`)
	) AUTO_INCREMENT=1;

/*creating a table unresolved_location*/

CREATE TABLE IF NOT EXISTS `unresolved_location` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`unresolved_location_name` VARCHAR(250) DEFAULT NULL, 
	CONSTRAINT pk_unresolved_location_id PRIMARY KEY(`id`)
	) AUTO_INCREMENT=1;

/*creating a table resolved_location_unresolved_location_map*/

CREATE TABLE IF NOT EXISTS `resolved_location_unresolved_location_map` (
	`id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	`resolved_location_id` SMALLINT UNSIGNED NOT NULL ,
	`unresolved_location_id` SMALLINT UNSIGNED NOT NULL UNIQUE,
	CONSTRAINT pk_resolved_location_unresolved_location_map_id PRIMARY KEY(`id`),
	CONSTRAINT fk_resolved_location_id FOREIGN KEY(`resolved_location_id`) 
	REFERENCES resolved_location(`id`) ON DELETE NO ACTION,
	CONSTRAINT fk_unresolved_location_id FOREIGN KEY(`unresolved_location_id`) 
	REFERENCES unresolved_location(`id`) ON DELETE NO ACTION
	) AUTO_INCREMENT=1;

/*creating a table source*/

CREATE TABLE IF NOT EXISTS `source` (
	`id` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT ,
	`source_name` VARCHAR(250) NOT NULL UNIQUE,
	CONSTRAINT pk_source_id PRIMARY KEY(`id`)
	) AUTO_INCREMENT=1;


/*creating a table article_download*/

CREATE TABLE IF NOT EXISTS `article_download` (
	`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	`article_download_local_file_path` VARCHAR(250) NOT NULL UNIQUE,
	`article_download_created_date` DATETIME NOT NULL,
	`article_download_last_updated_date` DATETIME NOT NULL,
	`article_download_url` VARCHAR(250) NOT NULL UNIQUE,
	`article_download_unique_id` VARCHAR(250) NOT NULL UNIQUE,
	`article_download_is_parsed` TINYINT(1) default 0,
	CONSTRAINT pk_article_main_id PRIMARY KEY(`id`))AUTO_INCREMENT=1;


/*creating a table article_parsed*/

CREATE TABLE IF NOT EXISTS `article_parsed` (
	`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	`article_title` VARCHAR(250) NOT NULL,
	`unresolved_news_type_id` SMALLINT UNSIGNED NOT NULL,
	`published_date` DATETIME NOT NULL,
	`unresolved_location_id` SMALLINT UNSIGNED ,
	`source_id` SMALLINT(3) UNSIGNED NOT NULL,
	`article_download_id` INT UNSIGNED NOT NULL UNIQUE,
	
	CONSTRAINT pk_article_main_id PRIMARY KEY(`id`),
	CONSTRAINT fk_article_download_id FOREIGN KEY(`article_download_id`) 
	REFERENCES article_download(`id`) ON DELETE NO ACTION,
	CONSTRAINT fk_article_news_type FOREIGN KEY(`unresolved_news_type_id`) 
	REFERENCES unresolved_news_type(`id`) ON DELETE NO ACTION,
	CONSTRAINT fk_article_location_id FOREIGN KEY(`unresolved_location_id`) 
	REFERENCES unresolved_location(`id`) ON DELETE NO ACTION,
	CONSTRAINT fk_content_source_id FOREIGN KEY(`source_id`) 
	REFERENCES source(`id`) ON DELETE NO ACTION
	) AUTO_INCREMENT=1;

/*creating a table article_content*/

CREATE TABLE IF NOT EXISTS `article_content` (
	`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	`article_parsed_id` INT UNSIGNED NOT NULL UNIQUE,
	`content` TEXT NOT NULL,
	CONSTRAINT pk_article_content_id PRIMARY KEY(`id`),
	CONSTRAINT fk_content_article_id FOREIGN KEY(`article_parsed_id`) 
	REFERENCES article_parsed(`id`) ON DELETE NO ACTION
	) AUTO_INCREMENT=1;

/*creating a table author*/

CREATE TABLE IF NOT EXISTS `author` (
	`id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
	`author_name` VARCHAR(250) NOT NULL,
	`article_parsed_id` INT UNSIGNED NOT NULL UNIQUE,
	CONSTRAINT pk_author_id PRIMARY KEY(`id`),
	CONSTRAINT fk_author_article_id FOREIGN KEY(`article_parsed_id`) 
	REFERENCES article_parsed(`id`) ON DELETE NO ACTION
	) AUTO_INCREMENT=1;




