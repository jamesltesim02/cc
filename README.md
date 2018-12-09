# 1. 初始化  
### 1.1 数据库更新脚本  
    alter table onethink_api_import_game_end engine=Innodb;  
    alter table onethink_auto_api_cash_log engine=Innodb;  
    alter table onethink_player_purse engine=Innodb;  

    ALTER TABLE `onethink_auto_api_cash_log`
        ADD COLUMN `settle_game_info` VARCHAR(255) NULL AFTER `change_time`;  
    ALTER TABLE `onethink_api_import_game_end`
        CHANGE COLUMN `game_id` `game_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'API遊戲局ID' AFTER `game_uid`,  
        ADD COLUMN `board_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'api游戏局id' AFTER `game_id`;  
    ALTER TABLE onethink_join_game_log ADD club_room_name VARCHAR(255) NULL DEFAULT '' AFTER room_name;
    ALTER TABLE `onethink_api_import_game_end` CHANGE `game_id` `game_id` VARCHAR(255) 
        CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT '0' COMMENT 'API遊戲局ID';
    ALTER TABLE `onethink_join_game_log` ADD `chang_flag` TINYINT(1) NULL DEFAULT '0' AFTER `club_room_name`;
    ALTER TABLE `onethink_api_import_game_end`
	    ADD COLUMN `settle_game_info` VARCHAR(255) NULL COMMENT '汇入的战局唯一标志' AFTER `action`;

### 1.2 依赖模块  
    pip install PyMySQL  

# 2. 进程管理  
### 2.1 安装nodejs  
### 2.2 安装pm2进程管理工具  
    sudo npm install -g pm2  
### 2.3 使用pm2启动进程 
    pm2 start index.py -x --interpreter python

# 3. 配置  
### 3.1 数据库及数据提供商信息配置文件 
    config.py
### 3.2 入口文件(可以配置任务频率时间)  
    index.py
