-- ----------------------------------------------------------------------------
-- MySQL Workbench Migration
-- Migrated Schemata: broadcaster
-- Source Schemata: broadcaster
-- Created: Tue May 27 22:03:45 2014
-- ----------------------------------------------------------------------------

SET FOREIGN_KEY_CHECKS = 0;;

-- ----------------------------------------------------------------------------
-- Schema broadcaster
-- ----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `broadcaster` ;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_group
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_group` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_group_permissions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_group_permissions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `group_id` INT(11) NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `group_id` (`group_id` ASC, `permission_id` ASC),
  INDEX `auth_group_permissions_5f412f9a` (`group_id` ASC),
  INDEX `auth_group_permissions_83d7f98b` (`permission_id` ASC),
  CONSTRAINT `group_id_refs_id_f4b32aac`
    FOREIGN KEY (`group_id`)
    REFERENCES `broadcaster`.`auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_6ba0f519`
    FOREIGN KEY (`permission_id`)
    REFERENCES `broadcaster`.`auth_permission` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 15
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_permission
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_permission` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `content_type_id` INT(11) NOT NULL,
  `codename` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `content_type_id` (`content_type_id` ASC, `codename` ASC),
  INDEX `auth_permission_37ef4eb4` (`content_type_id` ASC),
  CONSTRAINT `content_type_id_refs_id_d043b34a`
    FOREIGN KEY (`content_type_id`)
    REFERENCES `broadcaster`.`django_content_type` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 16
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.django_content_type
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`django_content_type` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `app_label` VARCHAR(100) NOT NULL,
  `model` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `app_label` (`app_label` ASC, `model` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_user
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_user` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `password` VARCHAR(128) NOT NULL,
  `last_login` DATETIME NOT NULL,
  `is_superuser` TINYINT(1) NOT NULL,
  `username` VARCHAR(30) NOT NULL,
  `first_name` VARCHAR(30) NOT NULL,
  `last_name` VARCHAR(30) NOT NULL,
  `email` VARCHAR(75) NOT NULL,
  `is_staff` TINYINT(1) NOT NULL,
  `is_active` TINYINT(1) NOT NULL,
  `date_joined` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username` (`username` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_user_groups
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_user_groups` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `group_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `user_id` (`user_id` ASC, `group_id` ASC),
  INDEX `auth_user_groups_6340c63c` (`user_id` ASC),
  INDEX `auth_user_groups_5f412f9a` (`group_id` ASC),
  CONSTRAINT `user_id_refs_id_40c41112`
    FOREIGN KEY (`user_id`)
    REFERENCES `broadcaster`.`auth_user` (`id`),
  CONSTRAINT `group_id_refs_id_274b862c`
    FOREIGN KEY (`group_id`)
    REFERENCES `broadcaster`.`auth_group` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 26
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.auth_user_user_permissions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`auth_user_user_permissions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `permission_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `user_id` (`user_id` ASC, `permission_id` ASC),
  INDEX `auth_user_user_permissions_6340c63c` (`user_id` ASC),
  INDEX `auth_user_user_permissions_83d7f98b` (`permission_id` ASC),
  CONSTRAINT `user_id_refs_id_4dc23c39`
    FOREIGN KEY (`user_id`)
    REFERENCES `broadcaster`.`auth_user` (`id`),
  CONSTRAINT `permission_id_refs_id_35d9ac25`
    FOREIGN KEY (`permission_id`)
    REFERENCES `broadcaster`.`auth_permission` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;

-- ----------------------------------------------------------------------------
-- Table broadcaster.django_session
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `broadcaster`.`django_session` (
  `session_key` VARCHAR(40) NOT NULL,
  `session_data` LONGTEXT NOT NULL,
  `expire_date` DATETIME NOT NULL,
  PRIMARY KEY (`session_key`),
  INDEX `django_session_b7b81f0c` (`expire_date` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;
SET FOREIGN_KEY_CHECKS = 1;;
