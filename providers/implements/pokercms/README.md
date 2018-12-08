# poker-cms
### 1. 依赖模块
    pip install requests PyExecJS pillow

### 3. 接口调用
    from pokercms import cmsapi
    # 查询俱乐部列表
    result = cmsapi.getClubList(username, password)
    # 查询当前牌局列表
    result = cmsapi.getCurrentGameList(username, password, club_id)
    # 查询牌局明细
    result = getGameDetail(username, password, club_id, room_id)
    # 查询带入提案
    result = cmsapi.getBuyinList(username, password, club_id)
    # 接受提案
    result = cmsapi.acceptBuyin(username, password, user_uuid, room_id)
    # 拒绝提案
    result = cmsapi.denyBuyin(username, password, user_uuid, room_id)
    # 查询牌局列表
    result = getHistoryGameList(username, password, club_id, start_time, end_time)
    # 查询战绩
    result = cmsapi.getHistoryGameDetail(username, password, room_id)
