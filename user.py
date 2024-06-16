import pyautogui
import pygetwindow as gw
from pygetwindow import PyGetWindowException
import asyncio
import time


class User:
    def __init__(self, accountName, lastStartTime):
        self.accountName = accountName
        self.lastStartTime = lastStartTime

    def __str__(self):
        return f"user: {self.accountName} \t last start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.lastStartTime))}"

    async def click_banana(self, click_time=10, loop_wait=1):
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
            except pyautogui.FailSafeException:
                pass
            finally:
                await asyncio.sleep(loop_wait)
