#!/usr/bin/python
# -*- coding: UTF-8 -*-

from providers import ProviderFactory
from models import purse,conn,buyin

# print purse.getBuyin('11', '11')
# conn.close()
# exit(0)
cp = ProviderFactory.createProvider({
    'name': 'common-provider',
    'description': '通用提供商',
    'module': 'providers.implements.CommonProvider',
    'className': 'CommonProvider',
    'username': 'controller12',
    'password': '5589',
    'loginApi': 'https://yqdp-manager689125.gakuen.fun/api/login_admin',
    'buyinApi': 'https://yqdp-manager689125.gakuen.fun/api/club_buyin',
    'acceptApi': 'https://vnt-ceo861.strong.zone/api/control_cms/accept_buy',
    'denyApi': 'https://vnt-ceo861.strong.zone/api/control_cms/deny_buy',
    'gameDetailsApi': 'http://api.bzpk44.com/index.php?c=export'
})
list =  cp.getBuyin()
for item in list:
    if ['suggest']) > -2:
        purseInfo = purse.getPurseInfoByGameId(item['pccid'])
        if purseInfo:
            data = {
                'club_name':item["club_name"], 
                'pccid':item["pccid"],
                'pccname':item["pccname"],
                'room_uuid':item["room_uuid"],
                'stack':item["stack"],
                'amounts':item["amounts"]
            }
            if int(purseInfo['cash']) >= int(item['amounts']):
                code = cp.acceptBuyin(data)
                if code == 200:              
                    try:
                        buyin.addBuyinLog(purseInfo, item, 'accept')
                        purse.updatePurse(purseInfo, -int(item['amounts']))
                        conn.commit()
                    finally:
                        conn.rollback()
                        if get_user_purse_info:

                            # if DEBUG_FLAG == 1:
                            #   print get_purse_sql
                            #   print run_mysql(get_purse_sql)
                            #   print get_user_purse_info[0]["cash"]
                            #   print buyin_data['data'][x]["amounts"]      

                            if int(get_user_purse_info[0]["cash"]) >= int(buyin_data['data'][x]["amounts"]):

                                if DEBUG_FLAG > 0:
                                    print "accept_buy"

                                # # post accept 
                                # accept_response =  accept_buy(data,post_response)

                                # if DEBUG_FLAG > 0:
                                    # print accept_response
                                
                                if accept_response == 200:
                                    # add buyin log
                                    add_buyin_log(get_user_purse_info[0], buyin_data['data'][x], "accept")

                                    # update purse
                                    update_purse(get_user_purse_info, buyin_data['data'][x])

                                    # add purse change log
                                    add_purse_change_log(get_user_purse_info, buyin_data['data'][x])


                                
                            else:
                                if DEBUG_FLAG > 0:
                                    print "deny_buy"

                                # post deny
                                # deny_response = deny_buy(data,post_response)

                                if deny_response == 200:
                                    # add buyin log 
                                    add_buyin_log(get_user_purse_info[0], buyin_data['data'][x], "deny")

                        else:
                                if DEBUG_FLAG > 0:
                                    print "deny_buy"

                                # post deny
                                deny_response = deny_buy(data,post_response)

                                # print deny_response

                                if deny_response == 200:
                                # add buyin log 
                                    get_user_purse_info = {}
                                    get_user_purse_info['frontend_user_id'] = 'no purse'
                                    get_user_purse_info['frontend_user_auth'] = 'no purse'
                                    get_user_purse_info['game_vid'] = buyin_data['data'][x]["pccid"]
                                    
                                    add_buyin_log(get_user_purse_info, buyin_data['data'][x], "deny")
    print item
# cp.getHistoryGameDetails({'startdate':'2018-12-01', 'enddate':'2018-12-09'})