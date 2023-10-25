"""

time：2023.10.25
cron: 1 1 1 1 1
new Env('安装依赖');
一键安装库里面脚本需要的依赖！

"""

import importlib.util
import os

yl = ['requests', 'bs4', 'user_agent']
for i in yl:
    spec = importlib.util.find_spec(i)
    if spec is None:
        # 如果找不到request库，则安装
        os.system("pip install --upgrade pip")
        os.system(f"pip install -r yl.txt -i https://pypi.tuna.tsinghua.edu.cn/simple {i}")
        print(f"{i}安装完成")
    else:
        # 如果已经安装，打印消息
        print(f"{i}已经安装")
