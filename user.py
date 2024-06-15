import subprocess
import pyautogui
import pygetwindow as gw
from pygetwindow import PyGetWindowException
import asyncio
import vdf
import time
import psutil


class User:
    def __init__(self, accountName, lastStartTime):
        self.accountName = accountName
        self.lastStartTime = lastStartTime

    def __str__(self):
        return f"user: {self.accountName} \t last start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.lastStartTime))}"

    async def run_steam(self, path, loop_wait=1):
        subprocess.run(['taskkill', '/f', '/im', 'steam.exe'], capture_output=True, text=True)
        subprocess.run(['taskkill', '/f', '/im', 'SteamService.exe'], capture_output=True, text=True)
        await asyncio.sleep(loop_wait)
        subprocess.Popen([path, '-login', self.accountName])
        # 登录steam后会启动九个进程
        while True:
            try:
                wd = gw.getWindowsWithTitle('Steam')[0]
                steam_procs = [proc.name() for proc in psutil.process_iter(['name']) if "steam" in proc.name()]
                if wd.title == 'Steam' and len(steam_procs) == 9:
                    await asyncio.sleep(3)
                    return f"{self.accountName} logged in."
            except PyGetWindowException:
                pass
            except  IndexError:
                pass
            finally:
                await asyncio.sleep(loop_wait)

    async def run_banana(self, path, click_time=10, loop_wait=1):
        subprocess.Popen([path])
        while True:
            try:
                wd = gw.getWindowsWithTitle('Banana')[0]
                self.lastStartTime = time.time()
                while time.time() - self.lastStartTime < click_time:
                    wd.activate()
                    window_left = wd.left
                    window_top = wd.top
                    window_width = wd.width
                    window_height = wd.height
                    pyautogui.click(window_left + window_width / 2, window_top + window_height / 2)
                wd.close()
                self.lastStartTime = time.time()
                await asyncio.sleep(3)
                return f"{self.accountName} Banana clicked."
            except IndexError:
                pass
            except PyGetWindowException:
                pass
            finally:
                await asyncio.sleep(loop_wait)


class Users:
    def __init__(self, **kwargs):

        self.config = kwargs
        self.event = asyncio.Event()
        self.users = self.get_users()
        self.event.set()

    def __str__(self):
        return '\n'.join([
            str(v) + f"\t remaining time:{time.strftime(' %H:%M:%S', time.gmtime(self.config['gap_time'] + v.lastStartTime - time.time()))}"
            for _, v in self.users.items()]) + '\n' + '-' * 100

    async def update_config(self, config):
        self.event.clear()
        self.config = config
        self.users = self.get_users()
        self.event.set()

    def get_users(self):
        users = {}
        with open(self.config['users_path'], 'r', encoding="utf-8") as f:
            us = f.read()
        us = vdf.loads(us)
        for k, v in us["users"].items():
            users[v["AccountName"]] = User(v["AccountName"], time.time())
        return users

    async def run(self):
        while True:
            for k, v in self.users.items():
                await self.event.wait()
                await asyncio.sleep(self.config["loop_wait_time"])
                if time.time() - v.lastStartTime >= self.config["gap_time"]:
                    print(await v.run_steam(self.config["steam_path"], self.config["loop_wait_time"]))
                    print(await v.run_banana(self.config["banana_path"], self.config["click_time"],
                                             self.config["loop_wait_time"]))
                print(self.__str__())


# 检测csgo
async def check_csgo():
    while "cs2.exe".lower() in [proc.name().lower() for proc in psutil.process_iter(['name'])]:
        print("cs2.exe is running！pause")
        await asyncio.sleep(1)
