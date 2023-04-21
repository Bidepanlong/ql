"""

time：2023.4.21
cron: 0 9 * * *
new Env('热度星客');

热度星客签到+自动提现脚本
地址：https://m.reduxingke.com/down/register.html?spread=279954&incode=XK28995483
抓包域名: m.reduxingke.com
抓包请求头里面: Authori-zation: Bearer XXXXX
环境变量 rdxkck = Authori-zation抓的XXXXX#提现交易密码(可选)  #分割两个值  Authori-zation不要Bearer
多账号新建变量或者用 & 分开
例如：rdxkck = dca86255101af382#123456     填交易密码满2元自动提现 默认提现到银行卡
     rdxkck = dca86255101af382            没有交易密码只签到
请求头User-Agent可以换成自己的
目前仅支持企业微信机器人推送

"""

import requests
from os import environ


def sign(authorization, pwd):
    headers = {
        "authori-zation": "Bearer " + authorization,
        "User-Agent": "Mozilla/5.0 (Linux; Android 11;Redmi Note 8 Pro Build/RP1A.200720.011;wv)AppleWebKit/537.36(KHTML./like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4435 MMWEBSDK/20230202 Mobile Safari/537.36 MMWEBID/9516MicroMessenger/8.0.33.2320(0x28002151) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
    }
    url = 'https://m.reduxingke.com/api/usersign/sign'
    response = requests.post(url, headers=headers).json()

    infourl = 'https://m.reduxingke.com/api/userinfo'
    info = requests.get(infourl, headers=headers).json()

    txmsg = "[提现]：提现佣金不足"
    txje = float(info['data']['brokerage_price'])
    if txje > 2:
        if pwd != 0:
            txheaders = {
                "authori-zation": "Bearer " + authorization,
                "User-Agent": "Mozilla/5.0 (Linux; Android 11;Redmi Note 8 Pro Build/RP1A.200720.011;wv)AppleWebKit/537.36(KHTML./like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4435 MMWEBSDK/20230202 Mobile Safari/537.36 MMWEBID/9516MicroMessenger/8.0.33.2320(0x28002151) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            }
            txdata = {
                "brokerage": txje,
                "pwd": pwd,
                "extract_type": "bank"
            }
            txurl = 'https://m.reduxingke.com/api/user/applyExtract'
            txinfo = requests.post(txurl, headers=txheaders, json=txdata).json()
            txmsg = "[提现]：{}".format(txinfo['msg'])
        else:
            print("[提现]：提现佣金不足")

    msg = "[账号]：{}\n[用户]：{}\n[签到]：{}\n[余额]：{}".format(a, info['data']['nickname'], response['msg'],
                                                              info['data']['brokerage_price'])
    print(msg)
    print(txmsg)
    ts_msg = "热度星客签到\n" + msg + '\n' + txmsg

    QYWX_KEY = get_environ("QYWX_KEY")
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + QYWX_KEY
    headers = {"Content-Type": "text/plain"}
    data = {
        "msgtype": "text",
        "text": {
            "content": ts_msg
        }

    }

    if QYWX_KEY != "":
        r = requests.post(url=webhook, headers=headers, json=data).json()
        if r["errmsg"] == "ok":
            print("企业微信机器人推送成功")
        else:
            print("企业微信机器人推送失败")
        print()
    else:
        print()


def get_environ(key, default="", output=True):
    def no_read():
        if output:
            if key == "rdxkck":
                print(f"未填写环境变量 {key} 请添加")
        return default

    return environ.get(key) if environ.get(key) else no_read()


if __name__ == '__main__':
    authori_zation = get_environ("rdxkck")
    cks = authori_zation.split("&")
    print("检测到{}个ck记录\n开始热度星客签到".format(len(cks)))
    print()
    a = 0
    for ck in cks:
        c = ck.split('&')
        for i in c:
            d = i.split('#')
        try:
            a += 1
            if len(d) == 2:
                sign(d[0], d[1])
            elif len(d) == 1:
                sign(d[0], 0)
        except KeyError:
            print("请检查ck是否正确")
            print()
