"""

time：2023.7.8
cron: 23 0 * * *
new Env('ikuuu签到');
地址：https://ikuuu.art/
环境变量 bd_ikuuu = 邮箱#密码
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


class ikuuu():
    def __init__(self, ck):
        self.msg = ''
        self.ck = ck
        self.cks = ""

    def sign(self):
        time.sleep(0.5)
        url = "https://ikuuu.art/user/checkin"
        url1 = 'https://ikuuu.art/user'
        login_url = 'https://ikuuu.art/auth/login'

        login_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        data = {
            'email': self.ck[0],
            'passwd': self.ck[1],
        }
        response = requests.post(login_url, headers=login_header, data=data)
        cookies = response.cookies
        cookies_dict = cookies.get_dict()
        for key, value in cookies_dict.items():
            ck = f"{key}={value}"
            self.cks += ck + ';'

        headers = {
            'Cookie': self.cks,
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        }
        time.sleep(0.5)
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
    token = get_environ("bd_ikuuu")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始ikuuu签到\n".format(len(cks)))
    for ck_all in cks:
        ck = ck_all.split("#")
        run = ikuuu(ck)
        msg += run.get_sign_msg()
    if send:
        send("ikuuu签到通知", msg)
