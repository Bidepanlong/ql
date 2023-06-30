"""

time：2023.6.30
cron: 20 0 * * *
new Env('ikun签到');
地址：https://v2.zwtg888.com/auth/register?code=DTqz
环境变量 bd_ikun = 邮箱#密码
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
        self.cks = ""

    def qd(self):
        try:
            time.sleep(0.5)
            login_url = "https://v2.zwtg888.com/auth/login"
            login_headers = {
                'Host': 'v2.zwtg888.com',
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
                'sec-ch-ua-platform': '"Windows"',
                'origin': 'https://v2.zwtg888.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://v2.zwtg888.com/auth/login',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            }
            login_data = {
                'email': self.ck[0],
                'passwd': self.ck[1],
            }
            login_response = requests.post(login_url, headers=login_headers, data=login_data)
            if login_response.status_code == 200:
                if '成功' in login_response.json()['msg']:
                    xx = login_response.json()['msg']
                    print(xx)
                    self.msg += xx + '\n'
                    cookies = login_response.cookies
                    cookies_dict = cookies.get_dict()
                    for key, value in cookies_dict.items():
                        ck = f"{key}={value}"
                        self.cks += ck + ';'
                else:
                    xx = login_response.json()['msg']
                    print(xx)
                    self.msg += xx
                    send('ikun签到通知', self.msg)
                    exit(0)
            else:
                xx = f'登录出错 未知问题'
                print(xx)
                self.msg += xx
                send('ikun签到通知', self.msg)
                exit(0)

            checkin_url = 'https://v2.zwtg888.com/user/checkin'
            checkin_headers = {
                'Host': 'v2.zwtg888.com',
                'Cookie': self.cks,
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'x-requested-with': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
                'sec-ch-ua-platform': '"Windows"',
                'origin': 'https://v2.zwtg888.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://v2.zwtg888.com/user',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            time.sleep(0.5)
            checkin_r = requests.post(checkin_url, headers=checkin_headers)
            if checkin_r.status_code == 200:
                if '获得' in checkin_r.json()['msg']:
                    xx = f"{checkin_r.json()['msg']}\n剩余流量：{checkin_r.json()['traffic']}"
                    print(xx)
                    self.msg += xx + '\n'
                    send('ikun签到通知', self.msg)
                elif "已经" in checkin_r.json()['msg']:
                    xx = f"{checkin_r.json()['msg']}"
                    print(xx)
                    self.msg += xx + '\n'
                    send('ikun签到通知', self.msg)
                else:
                    xx = f'签到出错'
                    print(xx)
                    self.msg += xx + '\n'
                    send('ikun签到通知', self.msg)
                    exit(0)
            else:
                xx = f'签到出错'
                print(xx)
                self.msg += xx
                send('ikun签到通知', self.msg)
                exit(0)

        except Exception as e:
            print(f'请求异常：{e}')


if __name__ == '__main__':
    ep = get_environ("bd_ikun")
    cks = ep.split("&")
    print("检测到{}个ck记录\n开始ikun签到\n暂时只写了签到。还没写剩余流量多少和其他信息，下次一定!\n".format(len(cks)))
    for ck_all in cks:
        ck = ck_all.split("#")
        run = Ikun(ck)
        run.qd()
