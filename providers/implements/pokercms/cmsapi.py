#! /usr/bin/env python
# coding=utf-8

import requests
from cryptor import rsacrypt
from poker import captcha as capcracker
import json
import os

domain = 'http://cms.pokermanager.club'
base_url = domain + '/cms-api/'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
headers = {
    # 'Referer': domain + '/cms-web/cmsLogin.html',
    # 'Origin': domain,
    'User-Agent': user_agent
  }
tempfile_path = os.path.dirname(os.path.realpath(__file__)) + '/temp/tokenandcookie.text'

# 获取验证码
def getCaptcha():
  # 获取token
  token_result = requests.post(base_url + 'token/generateCaptchaToken')
  token = token_result.json()['result']
  # cookie
  cookie = token_result.cookies.get_dict()
  
  # 请求验证码
  captcha_result = requests.post(
      base_url + 'captcha',
      data = {
        'token': token
      },
      headers = headers,
      cookies = cookie
    )
  captcha = captcha_result.json()['result']
  
  return token, captcha, cookie

# 登录
def login(username, password):
  # 获取验证码
  token, captcha, cookie = getCaptcha()
  # 识别验证码
  safeCode = capcracker.crack(captcha)
  # 加密账号密码
  reqData = rsacrypt.info_crypt(token, username, password)

  # 请求参数
  data = {
      'token': token,
      'data': reqData,
      'safeCode': safeCode,
      'locale': 'zh'
    }

  # 请求登录
  result = requests.post(
      base_url + 'login',
      data = data,
      headers = headers,
      cookies = cookie
    ).json()

  if result['iErrCode'] == 0:
    tempfile = open(tempfile_path, 'w+')
    tempfile.write(json.dumps({
      'token': result['result'],
      'cookie': cookie
    }))
    tempfile.close()
    return
  
  if result['iErrCode'] == 1103:
    login(username, password)
    return

  raise Exception(json.dumps(result))

# 调用接口封装
def invoke_api(api, username, password, params={}):
  if os.path.exists(tempfile_path) == False:
    login(username, password)

  tempfile = open(tempfile_path, 'r')
  tcinfo = json.loads(tempfile.read())
  
  result = requests.post(
      base_url + api,
      data = params,
      headers = {
        'Referer': domain + '/cms-web/cmsLogin.html',
        'Origin': domain,
        'User-Agent': user_agent,
        'token': tcinfo['token']
      },
      cookies = tcinfo['cookie']
    ).json()

  if result['iErrCode'] == 1000:
    login(username, password)
    return invoke_api(api, username, password, params)

  return result

# 查询俱乐部列表
def getClubList(username, password):
  return invoke_api('club/getClubList', username, password)

# 查询当前牌局
def getCurrentGameList(username, password, club_id):
  # 切换俱乐部
  invoke_api('club/clubInfo', username, password, params={'clubId': club_id})
  # 查询提案
  return invoke_api('game/getCurrentGameList', username, password)

# 查询牌局详情
def getGameDetail(username, password, club_id, room_id):
  # 切换俱乐部
  invoke_api('club/clubInfo', username, password, params={'clubId': club_id})
  return invoke_api(
    'game/getGameDetail',
    username,
    password,
    {
      'roomId': room_id,
      'sort': 2
    }
  )

# 查询提案列表
def getBuyinList(username, password, club_id):
  # 切换俱乐部
  invoke_api('club/clubInfo', username, password, params={'clubId': club_id})
  # 查询提案
  return invoke_api('game/getBuyinList', username, password)

# 接受提案
def acceptBuyin(username, password, user_uuid, room_id):
  return invoke_api(
    'game/acceptBuyin',
    username,
    password,
    {
      'userUuid': user_uuid,
      'roomId': room_id
    }
  )

# 拒绝提案
def denyBuyin(username, password, user_uuid, room_id):
  return invoke_api(
    'game/denyBuyin', username, password, {
    'userUuid': user_uuid,
    'roomId': room_id
  })

# 查询牌局列表
def getHistoryGameList(username, password, club_id, start_time, end_time):
  return invoke_api(
    'game/getHistoryGameList',
    username,
    password,
    {
      'clubId': club_id,
      'startTime': start_time,
      'endTime': end_time,
      'keyword': '',
      'order': -1,
      'gameType': 1,
      'pageSize': 1000,
      'pageNumber': 1
    }
  )

# 查询战绩
def getHistoryGameDetail(username, password, room_id):
  return invoke_api(
    'game/getHistoryGameDetail',
    username,
    password,
    {
      'roomId': room_id
    }
  )

if __name__ == '__main__':
  username, password = '18206774149', 'aa8888'

  # 查询俱乐部列表
  # result = getClubList(username, password)
  # 查询当前牌局列表
  # result = getCurrentGameList(username, password, 588000)
  # 查询牌局明细
  # result = getGameDetail(username, password, 588000, 33680918)
  # 查询带入提案
  # result = getBuyinList(username, password, 588000)
  # 接受提案
  # result = acceptBuyin(username, password, 691598, 33515925)
  # 拒绝提案
  # result = denyBuyin(username, password, 1575516, 33530967)
  # 查询历史牌局列表
  #result = getHistoryGameList(username, password, 588000, 1538323200000, 1540396800000)
  # 查询战绩
  # result = getHistoryGameDetail(username, password, 33484968)
  
  # print(result)

  # 查询俱乐部列表
  # clubs = getClubList(username, password)['result']
  # 假装有一个定时任务,每次都会查询所有俱乐部的提案
  # for c in clubs:
  #   transfer_reqs = getBuyinList(username, password, c['lClubID'])
  #   print(transfer_reqs)