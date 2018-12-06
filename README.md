### 使用pm2管理进程  
    pm2 start index.py -x --interpreter python  

### 更新sql:
    alter table onethink_api_import_game_end engine=Innodb;  
    alter table onethink_auto_api_cash_log engine=Innodb;  
    alter table onethink_player_purse engine=Innodb;  

    ALTER TABLE `onethink_auto_api_cash_log`  
        ADD COLUMN `settle_game_info` VARCHAR(255) NULL AFTER `change_time`;  
    ALTER TABLE `onethink_api_import_game_end`  
        CHANGE COLUMN `game_id` `game_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'API遊戲局ID' AFTER `game_uid`,  
        ADD COLUMN `board_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'api游戏局id' AFTER `game_id`;  
    ALTER TABLE onethink_join_game_log ADD club_room_name VARCHAR(255) NOT NULL DEFAULT '\'\'' AFTER room_name;