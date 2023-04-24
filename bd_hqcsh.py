"""

time：2023.4.24
cron: 0 9,18 * * *
new Env('好奇车生活签到');
微信小程序-好汽车生活-好物兑换
抓包域名: https://channel.cheryfs.cn/
抓包请求头里面: accountId 的值
环境变量名称：hqcshck = accountId 的值
多账号新建变量或者用 & 分开

"""

import time
import requests
from os import environ, path


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


def get_environ(key, default="", output=True):
    def no_read():
        if output:
            print(f"未填写环境变量 {key} 请添加")
            exit(0)
        return default

    return environ.get(key) if environ.get(key) else no_read()


class Hqcsh():
    def __init__(self, ck):
        self.msg = ''
        self.ck = ck
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6763'
        self.tid = '619669306447261696'

    def sign(self):
        time.sleep(0.5)
        sign_url = "https://channel.cheryfs.cn/archer/activity-api/signinact/signin"
        jf_url = 'https://channel.cheryfs.cn/archer/activity-api/common/accountPointLeft?pointId=620415610219683840'

        sign_headers = {
            'User-Agent': self.ua,
            'tenantId': self.tid,
            'activityId': '620810406813786113',
            'accountId': self.ck,
        }

        jf_headers = {
            'User-Agent': self.ua,
            'tenantId': self.tid,
            'activityId': '621911913692942337',
            'accountId': self.ck,
        }

        try:
            sign_rsp = requests.get(sign_url, headers=sign_headers)
            time.sleep(0.5)
            jf_rsp = requests.get(jf_url, headers=jf_headers)
            if sign_rsp.json()['success'] == True:
                if sign_rsp.json()['result']['success'] == True:
                    xx = f"[登录]：账号{a}登录成功\n[签到]：签到成功\n[积分]：{jf_rsp.json()['result']}\n\n"
                    print(xx)
                    self.msg += xx
                elif sign_rsp.json()['result']['success'] == False:
                    xx = f"[登录]：账号{a}登录成功\n[签到]：{sign_rsp.json()['result']['message']}\n[积分]：{jf_rsp.json()['result']}\n\n"
                    print(xx)
                    self.msg += xx
            elif sign_rsp.json()['success'] == False:
                xx = f"[登录]：账号{a}登录失败，请稍后重试或者ck可能失效,当前ck：{self.ck}\n\n"
                print(xx)
                self.msg += xx
            else:
                xx = f"[登录]：账号{a}登录失败，请稍后重试或者ck可能失效,当前ck：{self.ck}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            return self.msg
        except Exception as e:
            xx = f"[请求异常]：{e}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

    def get_sign_msg(self):
        return self.sign()


if __name__ == '__main__':
    token = get_environ("hqcshck")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始Hqcsh签到\n".format(len(cks)))
    a = 0
    for ck in cks:
        a += 1
        run = Hqcsh(ck)
        msg += run.get_sign_msg()
    if send:
        send("好奇车生活签到通知", msg)
