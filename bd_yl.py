"""

time：2023.10.31
cron: 1 1 1 1 1
new Env('安装依赖（运行脚本前运行）');
一键安装库里面脚本需要的依赖！

"""

import importlib.util
import os

yl = ['requests', 'bs4', 'user_agent']
for i in yl:
    spec = importlib.util.find_spec(i)
    if spec is None:
        os.system("pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple")
        os.system(f"pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {i}")
        print(f"{i}安装完成")
    else:
        print(f"{i}已经安装")
