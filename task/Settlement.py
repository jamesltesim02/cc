# ALTER TABLE `onethink_auto_api_cash_log`
# 	ADD COLUMN `target_game` VARCHAR(255) NULL AFTER `change_time`;

class Settlement:
    def __init__(self, provider):
        self.provider = provider

    def aaa(self):
        data = self.provider.queryUserBoard({})
        print(data)