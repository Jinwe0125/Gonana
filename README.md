Gonana 是一个用于Banana游戏的挂机脚本。实现多账户切换的 Gonana 可以轻松完成多个账户的挂机任务，
同时可以指定启动Banana的间隔时间，而不是常驻后台。
# Usage
首次运行会在项目目录下生成config.json文件，并且脚本开始运行。
在程序运行时可以通过修改config.json文件控制启动Banana的间隔启动时间等，例如:
```text
"gap_time": 3600,
"click_time": 10,
"loop_wait_time": 1
```
当然，也可以在程序运行时添加新的用户。只需要在登录steam时点击自动登录，并确保用户信息
已经写入 steam_root_path\config\loginusers.vdf。之后修改一次config.json 文件就可以完成新用户的添加。

