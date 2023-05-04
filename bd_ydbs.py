"""

time：2023.5.4
cron: 23 12 * * *
new Env('运动步数');
小米运动(Zepp Life)注册的账号，旧账户不行就新注册，随便邮箱，绑定wx
环境变量 ydbsck = 账号#密码
多账号新建变量或者用 & 分开

"""

import time
import requests
from os import environ, path
import random


# 读取通知
def load_send():
    global send
    cur_path = path.abspath(path.dirname(__file__))
    if path.exists(cur_path + "/SendNotify.py"):
        try:
            from SendNotify import send
            print("加载通知服务成功！")
        except:
            send = False
            print(
                '''加载通知服务失败~\n请使用以下拉库地址\nql repo https://github.com/Bidepanlong/ql.git "bd_" "README" "SendNotify"''')
    else:
        send = False
        print(
            '''加载通知服务失败~\n请使用以下拉库地址\nql repo https://github.com/Bidepanlong/ql.git "bd_" "README" "SendNotify"''')


load_send()


# 获取环境变量
def get_environ(key, default="", output=True):
    def no_read():
        if output:
            print(f"未填写环境变量 {key} 请添加")
            exit(0)
        return default

    return environ.get(key) if environ.get(key) else no_read()


class Ydbs():
    def __init__(self, user, psw):
        self.msg = ''
        self.user = user
        self.psw = psw

    def sign(self):
        time.sleep(0.5)
        step = str(random.randint(20000, 30000))
        url = "https://apis.jxcxin.cn/api/mi?user=" + self.user + "&password=" + self.psw + "&step=" + step
        r = requests.get(url)
        if r.status_code != 200:
            xx = f"[登录]：{self.user}\n[步数]：{step}\n[提交]：请求失败，{r.json()['msg']}\n\n"
            print(xx)
            self.msg += xx
            return self.msg
        try:
            if r.json()['code'] == 200:
                xx = f"[登录]：{self.user}\n[步数]：{step}\n[提交]:{r.json()['msg']}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            else:
                xx = f"[登录]：{self.user}\n[步数]：{step}\n[提交]:{r.json()['msg']}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
        except:
            xx = f"[登录]：解析响应失败，请检查网络\n\n"
            print(xx)
            self.msg += xx
            return self.msg

    def get_sign_msg(self):
        return self.sign()


if __name__ == '__main__':
    token = get_environ("ydbsck")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始刷步数\n".format(len(cks)))
    for ck in cks:
        c = ck.split('&')
        for i in c:
            d = i.split('#')
        try:
            run = Ydbs(d[0], d[1])
            msg += run.get_sign_msg()
        except KeyError:
            print("请检查ck是否正确")
            print()
    if send:
        send("刷步数通知", msg)
