#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 接口提供商接口, 用于规范提供商函数
# 不同的供应商应有具体实现
# 不允许直接使用提供商接口对象使用
# 也不应直接创建provider对象使用
# 应使用ProviderFactory中的createProvider创建provider对象使用
class ProviderInterface:

    def __init__(self):
        raise '不允许直接对ProviderInterface创建对象,请使用具体提供商实现类'

    def getBuyin(self):
        """
        获取待审批提案列表

        Returns:
            buyinList 提案列表
                [
                    {
                        "status": 0,   状态(等待处理 已处理)
                        "acc_id": 14632, 玩家编号
                        "agent_balance": 119916, 代理余额(不需要理会)
                        "pccname": "\u6d9bs", "total_buyin": 38600, 德扑暱称 
                        "room_uuid": 31944804,  房间编号
                        "club_name": "\ud83c\udf0a\u9ed1\u6843\u4ff1\u4e50\u90e8",  俱乐部名称
                        "room_name": "248\u266668\u965025",  房间名称(牌局名)
                        "stack": 800,    
                        "amounts": 800, 要求买入金额
                        "firstagent_balance": 119916, 总代理余额(不需要理会)
                        "acc_ps": null,  会员注解(不需要理会)
                        "pccid": "2639477333", 会员德扑ID
                        "rake_amounts": 800,   加权后的买入金额(不需要理会)
                        "suggest": 0, 建议(可买入 不可买入)(不需要理会)
                        "balance": 50524, 余额 (不需要理会)
                        "user_uuid": 1088802, (不需要理会)
                        "firstagent_ps": "",  (不需要理会)
                        "total_result": null, (不需要理会)
                        "operat": 1           (不需要理会)
                    }
                ]
        """

        raise 'getBuyin必须在实现类中重写实现'

    def acceptBuyin(self):
        """
        通过提案

        Args:
            params: 通过的提案信息
                {
                    club_name 俱乐部名称 string
                    pccid     俱乐部ID string
                    pccname   玩家德扑暱称 string
                    room_uuid 房间编号 string
                    amounts   买入金额 int 由/api/club_buyin
                }
        """

        raise 'acceptBuyin必须在实现类中重写实现'

    def denyBuyin(self):
        """
        拒绝提案

        Args:
            params: 拒绝的提案信息
                {
                    club_name 俱乐部名称 string
                    pccid     俱乐部ID string
                    pccname   玩家德扑暱称 string
                    room_uuid 房间编号 string
                    amounts   买入金额 int 由/api/club_buyin
                }
        """

        raise 'denyBuyin必须在实现类中重写实现'

    def getHistoryGameDetails(self):
        """
        查询战绩

        Args:
            params: 过滤时间条件
                {
                    startdate 开始时间
                    enddate   结束时间
                }
        """

        raise 'getHistoryGameDetails必须在实现类中重写实现'
