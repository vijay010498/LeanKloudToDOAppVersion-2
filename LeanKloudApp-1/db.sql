show databases;
create database IF NOT exists ToDoList;
USE TODOLIST;

drop table User;
CREATE TABLE IF NOT EXISTS `ToDoList`.`User` (
`id` INT  auto_increment,
`public_id`  varchar(255),
`name` varchar(255),
`password` varchar(255),
`admin` boolean,
PRIMARY KEY (`id`),
UNIQUE KEY(`public_id`)) ; 


drop table Todo;
CREATE TABLE IF NOT EXISTS `ToDoList`.`Todo` (
`id` int auto_increment,
txt varchar(255),
due_date date,
stat ENUM ('NOT STARTED','IN PROGRESS','FINISHED'),
PRIMARY KEY (id)
); 









