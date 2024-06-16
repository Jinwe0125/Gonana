import asyncio
import time
from user import User
from utils import SteamHelper


class Script:
    def __init__(self, **kwargs):
        self.config = kwargs
        self.steam_helper = SteamHelper()
        self.event = asyncio.Event()
        self.users = None
        self.event.set()
        self.refresh_users()

    def __str__(self):

        return '\n'.join([
            str(v) + f"\t remaining time:{time.strftime(' %H:%M:%S', time.gmtime(self.config['gap_time'] + v.lastStartTime - time.time()))}"
            for _, v in self.users.items()]) + '\n' + '-' * 100

    async def update_config(self, config):
        self.event.clear()
        self.config = config

        self.refresh_users()
        self.event.set()

    def refresh_users(self):
        account_names = self.steam_helper.get_users_account_name()
        if self.users is None:
            self.users = {n: User(n, time.time()) for n in account_names}
            return
        for n in [n for n in account_names if n not in self.users.copy().keys()]:
            self.users[n] = User(n, time.time())

    async def run(self):
        while True:
            for k, v in self.users.items():
                await self.event.wait()
                await asyncio.sleep(self.config["loop_wait_time"])
                if time.time() - v.lastStartTime >= self.config["gap_time"]:
                    await self.steam_helper.run_steam(k, self.config["loop_wait_time"])
                    # Banana steamid: '2923300'
                    if not self.steam_helper.run_game('2923300'):
                        continue
                    print(await v.click_banana(self.config["click_time"],self.config["loop_wait_time"]))
                print(self.__str__())
