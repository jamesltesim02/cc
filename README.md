# 1. 初始化  
### 1.1. 数据库更新脚本  
#### 1.1.1. 代理商同步任务更新脚本  
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

#### 1.1.2. CMS同步任务更新脚本  
    alter table onethink_historygamedetail engine=Innodb;  
    alter table onethink_cms_game_end engine=Innodb;  
    alter table onethink_cms_buyin_log engine=Innodb;  
    alter table onethink_cms_auto_cash_log engine=Innodb;
    alter table onethink_historygamelist engine=Innodb;
    
    ALTER TABLE `onethink_cms_game_end`
        CHANGE COLUMN `create_game_time` `create_game_time` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '創造時間' AFTER `game_id`,
        CHANGE COLUMN `end_game_time` `end_game_time` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '遊戲結束時間' AFTER `create_game_time`,
        CHANGE COLUMN `apply_time` `apply_time` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '執行時間'  AFTER `end_game_time`;

    ALTER TABLE `onethink_cms_auto_cash_log` ADD `settle_game_info` VARCHAR(255) NULL DEFAULT NULL AFTER `change_time`;

#### 1.1.3 coco同步任务脚本  
    -- 额度变更记录表 --
    drop table if exists `onethink_coco_auto_cash_log`;
    CREATE TABLE `onethink_coco_auto_cash_log` (
        `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '文档ID',
        `username` VARCHAR(255) NOT NULL COMMENT '會員名稱',
        `cash` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '原本金錢',
        `diamond` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '原本鑽石',
        `point` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '原本積分',
        `change_cash` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '更改金錢',
        `change_diamond` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '更改鑽石',
        `change_point` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '更改積分',
        `apply_time` INT(10) UNSIGNED NOT NULL DEFAULT '0',
        `change_time` INT(10) UNSIGNED NOT NULL DEFAULT '0',
        `settle_game_info` VARCHAR(255) NULL DEFAULT NULL,
        PRIMARY KEY (`id`)
    )
    COLLATE='utf8_general_ci'
    ENGINE=InnoDB
    AUTO_INCREMENT=1;

    -- 上分审批记录 --
    drop table if exists `onethink_coco_join_game_log`;
    CREATE TABLE `onethink_coco_join_game_log` (
        `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
        `userid` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '會員ID' COLLATE 'utf8mb4_bin',
        `username` VARCHAR(255) NOT NULL COMMENT '會員帳號' COLLATE 'utf8mb4_bin',
        `game_vid` VARCHAR(255) NOT NULL COMMENT '遊戲VID' COLLATE 'utf8mb4_bin',
        `club_id` VARCHAR(255) NOT NULL COMMENT '俱樂部ID' COLLATE 'utf8mb4_bin',
        `join_cash` VARCHAR(255) NOT NULL COMMENT '上分金額' COLLATE 'utf8mb4_bin',
        `application_time` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '申請時間',
        `check_time` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '審核時間',
        `check_user` VARCHAR(255) NULL DEFAULT NULL COMMENT '審核人員' COLLATE 'utf8mb4_bin',
        `check_status` VARCHAR(255) NOT NULL DEFAULT '0' COMMENT '審核結果' COLLATE 'utf8mb4_bin',
        `room_name` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_bin',
        `club_room_name` VARCHAR(255) NOT NULL DEFAULT '\'\'' COLLATE 'utf8mb4_bin',
        `chang_flag` TINYINT(1) NULL DEFAULT '0',
        PRIMARY KEY (`id`)
    )
    COLLATE='utf8mb4_bin'
    ENGINE=MyISAM
    AUTO_INCREMENT=1;

    -- 牌局结算记录表 --
    drop table if exists `onethink_coco_import_game_end`;
    CREATE TABLE `onethink_coco_import_game_end` (
        `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
        `game_uid` VARCHAR(255) NOT NULL COMMENT '遊戲UID',
        `game_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'API遊戲局ID' COLLATE 'utf8mb4_bin',
        `board_id` VARCHAR(255) NULL DEFAULT '0' COMMENT 'api游戏局id',
        `end_game_time` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '遊戲結束時間',
        `apply_time` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '執行時間',
        `action` VARCHAR(255) NOT NULL COMMENT '結果',
        `settle_game_info` VARCHAR(255) NULL DEFAULT NULL COMMENT '汇入的战局唯一标志',
        PRIMARY KEY (`id`)
    )
    COLLATE='utf8_general_ci'
    ENGINE=InnoDB
    AUTO_INCREMENT=1;

### 1.2. 依赖环境安装配置  
#### 1.2.1. python模块  
    pip install PyMySQL xlrd socketIO-client-nexus
#### 1.2.2. nodejs  
#### 1.2.4. pm2  
    sudo npm install -g pm2  
#### 1.2.5. pm2 日志管理插件pm2-logrotate  
    pm2 install pm2-logrotate   

# 2. 配置管理  
### 2.1. config.py配置文件  
    对数据库及自动任务信息配置  
    * 自动任务名称,必须配置并且唯一  
    'name': 'bzl-provider',  
    * 在onethink上对应的业务code  
    'serviceCode': 4,  
    * 提供商接口地址  
    'apiUrl': 'https://yqdp-manager689125.gakuen.fun/api',  
    * 手动汇入文件地址配置项  
    'localDataPath': 'C:/workspace/cc/task/upload/'  
### 2.2. 入口文件配置  
    入口文件: ecosystem.config.js  
    * 需要对python程序位置进行配置  
    interpreter: 'C:/Python27/python.exe',  
    * 也可以修改程序运行后的进程名以便日后管理  
    name: 'dzpk-auto',  
    * 配置日志文件路径(插件会自动按拆分规则命名为out__2018-12-14_00-22-22.log格式)  
    output: './logs/out.log',  
    error: './logs/error.log',  
### 2.3. 日志配置管理  
    在命令行运行命令对日志插件参数进行配置  
    * 设置每个日志文件不超过1M  
    pm2 set pm2-logrotate:max_size 1M  
    * 设置按时间生成日志文件 (秒 分 时 天 月 [星期])(* 目前为按天分割)  
    pm2 set pm2-logrotate:rotateInterval '0 0 * * *'  

# 3. 启动及进程管理  
### 3.1. 首次启动程序  
    pm2 start  
    * 在项目根目录运行,pm2会自动寻找ecosystem.config.js文件并执行  
### 3.2. 停止进程  
    pm2 stop dzpk-auto  
    * dzpk-auto 为配置的进程名  
### 3.3. 再次启动已停止的进程  
    pm2 start dzpk-auto  
### 3.4. 直接重启正在执行中的进程  
    pm2 restart dzpk-auto  
### 3.5. 查看正在运行中的进程列表  
    pm2 list  
### 3.6. 查看进程当前日志  
    pm2 logs dzpk-auto  
### 3.7. 删除列表中的指定进程  
    pm2 delete dzpk-auto  

# 4. CMS当前战局
    入口文件: /CmsPortal.py
    函数名: getCurrentGameList
