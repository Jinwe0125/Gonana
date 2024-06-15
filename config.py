import asyncio
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json


class ConfigHandler(FileSystemEventHandler):
    def __init__(self, loop, callback, users):
        self.loop = loop
        self.callback = callback
        self.users = users

    def on_modified(self, event):
        if "config.json" in event.src_path and '~' not in event.src_path:
            asyncio.run_coroutine_threadsafe(self.callback(event.src_path, self.users), self.loop)


async def config_watch(path, callback, users):
    loop = asyncio.get_event_loop()
    event_handler = ConfigHandler(loop, callback, users)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        observer.stop()
    observer.join()


async def main():
    path_to_watch = '.'
    watcher_task = asyncio.create_task(config_watch(path_to_watch, config_modified))
    try:
        await watcher_task
    except KeyboardInterrupt:
        watcher_task.cancel()
        await watcher_task


async def config_modified(path, users):
    config = read_config(path)
    await users.update_config(config)


def read_config(path):
    with open(path, 'r') as file:
        config = json.load(file)
    config["users_path"] = config["steam_root_path"] + "\\config\\loginusers.vdf"
    config["steam_path"] = config["steam_root_path"] + "\\steam.exe"
    return config


def check_config(filename):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, filename)
    if not os.path.exists(file_path):
        steam_path = input("please enter your steam root path: ")
        banana_path = input("please enter your banana path: ")
        with open('./config.json', 'w') as file:
            file.write(json.dumps(
                {"steam_root_path": steam_path, "banana_path": banana_path, "gap_time": 3600, "click_time": 10,
                 "loop_wait_time": 1}, indent=4, ensure_ascii=False))
    return read_config('./config.json')


