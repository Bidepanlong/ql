"""
time：2024.1.11
定时：一天一次就行了
new Env('彼得小团币')
抓包小程序或者app或者网页的token=Agxxxx  只要token后面的值
环境变量: 名称：bd_mttoken   值：token的值#uuid的值

如果需要一对一推送的用户，
wx打开https://wxpusher.zjiecode.com/wxuser/?type=1&id=67067#/follow
关注推送应用。在进入"WxPusher消息推送平台"公众号-我的-我的UID。获取自己的UID，需要推送的用户
环境变量的值就是 token的值#uuid的值#推送UID的值

如果没推送，大概的环境变量格式就是
AgXXXXXXXXXX#00000000XXXXXXX
有推送就是
AgXXXXXXXXXX#00000000XXXXXXX#UID_XXXXXXX


多账号默认新建变量或者用 & 分开
并发变量: bd_xtbbf  默认不设置为1

"""

import json
import random
import base64
import os
import string
from datetime import datetime
import requests
import time
from functools import partial
from user_agent import generate_user_agent
import concurrent.futures
from urllib3.exceptions import InsecureRequestWarning
import threading

# 活动开关 True/False
# 果园刮刮乐，12.31结束
run_ggl = True

# 自定义变量设置，不需要的不用管。
########################################################
# wxpusher管理员运行日志汇总推送 填入管理员的 UID_xxxxxxx
wxpusher_alluid = os.environ.get("bd_wxpusher_alluid")
if wxpusher_alluid is None:
    wxpusher_alluid = ''

# 自定义变量名，
# 可以自己设置一个环境变量在外面调用，默认自定义变量名 bd_zdyblm，默认不设置是bd_mttoken来调用ck
blname = os.environ.get("bd_zdyblm")
if blname is None:
    blname = 'bd_mttoken'

# 自定义变量分隔符，默认是 & 或者 新建变量。比如需要换行分割就改成 \n。
# 可以自己设置一个环境变量在外面调用，默认自定义分割变量名 bd_zdyblm，值 &
zdyfg = os.environ.get("bd_zdyfg")
if zdyfg is None:
    zdyfg = '&'
########################################################


# 调试设置
########################################################
# 是否打印详细日志 True/False
isprint = os.environ.get("bd_isprint")
if isprint is None:
    isprint = False
else:
    isprint = eval(isprint)

# 最大游戏任务循环次数
max_gamexh = os.environ.get("bd_gamexh")
if max_gamexh is None:
    max_gamexh = 5
else:
    max_gamexh = int(max_gamexh)

# 理论现在我接口生成指纹，这个不需要动，如果没跑成功，改成100。默认最大出现50个提交完成有异常的就不跑!
max_zt3 = os.environ.get("bd_maxzt3")
if max_zt3 is None:
    max_zt3 = 500
else:
    max_zt3 = int(max_zt3)

# 玄学数字，默认4，但是如果有时候提示指纹问题，上面改了100还是无法运行，改成5
xxsz = os.environ.get("bd_xxsz")
if xxsz is None:
    xxsz = 4
else:
    xxsz = int(xxsz)

# 如果改成100，4和5都没法运行，手动看看能不能正常领取游戏中心的币
########################################################


# 代理设置 代理池和代理api只能选择一个使用
########################################################
# 是否启用代理运行 True/False
isdl = os.environ.get("bd_isdlt")
if isdl is None:
    isdl = False
else:
    isdl = eval(isdl)

# 代理api，请保证api打开直接现在一个ip地址和端口即可。环境变量bd_dlapi 值：获取的代理api
proxy_api_url = os.environ.get("bd_dlapi")
if proxy_api_url is None:
    proxy_api_url = ''
# 代理api设置每多少秒切换一次
dl_sleep = os.environ.get("bd_dlsleep")
if dl_sleep is None:
    dl_sleep = 20
else:
    dl_sleep = int(dl_sleep)

# 代理池的地址 环境变量bd_dlc 值：自己的代理池的 ip:prot
proxy_url = os.environ.get("bd_dlc")
if proxy_url is None:
    proxy_url = ''

# 定义全局变量的
proxy = {
    'http': f'http://{proxy_url}',
    'https': f'http://{proxy_url}'
}


#########################################################

def start_dlapi():
    dlstart = threading.Thread(target=get_proxy, args=(stop_event,))
    dlstart.start()


stop_event = threading.Event()


def get_proxy(stop):
    a = 0
    while not stop.is_set():
        global proxy
        a += 1
        response = requests.get(proxy_api_url)
        if response.status_code == 200:
            proxy_data = response.text
            if isdl:
                print(f'🔔第{a}次获取代理成功: {proxy_data}')
            proxy = {
                'http': f'http://{proxy_data}',
                'https': f'http://{proxy_data}'
            }
            time.sleep(dl_sleep)
            continue
        else:
            if isdl:
                print(f'🔔第{a}次获取代理失败！重新获取！')
            continue


def ts_qb(data):
    # WxPusher API地址
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'

    # 按照序号字段对数据进行排序
    sorted_data = sorted(data, key=lambda x: x['序号'])

    # 构造要推送的表格内容
    table_content = ''
    for row in sorted_data:
        table_content += f"<tr><td style='border: 1px solid #ccc; padding: 6px;'>{row['序号']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['用户']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['今日团币']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['总共团币']}</td></tr>"

    table_html = f"<table style='border-collapse: collapse;'><tr style='background-color: #f2f2f2;'><th style='border: 1px solid #ccc; padding: 8px;'>🆔</th><th style='border: 1px solid #ccc; padding: 8px;'>用户</th><th style='border: 1px solid #ccc; padding: 8px;'>今日团币</th><th style='border: 1px solid #ccc; padding: 8px;'>总共团币</th></tr>{table_content}</table>"

    # 构造请求参数
    params = {
        "appToken": 'AT_F84lDjyaKceMNQshI4ZYhNyENLlnh5qW',
        'content': table_html,
        'contentType': 3,  # 表格类型
        'topicIds': [],  # 接收消息的用户ID列表，为空表示发送给所有用户
        "summary": f'小团币运行日志汇总',
        "uids": [wxpusher_alluid],
    }

    # 发送POST请求
    response = requests.post(api_url, json=params)

    # 检查API响应
    if response.status_code == 200:
        result = response.json()
        if result['code'] == 1000:
            print('🎉管理员汇总推送成功')
        else:
            print(f'💔管理员汇总推送失败，错误信息：{result["msg"]}')
    else:
        print('⛔️管理员汇总推送请求失败')


