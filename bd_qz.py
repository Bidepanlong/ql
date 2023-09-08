"""

time：2023.9.8
cron: 12 7,17 * * *
new Env('泉站签到');
每日签到0.2 满1元自动提现
微信小程序-泉站大桶XXXXX
抓包域名: admin.dtds888.com  请求体里面的tokne
环境变量: bd_qz = token的值
多账号新建变量或者用 & 分开

"""


import requests
from datetime import datetime
from SendNotify import send
import os



class Shui:
    def __init__(self, ck):
        self.token = ck  # 账号的token
        self.name = None  # 用户名字
        self.ye = None  # 余额
        self.ts = None  # 时间戳
        self.msg = '' # 推送消息
        # 请求头
        self.headers = {
            "Host": "admin.dtds888.com",
            "Connection": "keep-alive",
            "Content-Length": "505",
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5235 MMWEBSDK/20230701 MMWEBID/9516 MicroMessenger/8.0.40.2420(0x28002855) WeChat/arm64 Weixin NetType/3gnet Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            "content-type": "application/json",
            "Accept-Encoding": "gzip, compress, br, deflate",
            "Referer": "https://servicewechat.com/wxcee27346cf362ba6/24/page-frame.html"
        }
        # 请全体
        self.data = {
            'deviceType': 'wxapp',
            'timestamp': self.ts,
            'noncestr': '',
            'token': self.token,
            'sign': '',
            'version': 1.00
        }

    def login(self):
        """登录获取用户信息"""
        try:
            # 设置当前时间戳
            self.ts = int(datetime.now().timestamp())

            # 请求用户信息的url
            url = "https://admin.dtds888.com/api/index/user/index"

            # 请求
            response = requests.post(url, headers=self.headers, json=self.data)

            # 获取请求返回的响应
            if response.status_code == 200:
                # 获取用户昵称
                name = response.json()['data']['user']['user_nickname']
                self.name = name
                xx = f'{self.name}: 登录成功！'
                print(xx)
                self.msg += xx + '\n'
                # 获取余额
                return True
            else:
                print(f'登录失败')
                print(response.json())
                return False
        except Exception as e:
            print(f'登录异常：{e}')
            return False

    def sign(self):
        """签到"""
        try:
            self.ts = int(datetime.now().timestamp())
            url = "https://admin.dtds888.com/api/index/user/SignIn"
            response = requests.post(url, headers=self.headers, json=self.data)
            jg = response.json()
            if '成功' in jg['msg']:
                xx = f"{self.name}: {jg['msg']}"
                print(xx)
                self.msg += xx + '\n'
            elif '重复' in jg['msg']:
                xx = f"{self.name}: {jg['msg']}"
                print(xx)
                self.msg += xx + '\n'
            else:
                print(jg)
        except Exception as e:
            print(f'签到异常：{e}')
            return False

    def money(self):
        """查询余额"""
        try:
            # 设置当前时间戳
            self.ts = int(datetime.now().timestamp())

            # 请求用户信息的url
            url = "https://admin.dtds888.com/api/index/user/index"

            # 请求
            response = requests.post(url, headers=self.headers, json=self.data)

            # 获取请求返回的响应
            if response.status_code == 200:
                ye = response.json()['data']['user']['balance']
                self.ye = ye
                xx = f'余额: {self.ye}'
                print(xx)
                self.msg += xx + '\n'
            else:
                print(f'登录失败')
                print(response.json())
        except Exception as e:
            print(f'获取余额异常：{e}')

    def tx(self):
        """提现"""
        try:
            self.ts = int(datetime.now().timestamp())
            data = {
                'money': '1',  # 提现金额
                'name': 'we',  # 提现名字
                'deviceType': 'wxapp',
                'timestamp': self.ts,
                'noncestr': '',
                'token': self.token,
                'sign': '',
                'version': '1.00'
            }

            url = 'https://admin.dtds888.com/api/index/user/cashPost'
            if self.ye >= '1':
                response = requests.post(url, headers=self.headers, json=data)
                msg = response.json()['msg']
                xx = f'提现: {msg}'
                print(xx)
                self.msg += xx + '\n'
            else:
                xx = "提现: 钱包余额不足"
                print(xx)
                self.msg += xx + '\n'
                if send:
                    send("泉站签到通知：", self.msg)
        except Exception as e:
            print(f'提现异常：{e}')
            return False


if __name__ == '__main__':
    # 多账户用&分割，将多账户用& 隔开提取成列表
    tokens = os.environ.get("bd_qz")

    token_list = tokens.split('&')

    # 遍历列表
    for token in token_list:
        run = Shui(token)
        if run.login():
            run.sign()
            run.money()
            run.tx()
            print()
