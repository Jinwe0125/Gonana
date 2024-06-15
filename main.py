import asyncio
from user import Users
from config import check_config, config_watch, config_modified


async def init():
    config = check_config('config.json')
    users = Users(**config)
    watcher_task = asyncio.create_task(config_watch('.', config_modified,users))
    run_task = asyncio.create_task(users.run())

    try:
        await asyncio.gather(watcher_task, run_task)
    except KeyboardInterrupt:
        watcher_task.cancel()
        run_task.cancel()


if __name__ == '__main__':
    asyncio.run(init())
