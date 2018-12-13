# 1. 初始化  
### 1.1. 数据库更新脚本  
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

### 1.2. 依赖环境安装配置  
#### 1.2.1. python模块  
    pip install PyMySQL xlrd
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