class Mttb:
    def __init__(self, zh, ck):
        self.mtgcs = None
        global ts_all
        self.num = zh
        self.coins = None
        if "UID" in ck:
            self.ck = ck.split('#')[0]
            self.uuid = ck.split('#')[1]
            self.uid = ck.split('#')[2]
        else:
            self.ck = ck.split('#')[0]
            self.uuid = ck.split('#')[1]
            self.uid = None
        self.ddmsg = None
        self.fingerprint = None
        self.login = None
        self.lisss = None
        self.lastGmtCreated = None
        self.qdrwids = [10002, 10024, 10041, 10015, 10014, 10014]
        self.qdid = None
        self.llid = None
        self.startmsg = ''
        self.endmsg = ''
        self.llids = []
        self.qdactoken = None
        self.xtb = None
        self.wcxtb = None
        self.t_h = None
        self.actoken = None
        self.usid = None
        self.name = None
        self.ua = generate_user_agent(os='android')
        self.msg = ""
        self.ids = []
        self.noids = [420, 421, 422, 423, 424, 15169, 15170, 15171, 15172, 15173]
        self.id = None
        self.tid = None
        self.data_list = None
        self.mtbb = 'meituan'
        self.platform = xxsz
        self.gglactoken = None
        self.ggl_list = None
        self.gglid = None
        self.cardId = None

    def get_mtg(self):
        url = "http://bedee.top:1299/sign"
        data = {
            "url": "https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/queryMgcTaskInfo?yodaReady=h5&csecplatform=4&csecversion=2.3.1&mtgsig={}",
            # ck
            "cookie": f'token={self.ck};',
            "userAgent": 'Mozilla/5.0 (Linux; Android 9; 16T Build/PKQ1.190616.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5049 MMWEBSDK/20221109 MMWEBID/1928 MicroMessenger/8.0.31.2281(0x28001F59) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            "data": {"cType": "wx_wallet", "fpPlatform": 13, "wxOpenId": "", "appVersion": ""}
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            # print(response.json())
            mtf = response.json()['mtFingerprint']
            # print(mtf)
            # print()
            self.mtgcs = response.json()['mtgsig']
            self.mtgcs = json.dumps(self.mtgcs, separators=(',', ':'))
            # print()
        else:
            print("请求失败:", response.status_code)

    def wxpusher(self):
        msg = f'🆔{self.name}<br>💰今日团币: {self.coins}<br>🎁总共团币: {self.wcxtb}({int(self.wcxtb) / 1000}元)'
        str = f'''<section style="width: 24rem; max-width: 100%;border:none;border-style:none;margin:2.5rem auto;">
        <section
            style="margin: 0px auto;text-align: left;border: 1.5px solid #212122;padding: 10px 0px;box-sizing:border-box; width: 100%; display:inline-block;background-color:#F3FFF1">
            <section style="margin-top: 1rem; float: left; margin-left: 1rem; margin-left: 1rem; font-size: 3.3rem; font-weight: bold;">
                <p style="margin: 0; color: black">
                    通知
                </p>
            </section>
            <section style="display: block;width: 0;height: 0;clear: both;"></section>
            <section
                style="margin-top:20px; display: inline-block; border-bottom: 1px solid #212122; padding: 4px 20px; box-sizing:border-box;"
                class="ipaiban-bbc">
                <section
                    style="width:25px; height:25px; border-radius:50%; background-color:#212122;display:inline-block;line-height: 25px">
                    <p style="text-align:center;font-weight:1000;margin:0">
                        <span style="color: #ffffff;font-size:20px;">🗣</span>
                    </p>
                </section>
                <section style="display:inline-block;padding-left:10px;vertical-align: top;box-sizing:border-box;">
                </section>
            </section>
            <section style="margin-top:0rem;padding: 0.8rem;box-sizing:border-box;">
                <p style=" line-height: 1.6rem; font-size: 1.1rem; ">
                    {msg} 
                </p>            
            </section>
        </section>
    </section>'''
        data = {
            "appToken": 'AT_F84lDjyaKceMNQshI4ZYhNyENLlnh5qW',
            "content": str,
            "summary": f'{self.name}小团币运行日志',
            "contentType": 2,
            "uids": [self.uid],
        }
        url = 'http://wxpusher.zjiecode.com/api/send/message'
        try:
            res = requests.post(url=url, json=data).json()
            if res['code'] == 1000:
                self.endmsg += f'🎉日志推送完成\n'
                return True
            else:
                self.endmsg += f'💔日志推送失败\n'
                return False
        except:
            self.endmsg += f'⛔️日志推送出错\n'
            return False

    def sq_login(self):
        try_count = 5
        while try_count > 0:
            try:
                url = "http://bedee.top:1250/tbyz"
                headers = {'Content-Type': 'application/json'}
                data = {
                    'token': self.ck,
                    'ua': self.ua,
                    'uuid': self.uuid
                }
                r = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                ffmsg = r.json().get('msg', None)
                if '成功' in r.text and self.ck in r.text:
                    rj = r.json()
                    dlzt = rj['msg']
                    self.name = rj['name']
                    self.usid = rj['usid']
                    sj = rj['expirytime']
                    self.fingerprint = rj['fingerprint']
                    self.startmsg += f'🆔账号{self.num}-{self.name}({self.usid}) ✅{dlzt}\n⏰授权到期时间：{sj}\n'
                    return True
                elif self.ck not in r.text:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num} 登录返回错误，还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
                else:
                    print(f'🆔账号{self.num} 登录失败：{ffmsg}\n')
                    return False
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num} 登录异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def km_login(self):
        try_count = 5
        while try_count > 0:
            try:
                url = "http://bedee.top:1250/tbyz"
                headers = {'Content-Type': 'application/json'}
                data = {
                    'token': self.ck,
                    'ua': self.ua,
                    'uuid': self.uuid,
                    'km': km
                }
                r = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                ffmsg = r.json().get('msg', None)
                if '登录成功' in r.text and self.ck in r.text and '卡密次数不足' not in r.text:
                    rj = r.json()
                    dlzt = rj['msg']
                    self.name = rj['name']
                    self.usid = rj['usid']
                    self.fingerprint = rj['fingerprint']
                    self.startmsg += f'🆔账号{self.num}-{self.name}({self.usid}) ✅{dlzt}\n'
                    return True
                elif '卡密次数不足' in r.text or '卡密验证失败' in r.text:
                    rj = r.json()
                    dlzt = rj['msg']
                    self.name = rj['name']
                    self.usid = rj['usid']
                    self.startmsg += f'🆔账号{self.num}-{self.name}({self.usid}) ✅{dlzt}\n'
                    return False
                elif self.ck not in r.text:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num} 登录返回错误，还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
                else:
                    print(f'🆔账号{self.num} 登录失败：{ffmsg}\n')
                    return False
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num} 登录异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def act(self):
        try_count = 5
        while try_count > 0:
            try:
                url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login'
                h = {
                    'Accept': 'application/json, text/plain, */*',
                    'Content-Length': '307',
                    'x-requested-with': 'XMLHttpRequest',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sing = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                data = {
                    "mtToken": self.ck,
                    "deviceUUID": self.uuid,
                    "mtUserId": self.usid,
                    "idempotentString": sing
                }
                if isdl:
                    r = requests.post(url, headers=h, json=data, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.post(url, headers=h, json=data, timeout=10, verify=False)
                if r.json()['data']['loginInfo']['accessToken'] is not None:
                    self.actoken = r.json()['data']['loginInfo']['accessToken']
                    break
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num}-{self.name} 获取actoken异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num}-{self.name} 获取actoken异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def get_ids(self):
        try_count = 5
        while try_count > 0:
            try:
                url = f'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/queryMgcTaskInfo?yodaReady=h5&csecplatform=4&csecversion=2.3.1&mtgsig={self.mtgcs}'
                # print(url)
                data = {
                    'externalStr': '',
                    'riskParams': {
                        'uuid': self.uuid,
                        "platform": self.platform,
                        "fingerprint": self.fingerprint,
                        "version": "12.17.203",
                        "app": 0,
                        "cityid": "351"
                    },
                    'gameType': 10102
                }
                data = json.dumps(data, separators=(',', ':'))
                h = {
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'actoken': self.actoken,
                    'mtoken': self.ck,
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                if isdl:
                    r = requests.post(url, headers=h, data=data, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.post(url, headers=h, data=data, timeout=10, verify=False)
                rj = r.json()
                if rj['msg'] == 'ok' and r.json()['data']['taskList'] != []:
                    self.data_list = r.json()['data']['taskList']
                    return True
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num}-{self.name} 获取游戏任务异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num}-{self.name} 获取游戏任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def startcxtb(self):
        try_count = 5
        while try_count > 0:
            try:
                url = 'https://game.meituan.com/mgc/gamecenter/skuExchange/resource/counts?sceneId=3&gameId=10102'
                self.t_h = {
                    'User-Agent': self.ua,
                    'actoken': self.actoken,
                    'mtoken': self.ck,
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                if isdl:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False, proxies=proxy)

                else:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False)
                rj = r.json()
                if rj['msg'] == 'ok':
                    data = rj['data']
                    for d in data:
                        self.xtb = d['count']
                        self.startmsg += f'🎁运行前小团币: {int(self.xtb)}({int(self.xtb) / 1000}元)\n'
                    return True
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num}-{self.name} 查询运行前团币失败：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num}-{self.name} 查询运行前团币异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def endcxtb(self):
        try_count = 5
        while try_count > 0:
            try:
                url = 'https://game.meituan.com/mgc/gamecenter/skuExchange/resource/counts?sceneId=3&gameId=10102'
                # self.t_h = {
                #     'User-Agent': self.ua,
                #     'actoken': self.actoken,
                #     'mtoken': self.ck,
                #     'cookie': f'token={self.ck}'
                # }
                self.t_h = {
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'actoken': self.actoken,
                    'mtoken': self.ck,
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                if isdl:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False, )
                rj = r.json()
                if rj['msg'] == 'ok':
                    data = rj['data']
                    for d in data:
                        self.wcxtb = d['count']
                        self.endmsg += f'🎁运行后小团币: {int(self.wcxtb)}({int(self.wcxtb) / 1000}元)\n'
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 查询运行后团币失败：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 查询运行后团币异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def b64(self):
        y_bytes = base64.b64encode(self.tid.encode('utf-8'))
        y_bytes = y_bytes.decode('utf-8')
        return y_bytes

    def get_game(self):
        try_count = 5
        while try_count > 0:
            try:
                self.tid = f'mgc-gamecenter{self.id}'
                self.tid = self.b64()
                url = f'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/finishV2'
                params = {
                    'taskId': self.tid,
                }
                if isdl:
                    r = requests.get(url, headers=self.t_h, params=params, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.get(url, headers=self.t_h, params=params, timeout=10, verify=False)
                if isprint:
                    print(f'🆔账号{self.num}-{self.name}({self.usid}) 领取{self.id} {r.json()}')
                if r.status_code == 200:
                    if r.json()['msg'] == 'ok':
                        time.sleep(random.randint(1, 3))
                        return True
                    elif '完成过' in r.text:
                        time.sleep(random.randint(1, 3))
                        return False
                    else:
                        if isprint:
                            print(f'🆔账号{self.num}-{self.name}({self.usid}) 任务状态: {r.text}')
                        return False
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} {self.id}领取任务失败：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.id}领取任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def post_id(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'game.meituan.com',
                    'Connection': 'keep-alive',
                    # 'Content-Length': '2725',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'actoken': self.actoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://mgc.meituan.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://mgc.meituan.com/',
                    # 'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs
                    ,
                }
                data = {
                    "taskId": self.id,
                    "externalStr": "",
                    "riskParams": {
                        "uuid": self.uuid,
                        "platform": 4,
                        "fingerprint": self.fingerprint,
                        "version": "12.17.203",
                        "app": 0,
                        "cityid": "351"
                    },
                    "gameType": 10102
                }
                if isdl:
                    r = requests.post(
                        'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/receiveMgcTaskReward',
                        params=params, headers=headers, json=data, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.post(
                        'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/receiveMgcTaskReward',
                        params=params, headers=headers, json=data, timeout=10, verify=False)
                if isprint:
                    print(f'🆔账号{self.num}-{self.name}({self.usid}) 完成{self.id} {r.json()}')
                if r.status_code == 200:
                    if r.json()['msg'] == 'ok':
                        time.sleep(random.randint(1, 3))
                        return True
                    elif '异常' in r.text:
                        time.sleep(random.randint(1, 3))
                        return False
                    else:
                        print(f'🆔账号{self.num}-{self.name} {self.id},{r.text}\n')
                        time.sleep(random.randint(1, 3))
                        return False
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} {self.id}完成任务异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))

                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.id}完成任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def coin_login(self):
        """获取签到浏览的actoken"""
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Origin': 'https://awp.meituan.com',
                    'Cookie': f'uuid={self.uuid};token={self.ck};',
                    'Accept': '*/*',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json',
                    'Host': 'game.meituan.com',
                    'Connection': 'Keep-Alive',
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'mtUserId': self.usid,
                    'mtDeviceId': self.uuid,
                    'mtToken': self.ck,
                    'nonceStr': 'tq0wppcrgrc0nk26',
                    'gameType': 10273,
                    'externalStr': {"cityId": "351"},
                    'shark': 1,
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                if isdl:
                    r = requests.get('https://game.meituan.com/coin-marketing/login/loginMgc', headers=headers,
                                     params=params, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.get('https://game.meituan.com/coin-marketing/login/loginMgc', headers=headers,
                                     params=params, timeout=10, verify=False)
                self.qdactoken = r.json().get('accessToken', None)
                if self.qdactoken is not None:
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 获取qdactoken异常，还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取qdactoken异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def qd(self):
        """签到和浏览任务"""
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'game.meituan.com',
                    'Connection': 'keep-alive',
                    'x-requested-with': 'XMLHttpRequest',
                    'appName': 'meituan',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'Origin': 'https://awp.meituan.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    "protocolId": self.qdid,
                    "data": {},
                    "riskParams": {
                        "ip": "",
                        "uuid": self.uuid,
                        "platform": self.platform,
                        "version": "12.17.203",
                        "app": 0,
                        "fingerprint": self.fingerprint,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken
                }
                if self.qdid == 10024:
                    while True:
                        if isdl:
                            r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                              json=data, params=params, timeout=10, verify=False, proxies=proxy)
                        else:
                            r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                              json=data, params=params, timeout=10, verify=False)
                        if isprint:
                            print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.qdid}: {r.json()}')
                        if 'interval' in r.text:
                            xxsj = r.json()['data']['timedReward']['interval']
                            time.sleep(xxsj / 1000)
                            time.sleep(random.randint(1, 3))
                            continue
                        else:
                            time.sleep(random.randint(1, 3))
                            break
                    return True
                elif self.qdid == 10041:
                    while True:
                        if isdl:
                            r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                              json=data,
                                              params=params, timeout=10, verify=False, proxies=proxy)
                        else:
                            r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                              json=data,
                                              params=params, timeout=10, verify=False)
                        if isprint:
                            print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.qdid}: {r.json()}')
                        if 'rewardAmount' in r.text:
                            time.sleep(random.randint(1, 3))
                            continue
                        else:
                            time.sleep(random.randint(1, 3))
                            break
                    return True
                else:
                    if isdl:
                        r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                          json=data,
                                          params=params, timeout=10, verify=False, proxies=proxy)
                    else:
                        r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                          json=data,
                                          params=params, timeout=10, verify=False)
                    if isprint:
                        print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.qdid}: {r.json()}')
                    time.sleep(random.randint(1, 3))
                    return True
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.qdid}签到任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def get_llids(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'game.meituan.com',
                    'Connection': 'keep-alive',
                    'x-requested-with': 'XMLHttpRequest',
                    'appName': self.mtbb,
                    'User-Agent': self.ua,
                    'Accept': '*/*',
                    'Origin': 'https://awp.meituan.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                # "protocolId": 10002,  # 签到
                # "protocolId": 10024,  # 1 3 5 要等待时间
                # "protocolId": 10041,  # 下滑浏览
                # "protocolId": 10008,  # 获取id
                # "protocolId": 10014,  # 抽奖
                # "protocolId": 10015,  # 抽奖前运行
                data = {
                    "protocolId": 10008,
                    "data": {},
                    "riskParams": {
                        "ip": "",
                        "uuid": self.uuid,
                        "platform": 4,
                        "version": "12.17.203",
                        "app": 0,
                        "fingerprint": self.fingerprint,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken,
                }
                if isdl:
                    r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                      json=data,
                                      params=params, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                      json=data,
                                      params=params, timeout=10, verify=False)
                time.sleep(random.randint(1, 3))
                self.lisss = r.json()['data']['taskInfoList']
                return True
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.qdid}签到任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def get_ll(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'game.meituan.com',
                    'Connection': 'keep-alive',
                    'x-requested-with': 'XMLHttpRequest',
                    'appName': self.mtbb,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'Origin': 'https://awp.meituan.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }

                get_data = {
                    "protocolId": 10010,  # 先运行获取任务
                    "data": {
                        "externalStr": {"cityId": "351"},
                        "taskId": self.llid,  # 任务id
                        "taskEntranceType": "normal"
                    },
                    "riskParams": {
                        "ip": "",
                        "uuid": self.uuid,
                        "platform": 4,
                        "version": "12.17.203",
                        "app": 0,
                        "fingerprint": self.fingerprint,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken,
                    "mtToken": self.ck
                }
                if isdl:
                    r = requests.post(
                        'https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                        json=get_data,
                        params=params, timeout=10, verify=False, proxies=proxy
                    )
                else:
                    r = requests.post(
                        'https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                        json=get_data,
                        params=params, timeout=10, verify=False
                    )
                if isprint:
                    print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.llid} 领取任务 {r.json()}')
                if r.json()['data'] is None:
                    time.sleep(random.randint(1, 3))
                    return False
                else:
                    time.sleep(random.randint(1, 3))
                    return True
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.llid}获取浏览任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def post_ll(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    "Host": "game.meituan.com",
                    "Connection": "keep-alive",
                    "Content-Length": "747",
                    "x-requested-with": "XMLHttpRequest",
                    "appName": self.mtbb,
                    "innerSource": "10273_yxdt",
                    "User-Agent": self.ua,
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Origin": "https://mgc.meituan.com",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }

                post_data = {
                    "protocolId": 10009,
                    "data": {
                        "externalStr": "{\"cityId\":\"351\"}",
                        "taskId": f'{self.llid}',
                        "taskEntranceType": "normal"
                    },
                    "riskParams": {
                        "ip": "",
                        "uuid": self.uuid,
                        "platform": 4,
                        "version": "12.17.203",
                        "app": 0,
                        "fingerprint": self.fingerprint,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken,
                    "mtToken": self.ck
                }
                if isdl:
                    r = requests.post(
                        'https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                        json=post_data,
                        params=params, timeout=10, verify=False,
                        proxies=proxy
                    )
                else:
                    r = requests.post(
                        'https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                        json=post_data,
                        params=params, timeout=10, verify=False
                    )
                if isprint:
                    print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.llid} 完成任务 {r.json()}\n')
                if r.json()['data'] is None:
                    time.sleep(random.randint(1, 3))
                    return False
                else:
                    time.sleep(random.randint(1, 3))
                    return True
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} {self.llid}完成浏览任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def tj_bchd(self):
        try_count = 5
        while try_count > 0:
            try:
                bchd = int(self.wcxtb) - int(self.xtb)
                url = "https://game.meituan.com/mgc/gamecenter/skuExchange/resources/change/logs?changeType=1&limit=50&sceneId=2&gameId=10139&mtToken=&acToken=&shark=1&yodaReady=h5&csecplatform=4&csecversion=2.3.1"
                headers = {
                    "Host": "game.meituan.com",
                    "Connection": "keep-alive",
                    "x-requested-with": "XMLHttpRequest",
                    "actoken": self.qdactoken,
                    "mtoken": self.ck,
                    "User-Agent": "Mozilla/5.0 (Linux; Android 13; V2055A Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.74 Mobile Safari/537.36 TitansX/11.38.10 KNB/1.2.0 android/13 mt/com.meituan.turbo/2.0.202 App/10120/2.0.202 MeituanTurbo/2.0.202",
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Origin": "https://awp.meituan.com",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://awp.meituan.com/",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"

                }
                if isdl:
                    r = requests.get(url, headers=headers, timeout=10, verify=False, proxies=proxy)
                else:
                    r = requests.get(url, headers=headers, timeout=10, verify=False)
                if r.json()['msg'] == 'ok':
                    datalist = r.json()['data']
                    coins = 0
                    for data in datalist:
                        coin = data['changeCount']
                        gmtCreated = data['gmtCreated']
                        if gmtCreated >= f"{datetime.now().strftime('%Y-%m-%d')} 00:00:00":
                            coins += coin
                        else:
                            break
                    self.lastGmtCreated = datalist[-1]['gmtCreated']
                    while True:
                        if self.lastGmtCreated >= f"{datetime.now().strftime('%Y-%m-%d')} 00:00:00":
                            url1 = f"https://game.meituan.com/mgc/gamecenter/skuExchange/resources/change/logs?changeType=1&limit=50&sceneId=2&lastGmtCreated={self.lastGmtCreated}&gameId=10139&mtToken=&acToken=&shark=1&yodaReady=h5&csecplatform=4&csecversion=2.3.1"
                            if isdl:
                                r = requests.get(url1, headers=headers, timeout=10, verify=False, proxies=proxy)
                            else:
                                r = requests.get(url1, headers=headers, timeout=10, verify=False)
                            if isprint:
                                print(r.json())
                                print()
                            if 'ok' in r.text and r.json()['data'] != []:
                                datalist = r.json()['data']
                                for data in datalist:
                                    coin = data['changeCount']
                                    gmtCreated = data['gmtCreated']
                                    if gmtCreated >= f"{datetime.now().strftime('%Y-%m-%d')} 00:00:00":
                                        coins += coin
                                    else:
                                        break
                                self.lastGmtCreated = datalist[-1]['gmtCreated']
                                if self.lastGmtCreated >= f"{datetime.now().strftime('%Y-%m-%d')} 00:00:00":
                                    time.sleep(random.randint(1, 3))
                                    continue
                                else:
                                    self.coins = coins
                                    self.endmsg += f'🔥本次获得小团币: {bchd}\n💰今日团币: {coins}\n'
                                    return True
                            elif 'ok' in r.text and r.json()['data'] == []:
                                self.coins = coins
                                self.endmsg += f'🔥本次获得小团币: {bchd}\n💰今日团币: {coins}\n'
                                return True
                            else:
                                if isprint:
                                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                                try_count -= 1
                                time.sleep(random.randint(2, 5))
                                continue
                        else:
                            self.coins = coins
                            self.endmsg += f'🔥本次获得小团币: {bchd}\n💰今日团币: {coins}\n'
                            return True
                    break
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def get_new_gameid(self):
        if self.get_ids():
            self.ids = []
            zt_3 = []
            for i in self.data_list:
                if i['status'] == 2 and i['id'] not in self.noids:
                    self.ids.append(i['id'])
                if i['status'] == 3 and i['id'] not in self.noids:
                    self.ids.append(i['id'])
                    zt_3.append(i['id'])
                else:
                    pass
            if isprint:
                print(f'🆔账号{self.num}-{self.name}({self.usid}) 获取到{len(self.ids)}个游戏任务！\n{self.ids}')
            if self.ids != [] and len(zt_3) < max_zt3:
                return True
            elif not self.ids:
                return True
            else:
                self.startmsg += f'🆔账号{self.num}-{self.name}({self.usid}) ⛔️跑不动,{len(zt_3)}个任务未提交成功!尝试修改max_zt3参数为100！！！\n'
                return False
        else:
            return False

    def run_game(self):
        random.shuffle(self.data_list)
        i_num = 0
        for i in self.data_list:
            zong = len(self.ids)
            self.id = i['id']
            zt = i['status']
            if self.id in self.noids:
                pass
            else:
                if zt == 2 and self.id in [386, 510, 511, 332]:
                    i_num += 1
                    a = 0
                    while a < 5:
                        a += 1
                        if isprint:
                            print(
                                f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 状态: {zt} 第{a}次')
                        if self.get_game():
                            self.post_id()
                            continue
                        else:
                            break
                    continue
                elif zt == 3 and self.id in [386, 510, 511, 332]:
                    i_num += 1
                    a = 1
                    if isprint:
                        print(
                            f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 状态: {zt} 第{a}次')
                    self.post_id()
                    while a < 5:
                        a += 1
                        if isprint:
                            print(
                                f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 状态: {zt} 第{a}次')
                        if self.get_game():
                            self.post_id()
                            continue
                        else:
                            break
                    continue
                elif zt == 2:
                    i_num += 1
                    if isprint:
                        print(
                            f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 状态: {zt}')
                    if self.get_game():
                        self.post_id()
                        continue
                elif zt == 3:
                    i_num += 1
                    if isprint:
                        print(f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 状态: {zt}')
                    self.post_id()
                    continue
                else:
                    continue

    def get_new_llids(self):
        if self.get_llids():
            self.llids = []
            for i in self.lisss:
                taskTitles = json.loads(i['mgcTaskBaseInfo']['viewExtraJson'])
                buttonName = taskTitles.get('common', None).get('buttonName', '去完成')
                zt = i['status']
                if zt == 2 and buttonName in ['去完成', '去浏览', '去阅读', '去领取']:
                    self.llids.append(i['id'])
                elif zt == 3 and buttonName in ['去完成', '去浏览', '去阅读', '去领取']:
                    self.llids.append(i['id'])
                else:
                    pass
            if isprint:
                print(f'🆔账号{self.num}-{self.name}({self.usid}) 获取到{len(self.llids)}个浏览任务！\n{self.llids}')
            if self.llids:
                return True
            else:
                return False
        else:
            return False

    def run_tbzx(self):
        for i in self.lisss:
            zt = i['status']
            self.llid = i['id']
            taskTitles = json.loads(i['mgcTaskBaseInfo']['viewExtraJson'])
            taskTitle = taskTitles['common']['taskTitle']
            taskDesc = taskTitles['common']['taskDesc']
            buttonName = taskTitles.get('common', None).get('buttonName', '去完成')
            if zt in [2, 3] and self.llid == 15181:
                if isprint:
                    print(
                        f'🆔账号{self.num}-{self.name}({self.usid}) {self.llid}: 状态：{zt} {taskTitle}({taskDesc}) {buttonName}')
                while True:
                    if self.get_ll():
                        if self.post_ll():
                            continue
                        else:
                            break
                    else:
                        break
            elif zt == 2 and buttonName in ['去完成', '去浏览', '去阅读', '去领取']:
                if isprint:
                    print(
                        f'🆔账号{self.num}-{self.name}({self.usid}) {self.llid}: 状态：{zt} {taskTitle}({taskDesc}) {buttonName}')
                if self.get_ll():
                    self.post_ll()
            elif zt == 3 and buttonName in ['去完成', '去浏览', '去阅读', '去领取']:
                if isprint:
                    print(
                        f'🆔账号{self.num}-{self.name}({self.usid}) {self.llid}: 状态：{zt} {taskTitle}({taskDesc}) {buttonName}')
                self.post_ll()
            else:
                continue

    def run_tbrw(self):
        self.read_sign()
        if self.get_new_llids():
            self.run_tbzx()
        self.mtbb = 'meituanturbo'
        if self.get_new_llids():
            self.run_tbzx()
        self.llid = 616
        if self.get_ll():
            self.post_ll()
        for i in self.qdrwids:
            self.qdid = i
            self.qd()
        else:
            pass

    def read_sign(self):
        try_count = 5
        while try_count > 0:
            try:
                url = 'https://web.meituan.com/novel/marketing/sign/signV2'
                headers = {
                    'Host': 'web.meituan.com',
                    'appType': 'group',
                    'token': self.ck,
                    'content-type': 'application/json',
                    'User-Agent': self.ua,
                    'Referer': 'https://servicewechat.com/wxde8ac0a21135c07d/1248/page-frame.html',
                }

                params = {
                    'yodaReady': 'wx',
                    'csecappid': 'wxde8ac0a21135c07d',
                    'csecplatform': '3',
                    'csecversionname': '7.49.4',
                    'csecversion': '1.4.0',
                }
                json_data = {
                    'fingerprint': '',
                }
                r = requests.post(url=url, params=params, headers=headers, json=json_data)
                if '成功' in r.text:
                    response = r.json()
                    times = response['data']['times']
                    sign_list = response['data']['signList']
                    award_amount_list = [item['awardAmount'] for item in sign_list if item['signed']]
                    if isprint:
                        print(
                            f"🆔账号{self.num}-{self.name} 第{times}天阅读签到成功📕，今日已获得{award_amount_list[-1]}团币")
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 小说签到异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue

            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 小说签到异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def game_gift(self):
        url = "https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/gift/xtb/exchangeWeekCard?yodaReady=h5&csecplatform=4&csecversion=2.3.1&mtgsig={}"
        h = {
            'Accept': 'application/json, text/plain, */*',
            'x-requested-with': 'XMLHttpRequest',
            'User-Agent': self.ua,
            'Content-Type': 'application/json;charset=UTF-8',
            'actoken': self.actoken,
            'mtoken': self.ck,
            'Cookie': f'uuid={self.uuid};token={self.ck};'
        }
        if isdl:
            r = requests.get(url, headers=h, timeout=10, verify=False, proxies=proxy)
            time.sleep(random.randint(1, 3))
        else:
            r = requests.get(url, headers=h, timeout=10, verify=False)
            time.sleep(random.randint(1, 3))
        if isprint:
            print(r.text)

    def get_gglactoken(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '119',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://guoyuan.meituan.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    'uuid': self.uuid,
                    'scratchSource': 1,
                    'idempotent': 'pr2l4wrcn7'
                }
                r = requests.post('https://guoyuan.meituan.com/scratch/index', params=params, headers=headers,
                                  json=data)
                self.gglactoken = r.json().get('data').get('acToken', None)
                if self.gglactoken is not None:
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐actoken异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐actoken异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def get_ggllist(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'acToken': self.gglactoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'scratchSource': '1',
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                r = requests.get('https://guoyuan.meituan.com/scratch/mgcUser/taskList', params=params,
                                 headers=headers)
                self.ggl_list = r.json().get('data').get('taskList', None)
                if self.ggl_list:
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐任务列表异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐任务列表异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def get_ggl(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '34',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'acToken': self.gglactoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Origin': 'https://guoyuan.meituan.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    'taskId': self.gglid,
                    'scratchSource': 1
                }
                r = requests.post(
                    'https://guoyuan.meituan.com/scratch/mgcUser/finishTask',
                    params=params,
                    headers=headers,
                    json=data,
                )
                codes = r.json().get('code', None)
                if isprint:
                    print(f'🆔账号{self.num}-{self.name}({self.usid}) {self.gglid} 领取刮刮乐任务 {r.json()}')
                if codes == 0 or codes == 1101:
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 领取刮刮乐任务异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 领取刮刮乐任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def post_ggl(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '34',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'acToken': self.gglactoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://guoyuan.meituan.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    'taskId': self.gglid,
                    'scratchSource': 1
                }
                r = requests.post(
                    'https://guoyuan.meituan.com/scratch/mgcUser/receiveTaskReward',
                    params=params,
                    headers=headers,
                    json=data,
                )
                codes = r.json().get('code', None)
                restCard = r.json().get('data', None).get('restCard', None)
                if isprint:
                    print(
                        f'🆔账号{self.num}-{self.name}({self.usid}) {self.gglid} 完成刮刮乐任务，次数{restCard}。{r.json()}')
                if codes == 0:
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 完成刮刮乐任务异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue

            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 完成刮刮乐任务异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def get_gglcard(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '19',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'acToken': self.gglactoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://guoyuan.meituan.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    'scratchSource': 1
                }
                r = requests.post(
                    'https://guoyuan.meituan.com/scratch/mgcUser/useCard',
                    params=params,
                    headers=headers,
                    json=data,
                )
                codes = r.json()['code']
                if '没有刮刮卡' in r.text:
                    return False
                elif '正在刮的卡' in r.text:
                    return False
                elif codes == 0:
                    self.cardId = r.json()['data']['scratchInProgress']['cardId']
                    if isprint:
                        print(f'🆔账号{self.num}-{self.name} 获取刮刮乐id成功: {self.cardId}')
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐id异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except Exception as e:
                print(e)
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 获取刮刮乐id异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def gk_ggl(self):
        try_count = 5
        while try_count > 0:
            try:
                headers = {
                    'Host': 'guoyuan.meituan.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '87',
                    'Accept': 'application/json, text/plain, */*',
                    'x-requested-with': 'XMLHttpRequest',
                    'acToken': self.gglactoken,
                    'mtoken': self.ck,
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://guoyuan.meituan.com',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cookie': f'uuid={self.uuid};token={self.ck};'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    'mtgsig': self.mtgcs,
                }
                data = {
                    'cardId': self.cardId,
                    'scratchedUnits': [1, 1, 1, 1, 1, 1, 1, 1, 1],
                    'scratchSource': 1
                }
                r = requests.post(
                    'https://guoyuan.meituan.com/scratch/mgcUser/progress',
                    params=params,
                    headers=headers,
                    json=data,
                )
                codes = r.json().get('code', None)
                if codes == 0:
                    prizeList = r.json()['data']['prizeList']
                    for i in prizeList:
                        if isprint:
                            print(f'🆔账号{self.num}-{self.name} 刮刮乐获得{i["prizeName"]}')
                    time.sleep(random.randint(1, 3))
                    return True
                else:
                    if isprint:
                        self.endmsg += f'🆔账号{self.num}-{self.name} 刮刮乐刮卡异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except:
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 刮刮乐刮卡异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(3, 8))
                continue

    def run_ggl(self):
        if self.get_gglactoken():
            if self.get_ggllist():
                for i in self.ggl_list:
                    zt = i['status']
                    self.gglid = i['id']
                    viewTitle = i['viewTitle']
                    dailyFinishTimes = i['dailyFinishTimes']
                    maxLimit = i['maxLimit']
                    if dailyFinishTimes < maxLimit and '下单' not in viewTitle and '美团首页' not in viewTitle and zt == 2:
                        if isprint:
                            print(
                                f'🆔账号{self.num}-{self.name}({self.usid}) {self.gglid}: 状态：{zt} {viewTitle}({dailyFinishTimes}/{maxLimit}) 未完成')
                        for i in range(maxLimit - dailyFinishTimes):
                            if self.get_ggl():
                                self.post_ggl()
                    elif dailyFinishTimes <= maxLimit and '下单' not in viewTitle and '美团首页' not in viewTitle and zt == 3:
                        if isprint:
                            print(
                                f'🆔账号{self.num}-{self.name}({self.usid}) {self.gglid}: 状态：{zt} {viewTitle}({dailyFinishTimes}/{maxLimit}) 未领取')
                        self.post_ggl()
                    else:
                        if isprint:
                            print(
                                f'🆔账号{self.num}-{self.name}({self.usid}) {self.gglid}: 状态：{zt} {viewTitle}({dailyFinishTimes}/{maxLimit}) 已完成或者跳过不做')
            while True:
                if self.get_gglcard():
                    self.gk_ggl()
                    continue
                else:
                    break

    def main(self):
        if km is None:
            self.login = self.sq_login
        else:
            self.login = self.km_login
        if self.login():
            self.act()
            self.get_mtg()
            if self.startcxtb():
                isgame = self.get_new_gameid()
                if isgame and self.ids != []:
                    if 717 not in self.ids:
                        self.game_gift()
                    self.startmsg += f'🔔游戏中心获取任务成功！🚀即将运行游戏中心任务和团币中心任务\n'
                    print(self.startmsg)
                    a = 0
                    while True:
                        a += 1
                        if a > max_gamexh:
                            break
                        self.run_game()
                        isgame = self.get_new_gameid()
                        if isgame and len(self.ids) != 0:
                            continue
                        elif isgame and len(self.ids) == 0:
                            break
                        else:
                            self.endmsg += f'⛔️第{a}循环发现问题，停止游戏中心任务运行！'
                            break
                    if self.coin_login():
                        self.run_tbrw()
                        if run_ggl:
                            self.run_ggl()
                        self.endmsg += f'🆔账号{self.num}-{self.name}({self.usid}) 🎉运行完成\n'
                        if self.endcxtb():
                            if self.tj_bchd():
                                if self.uid is not None:
                                    self.wxpusher()
                                    ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                          '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                    ts_all.append(ts)
                                    print(self.endmsg)
                                else:
                                    ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                          '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                    ts_all.append(ts)
                                    print(self.endmsg)
                            else:
                                self.endmsg += '🆔账号{self.num}-{self.name}({self.usid})⛔️获取今日团币失败\n'
                                print(self.endmsg)
                        else:
                            self.endmsg += '🆔账号{self.num}-{self.name}({self.usid})⛔️获取运行后团币失败\n'
                            print(self.endmsg)
                    else:
                        self.endmsg += '🆔账号{self.num}-{self.name}({self.usid})⛔️获取qdtoken失败\n'
                        print(self.endmsg)

                elif isgame and self.ids == []:
                    self.startmsg += f'✅游戏中心已经全部完成！🚀即将运行团币中心任务\n'
                    print(self.startmsg)
                    if self.coin_login():
                        self.run_tbrw()
                        if run_ggl:
                            self.run_ggl()
                        self.endmsg += f'🆔账号{self.num}-{self.name}({self.usid}) 🎉运行完成\n'
                        if self.endcxtb():
                            if self.tj_bchd():
                                if self.uid is not None:
                                    self.wxpusher()
                                    ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                          '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                    ts_all.append(ts)
                                    print(self.endmsg)
                                else:
                                    ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                          '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                    ts_all.append(ts)
                                    print(self.endmsg)
                    else:
                        self.endmsg += f'🆔账号{self.num}-{self.name}({self.usid})⛔️获取qdtoken失败\n'
                        print(self.endmsg)
                else:
                    self.startmsg += f'💔游戏中心获取任务失败！停止运行！\n'
                    print(self.startmsg)
            else:
                self.startmsg += '⛔️获取运行前团币失败\n'
                print(self.startmsg)
        else:
            self.startmsg += '⛔️️登录失败️\n'
            print(self.startmsg)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    print = partial(print, flush=True)
    msg = """
🔔当前版本V1.11
tg频道: https://t.me/dzr_byg
授权找机器人
更新日志:
    1、更新看注释！！！更新看注释！！！更新看注释！！！
    """
    print(msg)

    token = os.environ.get(blname)

    if token is None:
        print(f'⛔️未获取到ck变量：请检查变量是否填写')
        exit(0)
    if zdyfg in token:
        tokens = token.split(zdyfg)
    else:
        tokens = [token]

    print(f'✅获取到{len(tokens)}个账号')

    bf = os.environ.get("bd_xtbbf")
    if bf is None:
        print(f'⛔️为设置并发变量，默认1')
        bf = 5
    else:
        bf = int(bf)
        print(f'✅设置最大并发数: {bf}')

    km = os.environ.get("bd_xtbkm")
    if km is None:
        print(f'✅授权模式运行')
    else:
        print(f'✅卡密模式运行')

    if isprint:
        print(f'✅开启详细日志')
    else:
        print(f'⛔️未开启详细日志')

    if isdl:
        if proxy_api_url != '':
            print(f'✅开启代理api运行')
            start_dlapi()
        elif proxy_url != '':
            print(f'✅开启代理池运行')
        else:
            print(f'⛔️未填入代理')
            exit(0)
    else:
        print(f'⛔️未开启代理运行')

    ts_all = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(bf)) as executor:
        print(f'======================================')
        for num in range(len(tokens)):
            runzh = num + 1
            if len(tokens[num].split("#")) == 2 and "UID" in tokens[num]:
                print(f'🆔账号{runzh} 好像没加uuid，请添加后再运行！\n')
            elif len(tokens[num].split("#")) == 2 and "UID" not in tokens[num]:
                run = Mttb(runzh, tokens[num])
                executor.submit(run.main)
            elif len(tokens[num].split("#")) == 3:
                run = Mttb(runzh, tokens[num])
                executor.submit(run.main)
            elif len(tokens[num].split("#")) == 1:
                print(f'🆔账号{runzh} 好像没加uuid，请添加后再运行！\n')
            time.sleep(random.randint(2, 5))

    if wxpusher_alluid == '':
        stop_event.set()
        pass
    else:
        stop_event.set()
        ts_qb(ts_all)
