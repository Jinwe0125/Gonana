import asyncio
import subprocess
import winreg
import pygetwindow as gw
import psutil
import vdf
from pygetwindow import PyGetWindowException


class SteamHelper:
    def __init__(self):
        self.steam_path = ""
        self.games = {}
        self.refresh_params()

    def refresh_params(self):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam') as key:
            # 子键、值，上次更新时间
            subkey_num, value_num, _ = winreg.QueryInfoKey(key)
            self.steam_path = {winreg.EnumValue(key, i)[0]: winreg.EnumValue(key, i)[1] for i in range(value_num)}.get(
                "SteamPath")
            with winreg.OpenKey(key, "Apps") as apps:
                apps_subkey_num, _, _ = winreg.QueryInfoKey(apps)
                apps_keys = [winreg.EnumKey(apps, i) for i in range(apps_subkey_num)]
                for app_key in apps_keys:
                    with winreg.OpenKey(apps, app_key) as app:
                        _, app_value_num, _ = winreg.QueryInfoKey(app)
                        app_values = {winreg.EnumValue(app, i)[0]: winreg.EnumValue(app, i)[1] for i in
                                      range(app_value_num)}
                        if app_values.get("Name") is not None:
                            self.games[app_values["Name"]] = app_key

    def get_running(self) -> list[str]:
        running = []
        for key, value in self.games.items():
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf'Software\Valve\Steam\Apps\{value}') as app:
                _, app_value_num, _ = winreg.QueryInfoKey(app)
                app_values = {winreg.EnumValue(app, i)[0]: winreg.EnumValue(app, i)[1] for i in
                              range(app_value_num)}
                if app_values.get("Running") == 1:
                    running.append(key)
        return running

    def run_game(self, game_id: str):
        if game_id not in self.games.values():
            return False
        if game_id not in self.get_running():
            subprocess.Popen([self.steam_path + '/steam.exe', '-applaunch', game_id])
        return True

    async def run_steam(self, accountName, loop_wait):
        subprocess.run(['taskkill', '/f', '/im', 'steam.exe'], capture_output=True, text=True)
        subprocess.run(['taskkill', '/f', '/im', 'SteamService.exe'], capture_output=True, text=True)
        subprocess.Popen([self.steam_path + '/steam.exe', '-login', accountName])
        # 登录steam后会启动九个进程
        while True:
            try:
                wd = gw.getWindowsWithTitle('Steam')[0]
                steam_procs = [proc.name() for proc in psutil.process_iter(['name']) if "steam" in proc.name()]
                if wd.title == 'Steam' and len(steam_procs) == 9:
                    await asyncio.sleep(3)
                    return f"{accountName} logged in."
            except PyGetWindowException:
                pass
            except  IndexError:
                pass
            finally:
                await asyncio.sleep(loop_wait)

    def get_users_account_name(self):
        with open(self.steam_path + '/config/loginusers.vdf', 'r', encoding="utf-8") as f:
            us = vdf.loads(f.read())

        return [v["AccountName"] for _, v in us["users"].items()]
