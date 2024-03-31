drop database if exists testingdb;
create database testingdb;
use testingdb;
drop table if exists usuario;
CREATE TABLE usuario (
    admin_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    admin_name VARCHAR(250) NOT NULL,
    admin_password VARCHAR(250) NOT NULL,
    failed_login_attempt INT DEFAULT 0,
    account_locked BOOLEAN DEFAULT FALSE,
    lock_time TIMESTAMP NULL
);



insert into usuario (admin_name, admin_password) values ('admin', 'scrypt:32768:8:1$KrHR7DdaPjwl7jb1$eacb1bd5d2f39666d83f4f082044fc4cac3bcc067c03909ef2e6d90aaaa57b00ebd9f2861ce5ad50dba32810fdda76b9086ab66e38176d06afb15b3f2051fc34');
insert into usuario (admin_name, admin_password) values ('victor', 'scrypt:32768:8:1$gVg0HM9CNRFWFswp$843f86d8816c43e0ab05dac19fc897ca159eab25099dd397c6ff45f162e9c63055df1703b6a691da4278e7869b5d02e77cda472cd7c865f4b2da27e2fd4ac8e5');
#update usuario set failed_login_attempt = 0 where admin_id = 2;
select * from usuario;
select * from login_logs;

drop procedure if exists InsertarUsuario;
DELIMITER //
CREATE PROCEDURE InsertarUsuario(
    IN p_admin_name VARCHAR(250),
    IN p_admin_password VARCHAR(250)
)
BEGIN
    INSERT INTO usuario (admin_name, admin_password) 
    VALUES (p_admin_name, p_admin_password);
END //
DELIMITER ;


drop procedure if exists ToggleUserLock;
DELIMITER //
CREATE PROCEDURE ToggleUserLock(
    IN p_admin_name VARCHAR(250),
    IN p_lock_status BOOLEAN
)
BEGIN
    IF p_lock_status THEN
        UPDATE usuario
        SET account_locked = TRUE, lock_time = NOW()
        WHERE admin_name = p_admin_name;
    ELSE
        UPDATE usuario
        SET account_locked = 0, lock_time = NULL, failed_login_attempt = 0
        WHERE admin_name = p_admin_name;
    END IF;
END //
DELIMITER ;



drop procedure if exists UpdateFailedLoginAttempts;
DELIMITER //
CREATE PROCEDURE UpdateFailedLoginAttempts(
    IN p_admin_name VARCHAR(250),
    IN p_valor int
)
BEGIN
    UPDATE usuario
    SET failed_login_attempt = p_valor
    WHERE admin_name = p_admin_name;
END //
DELIMITER ;

drop view if exists GetAllUsuarios;
CREATE VIEW GetAllUsuarios AS SELECT * FROM usuario;

CREATE TABLE login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL,
    login_attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_success BOOLEAN,
    error_message TEXT
);
DELIMITER //

CREATE PROCEDURE InsertarLoginLog(
    IN p_username VARCHAR(250),
    IN p_login_success BOOLEAN,
    IN p_error_message TEXT
)
BEGIN
    INSERT INTO login_logs (username, login_success, error_message) 
    VALUES (p_username, p_login_success, p_error_message);
END //

DELIMITER ;

