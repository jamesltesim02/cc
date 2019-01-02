#!/bin/python
# -*- coding: UTF-8 -*-

import time
import datetime
import base64
import traceback

def getTotoalBuyinAmount(cursor, pccid, beginTime, endTime, joinToken):
    sql = """
        select
            sum(join_cash) as totalAmount
        from
            onethink_coco_join_game_log
        where
            check_time between %s and %s
            and
            game_vid = %s
            and
            club_room_name = %s
            and
            check_status = 'accept'
    """
    cursor.execute(sql, (beginTime, endTime, pccid, joinToken))
    return cursor.fetchone()

def updatePurse(cursor, info, delta):
    timestamp = str(time.time())
    cash = int(info['cash'])+int(delta)
    sql = "update onethink_player_purse set cash=%s where id=%s"
    cursor.execute(sql, (str(cash), info['pp.id']))
    sql = """
        INSERT INTO `onethink_coco_auto_cash_log` (
            `username`,
            `cash`,
            `diamond`,
            `point`,
            `change_cash`,
            `change_diamond`,
            `change_point`,
            `apply_time`,
            `change_time`,
            `settle_game_info`
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    logInfo = (
        info['frontend_user_auth'],
        info['cash'],
        info['diamond'],
        info['point'],
        str(cash),
        info['diamond'],
        info['point'],
        timestamp,
        timestamp,
        info['settle_game_info']
    )

    print (sql, logInfo)

    cursor.execute(sql, logInfo)

def addSettleFailLog(cursor, data):
    querySQL = """
        select count(1) log_count
        from onethink_coco_import_game_end
        where settle_game_info = %s
    """
    cursor.execute(querySQL, data['settle_game_info'])
    result = cursor.fetchone()
    if result['log_count'] > 0:
        print('already loged')
        return

    sql = """
        insert into onethink_coco_import_game_end(
            game_uid,
            game_id,
            board_id,
            end_game_time,
            apply_time,
            action,
            settle_game_info
        )
        values(%s, %s,  %s, %s, %s, %s, %s)
    """
    cursor.execute(
        sql,
        (
            data['game_uid'],
            data['game_id'],
            data['board_id'],
            data['end_game_time'],
            data['apply_time'],
            data['action'],
            data['settle_game_info']
        )
    )

