CREATE TABLE IF NOT EXISTS item (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    available_amount INT NOT NULL
 ENGINE=INNODB;

 CREATE TABLE IF NOT EXISTS item_group (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    group VARCHAR(255) NOT NULL
 ENGINE=INNODB;

CREATE TABLE item_item_group (
    item_id INT UNSIGNED NOT NULL,
    group_id INT UNSIGNED NOT NULL,
    CONSTRAINT constr_item_item_group_item_fk
        FOREIGN KEY item_fk (item_id) REFERENCES item (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT constr_item_item_group_group_fk
        FOREIGN KEY group_fk (group_id) REFERENCES item_group (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB CHARACTER SET ascii COLLATE ascii_general_ci