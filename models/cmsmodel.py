import base64
import time
import datetime

def saveGameinfo(conn, params):
  sql = """
          insert into onethink_historygamelist (
            `roomname`,
            `bigblind`,
            `createuser`,
            `gameroomtype`,
            `hands`,
            `iAnte`,
            `leagueid`,
            `maxplayer`,
            `players`,
            `roomid`,
            `smallblind`,
            `createtime`
          )
          values (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
          )
        """
  cursor = conn.cursor()
  cursor.execute(
    sql,
    (
      params['roomname'],
      str(params['bigblind']),
      params['createuser'],
      str(params['gameroomtype']),
      str(params['hands']),
      str(params['iAnte']),
      str(params['leagueid']),
      str(params['maxplayer']),
      str(params['players']),
      str(params['roomid']),
      str(params['smallblind']),
      str(divmod(params['createtime'], 1000)[0])
    )
  )

def getCountOfGameinfo(conn, params):
  sql = """
        select count(1) as game_count
        from onethink_historygamelist
        where roomid = %s and createtime = %s
        """
  with conn.cursor() as cursor:
    cursor.execute(
      sql,
      (
        params['roomid'],
        params['createtime']
      )
    )
    return cursor.fetchone()

def saveGameUserRecord(conn, params):
  sql = """
        INSERT INTO `onethink_historygamedetail` (
          `insuranceGetStacks`, 
          `info_id`, 
          `showId`, 
          `clubId`, 
          `bonus`, 
          `strCover`, 
          `strNick`, 
          `strSmallCover`, 
          `gameType`, 
          `clubName`, 
          `buyinStack`, 
          `fantseynum`, 
          `insuranceBuyStacks`, 
          `remainStack`, 
          `uuid`, 
          `insurance`, 
          `InsurancePremium`, 
          `endTime`, 
          `bz_username`, 
          `afbonus`, 
          `back`
        ) 
        VALUES (
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s,
          %s
        )
        """

  cursor = conn.cursor()
  cursor.execute(
    sql,
    (
      str(params['insuranceGetStacks']),
      params['roomid'],
      params['showId'],
      str(params['clubId']),
      str(params['bonus']),
      params['strCover'],
      params['strNick'],
      params['strSmallCover'],
      params['gameType'],
      params['clubName'],
      str(params['buyinStack']),
      str(params['fantseynum']),
      str(params['insuranceBuyStacks']),
      str(params['remainStack']),
      str(params['uuid']),
      str(params['insurance']),
      str(params['InsurancePremium']),
      str(time.mktime(datetime.datetime.strptime(params['endTime'], "%Y-%m-%d %H:%M:%S").timetuple())),
      str(params['username']),
      str(params['afbonus']),
      str(params['back'])
    )
  )

def getCountOfUser(conn, params):
  sql = """
        select count(1) as user_settle_count
        from onethink_historygamedetail
        where showId = %s and info_id = %s
        """
  with conn.cursor() as cursor:
    cursor.execute(
      sql,
      (
        params['showId'],
        params['roomid']
      )
    )
    return cursor.fetchone()

def getTotoalCmsBuyinAmount(conn, pccid, roomid, beginTime, endTime):
  with conn.cursor() as cursor:
    sql = """
      select
        sum(join_cash) as total_amount
      from
        onethink_cms_buyin_log
      where
        check_time between %s and %s
        and
        game_vid = %s
        and
        room_id = %s
        and
        check_status = 'accept'
    """

    cursor.execute(sql, (beginTime, endTime, pccid, roomid))
    return cursor.fetchone()

def getSpecialRake(conn, cloubId):
  sql = """
        SELECT * 
        FROM `onethink_cms_special_session_back` 
        WHERE `clubid` = %s
        """
  with conn.cursor() as cursor:
    cursor.execute(sql, cloubId)
    return cursor.fetchone()

def addSettleFailLog(conn, params):
	cursor = conn.cursor()
	sql = """
      insert into onethink_cms_game_end(
        game_uid,
        game_name,
        game_id,
        create_game_time,
        end_game_time,
        apply_time,
        action
      )
      values(%s, %s,  %s, %s, %s, %s)
	    """
	cursor.execute(
	    sql,
	    (
	      params['game_uid'],
	      params['game_name'],
	      params['game_id'],
	      params['create_game_time'],
	      params['end_game_time'],
	      params['apply_time'],
	      params['action']
		)
	)