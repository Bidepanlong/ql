"""

time：2023.5.7
cron: 2 0,12 * * *
new Env('歌画东阳');
地址：https://app.tmuyun.com/webChannels/invite?inviteCode=BRHAB9&tenantId=49&accountId=6448adf9c790b07c90ca2591
进入app-我的-抢红包或者在我的红包界面抓包
提前在我的钱包里面绑定zfb号
抓包域名: fijdzpur.act.tmuact.com 或者 wallet.act.tmuact.com
抓包请求体里面: account_id和session_id的值
环境变量名称：ghdyck = account_id的值#session_id的值  注：用'#'号分开两个参数，顺序不要乱，先是account_id的值然后session_id的值
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


class Ghdy():
    def __init__(self, ck):
        self.msg = ''
        self.ck = ck
        self.ua = 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36;xsb_dongyang;xsb_dongyang;5.0.7.0.0;native_app'
        self.m = 'front'

    def sign(self):
        time.sleep(0.5)
        tx_url = "https://wallet.act.tmuact.com/activity/api.php"
        q_url = "https://fijdzpur.act.tmuact.com/activity/api.php"

        h = {
            "User-Agent": self.ua
        }
        sgin_data = {
            'm': self.m,
            'subm': 'money_wallet',
            'action': 'commongetmoneyinit',
            'account_id': self.ck[0],
            'session_id': self.ck[1],
            'app': 'XSB_DONGYANG',
        }

        q_data = {
            "m": self.m,
            "subm": "money",
            "action": "open",
            'account_id': self.ck[0],
            'session_id': self.ck[1],
            "token": "",
            "q": "YunSLfjZu",
        }

        tx_data = {
            'm': self.m,
            'subm': 'money_wallet',
            'action': 'commonchange',
            'account_id': self.ck[0],
            'session_id': self.ck[1],
            'app': 'XSB_DONGYANG',
        }
        try:
            q_rsp = requests.post(q_url, headers=h, data=q_data)
            time.sleep(0.5)
            sign_rsp = requests.post(tx_url, headers=h, data=sgin_data)
            time.sleep(3)
            tx_rsp = requests.post(tx_url, headers=h, data=tx_data)
            if sign_rsp.json()['status'] == True:
                zfb = sign_rsp.json()['data']['zfb']
                ye = sign_rsp.json()['data']['can_get']
                if q_rsp.json()['status'] == True:
                    je = q_rsp.json()['data']['name']
                    if tx_rsp.json()['status'] == True:
                        xx = f"[登录]：{zfb}\n[红包]：获得{je}元\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                    elif tx_rsp.json()['status'] == False:
                        xx = f"[登录]：{zfb}\n[红包]：获得{je}元\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                    else:
                        xx = f"[登录]：{zfb}\n[红包]：获得{je}元\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                elif q_rsp.json()['status'] == False:
                    if tx_rsp.json()['status'] == True:
                        xx = f"[登录]：{zfb}\n[红包]：{q_rsp.json()['msg']}\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                    elif tx_rsp.json()['status'] == False:
                        xx = f"[登录]：{zfb}\n[红包]：{q_rsp.json()['msg']}\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                    else:
                        xx = f"[登录]：{zfb}\n[红包]：{q_rsp.json()['msg']}\n[余额]：{ye}\n[提现]：{tx_rsp.json()['msg']}\n\n"
                        print(xx)
                        self.msg += xx
                else:
                    xx = f"[登录]：登录异常，请稍后重试或者ck可能失效,当前ck：{self.ck}\n\n"
                    print(xx)
                    self.msg += xx
            elif sign_rsp.json()['status'] == False:
                xx = f"[登录]：登录失败，请稍后重试或者ck可能失效,当前ck：{self.ck}\n\n"
                print(xx)
                self.msg += xx
            else:
                xx = f"[登录]：登录异常，请稍后重试或者ck可能失效,当前ck：{self.ck}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            return self.msg
        except Exception as e:
            xx = f"[请求异常]：稍后再试\n{e}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

    def get_sign_msg(self):
        return self.sign()


if __name__ == '__main__':
    token = get_environ("ghdyck")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始歌画东阳抢红包\n".format(len(cks)))
    for ck_all in cks:
        ck = ck_all.split("#")
        run = Ghdy(ck)
        msg += run.get_sign_msg()
    if send:
        send("歌画东阳通知", msg)
