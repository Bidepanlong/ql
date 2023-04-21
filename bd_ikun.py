"""

time：2023.4.21
cron: 23 0 * * *
new Env('ikun签到');
地址：https://ikuuu.eu/
抓包域名: https://ikuuu.eu/user/checkin
抓包请求头里面: cookie 的值全部复制到变量就行
环境变量 ikunck = cookie的值
多账号新建变量或者用 & 分开

"""

import time
import requests
from os import environ, path
from bs4 import BeautifulSoup


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


class Ikun():
    def __init__(self, ck):
        self.msg = ''
        self.ck = ck

    def sign(self):
        time.sleep(0.5)
        url = "https://ikuuu.eu/user/checkin"
        url1 = 'https://ikuuu.eu/user'

        headers = {
            'Cookie': self.ck,
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        }

        r = requests.post(url, headers=headers)
        time.sleep(0.5)
        r1 = requests.get(url1, headers=headers)
        try:
            soup = BeautifulSoup(r1.text, 'html.parser')
            bs = soup.find('span', {'class': 'counter'})
            syll = bs.text
            dl = soup.find('div', {'class': 'd-sm-none d-lg-inline-block'})
            name = dl.text
        except:
            xx = f"[登录]：请检查ck有效性：{self.ck}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

        if r.status_code != 200:
            xx = f"[登录]：{name}\n[签到]：请求失败，请检查网络或者ck有效性：{self.ck}\n\n"
            print(xx)
            self.msg += xx
            return self.msg
        try:
            if "已经签到" in r.json()['msg']:
                xx = f"[登录]：{name}\n[签到]：{r.json()['msg']}\n[流量]：{syll}GB\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            elif "获得" in r.json()['msg']:
                xx = f"[登录]：{name}\n[签到]：{r.json()['msg']}\n[流量]：{syll}GB\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            else:
                xx = f"[登录]：未知错误，请检查网络或者ck有效性：{self.ck}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
        except:
            xx = f"[登录]：解析响应失败，请检查网络或者ck有效性：{self.ck}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

    def get_sign_msg(self):
        return self.sign()


if __name__ == '__main__':
    token = get_environ("ikunck")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始ikun签到\n".format(len(cks)))
    for ck in cks:
        run = Ikun(ck)
        msg += run.get_sign_msg()
    if send:
        send("ikun签到通知", msg)


