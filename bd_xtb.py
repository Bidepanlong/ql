"""
time：2024.4.19
定时：一天一次就行了
new Env('团币自备接口版本')
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
import requests.utils
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
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# 自己设备的接口穿透的 ip:port
km = '127.0.0.1:12345'

# 无法获取id的是否使用内置id直接运行！慎用！默认关闭！
nzidrun = False

# 活动开关 True/False
# 果园刮刮乐
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

# 今日团币默认大于900就不跑任务了
jrtb_nums = os.environ.get("bd_jrtbnums")
if jrtb_nums is None:
    jrtb_nums = 900
else:
    jrtb_nums = int(jrtb_nums)

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
# isdl = os.environ.get("bd_isdlt")
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
        self.zw = None
        self.title = None
        self.xslist = None
        self.xs_headers = None
        self.xsid = None
        self.jobId = None
        self.property = None
        self.condition = None
        self.mtgsig = None
        global ts_all
        self.num = zh
        self.coins = None
        try:
            if "UID" in ck:
                self.ck = ck.split('#')[0]
                self.uuid = ck.split('#')[1]
                self.uid = ck.split('#')[2]
            else:
                self.ck = ck.split('#')[0]
                self.uuid = ck.split('#')[1]
                self.uid = None
        except:
            print(f'⛔️⛔️⛔️⛔️⛔️⛔️⛔️⛔️账户{self.num}异常!!!')
            exit(0)
        self.ddmsg = None
        self.lisss = None
        self.lastGmtCreated = None
        self.qdrwids = [10002, 10024, 10041, 10015, 10014]
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
        self.noids = [15169, 15170, 15171, 15172, 15173]
        self.id = None
        self.tid = None
        self.data_list = None
        self.mtbb = 'meituan'
        self.platform = xxsz
        self.gglactoken = None
        self.ggl_list = None
        self.gglid = None
        self.cardId = None

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

    def login(self):
        try_count = 5
        while try_count > 0:
            try:
                url = "https://open.meituan.com/user/v1/info/auditting?fields=auditAvatarUrl%2CauditUsername"
                h = {
                    'Connection': 'keep-alive',
                    'Origin': 'https://mtaccount.meituan.com',
                    'User-Agent': self.ua,
                    'token': self.ck,
                    'Referer': 'https://mtaccount.meituan.com/user/',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,en-US;q=0.9',
                    'X-Requested-With': 'com.sankuai.meituan',
                }
                r = requests.get(url, headers=h)
                # print(r.text)
                if 'username' in r.text:
                    rj = r.json()
                    self.name = rj["user"]["username"]
                    self.usid = rj["user"]["id"]
                    self.zw = self.sc_zw()
                    self.startmsg += f'🆔账号{self.num}-{self.name}({self.usid}) ✅登录成功！\n'
                    return True
                elif '失败' in r.text:
                    return False
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num} 登录失败：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num} 登录异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
                continue

    def Getmtgsig_data(self, urls, headers, body):
        try_count = 5
        while try_count > 0:
            try:
                encoded_data = base64.b64encode(body.encode('utf-8'))
                bodybase64 = encoded_data.decode('utf-8')
                data = {
                    'km': km,
                    'usid': self.usid,
                    'method': 'POST',
                    'url': urls,
                    'ua': self.ua,
                    'bbody': bodybase64
                }
                r = requests.post('http://bedee.top:12333/mtgsig', json=data)
                if '成功' in r.text and r.json()['usid'] == self.usid:
                    if isprint:
                        print(f'🆔账号{self.num}-{self.name} {r.json()["msg"]}')
                    self.mtgsig = r.json()['mtgsig']
                    headers['mtgsig'] = self.mtgsig
                    if isdl:
                        r = requests.post(url=urls, headers=headers, data=body, timeout=10, verify=False,proxies=proxy)
                    else:
                        r = requests.post(url=urls, headers=headers, data=body, timeout=10, verify=False)
                    return r
                elif '失败' in r.text:
                    print(r.json()['msg'])
                    return False
                elif r.json()['usid'] != self.usid:
                    print(f'🆔账号{self.num}-{self.name} 请求异常,返回的参数不对！\n')
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
                else:
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except Exception as e:
                try_count -= 1
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 请求异常,还有{try_count}次重试机会\n'
                time.sleep(random.randint(3, 8))
                if try_count == 0:
                    print(f'🆔账号{self.num}-{self.name} 结束运行~')
                    return False

    def sc_zw(self):
        # 设置加密秘钥和加密Iv
        key = b'kwBq8snI'
        iv = b'kwBq8snI'

        # 转换加密内容为字节类型
        data = b'{"A32":[],"A38":42,"A14":"AA\\u003d\\u003d\\n","A53":"1200190209","A23":"MOLY.LR13.R1.TC8.SP.V2.P59,MOLY.LR13.R1.TC8.SP.V2.P59","A16":97.0,"A21":"Unplugged","A29":1710463703,"A10":"Redmi","A48":"Redmi/begonia/begonia:11/RP1A.200720.011/V12.5.6.0.RGGCNXM:user/release-keys","A8":"RP1A.200720.011","A12":"unknown","A51":"DP","A25":[],"A56":"xiaomi","A33":8,"A20":"2000000","A4":"aarch64","A18":"Redmi Note 8 Pro","A26":"1080,2220","A19":440,"A52":"DP","A54":"3.14159265358979323846264338327950288419716939937510","A40":1710654956463,"A7":"unknown","A35":{"hashInfo":[],"number":0},"A24":"unknown","A34":"unknown","A41":1710857434000,"A3":"unknown","A28":1710857983443,"A57":"////PwAAAgAQAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\u003d\\n","A36":null,"A42":1,"A9":"unknown","A55":"428410883","A1":"android","A30":{"hashInfo":[],"number":0},"A11":"WIFI","A15":"","A37":"com.android.browser-com.android.calendar-com.android.camera-com.android.contacts-com.android.contacts-com.android.deskclock-com.android.fileexplorer-com.android.mms-com.android.settings-com.android.thememanager","A22":"11","A13":"unknown","A43":"1230768000000","A5":"dpsheb275afb5fc715339061ebc6571adfccatpu","A44":0,"A6":1,"A2":1710857982866,"A45":5,"A49":"DP","A46":"97460768768@118164561920","A39":"com.android.soundrecorder-com.miui.calculator-com.xiaomi.scanner-bin.mt.plus-com.guoshi.httpcanary.premium-com.jingdong.app.mall-com.jmxxqyand.bingcheng-com.junge.algorithmAide-com.meituan.turbo-com.miui.screenrecorder","A27":0.0,"A50":"000000000000016066FDF138B43928771EF787713DCF1A171003093481310199","A47":"unknown","A31":[],"A17":[]}'

        # 将data解码为字符串
        data_str = data.decode('utf-8')

        # 将字符串转换为JSON对象
        json_obj = json.loads(data_str)

        json_obj['A29'] = int(time.time() - random.randint(100, 300))
        json_obj['A2'] = int(time.time() * 1000.0000001)
        json_obj['A28'] = json_obj['A2'] + random.randint(280, 300)
        json_obj['A40'] = int(time.time() * 1000 - random.randint(4000, 5000))
        a = random.randint(12345678911, 98765432101)
        b = random.randint(123456789102, 987654321012)
        json_obj['A46'] = f'{a}@{b}'
        json_obj['A50'] = self.uuid
        # json_obj['A36']['latitude'] = round(random.uniform(29.6067111, 29.6067999), 7)
        # json_obj['A36']['longitude'] = round(random.uniform(94.3670111, 94.3670999), 7)
        updated_data = json.dumps(json_obj).replace(", ", ",").replace(": ", ":").replace("=", "\\u003d").encode(
            'utf-8')
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(updated_data) + padder.finalize()
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
        lines = [encoded_data[i:i + 76] for i in range(0, len(encoded_data), 76)]
        formatted_data = '\n'.join(lines)
        if len(lines[-1]) < 76:
            formatted_data += '\n'
        # formatted_data = formatted_data.replace('\n', '\\n')
        return formatted_data

    def act(self):
        try_count = 5
        while try_count > 0:
            try:
                url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login?yodaReady=h5&csecplatform=4&csecversion=2.3.1'
                h = {
                    'accessToken': '',
                    'Accept': 'application/json, text/plain, */*',
                    'Content-Length': '307',
                    'x-requested-with': 'XMLHttpRequest',
                    'User-Agent': self.ua,
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Cookie': f'token={self.ck}'
                }
                sing = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                data = {
                    "mtToken": self.ck,
                    "deviceUUID": self.uuid,
                    "mtUserId": self.usid,
                    "idempotentString": sing
                }
                # body = json.dumps(data)
                # r = self.Getmtgsig_data(url, h, body)
                if isdl:
                    r = requests.post(url, headers=h, json=data, timeout=10, verify=False)
                else:
                    r = requests.post(url, headers=h, json=data, timeout=10, verify=False)
                if r.json()['data']['loginInfo']['accessToken'] is not None:
                    self.actoken = r.json()['data']['loginInfo']['accessToken']
                    return True
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

    def get_mtgsig(self, urls, body):
        try_count = 5
        while try_count > 0:
            try:
                encoded_data = base64.b64encode(body.encode('utf-8'))
                bodybase64 = encoded_data.decode('utf-8')
                data = {
                    'km': km,
                    'usid': self.usid,
                    'method': 'POST',
                    'url': urls,
                    'ua': self.ua,
                    'bbody': bodybase64
                }
                r = requests.post('http://bedee.top:12333/mtgsig', json=data)
                if '成功' in r.text and r.json()['usid'] == self.usid:
                    if isprint:
                        print(f'🆔账号{self.num}-{self.name} {r.json()["msg"]}')
                    return r.json()['mtgsig']
                elif '卡密次数不足' in r.text or '失败' in r.text:
                    print(r.json()['msg'])
                    return False
                elif r.json()['usid'] != self.usid:
                    print(f'🆔账号{self.num}-{self.name} 请求异常,返回的参数不对！\n')
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
                else:
                    try_count -= 1
                    time.sleep(random.randint(3, 8))
                    continue
            except Exception as e:
                try_count -= 1
                if isprint:
                    self.endmsg += f'🆔账号{self.num}-{self.name} 请求异常,还有{try_count}次重试机会\n'
                time.sleep(random.randint(3, 8))
                if try_count == 0:
                    print(f'🆔账号{self.num}-{self.name} 结束运行~')
                    return False

    def get_ids(self):
        try_count = 5
        while try_count > 0:
            try:
                url = f'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/queryMgcTaskInfo?yodaReady=h5&csecplatform=4&csecversion=2.3.1'
                data = {
                    'externalStr': '',
                    'riskParams': {
                        'uuid': self.uuid,
                        "platform": self.platform,
                        "fingerprint": self.zw,
                        "version": "12.19.209",
                        "app": 0,
                        "cityid": "351"
                    },
                    'gameType': 10102
                }
                body = json.dumps(data, separators=(',', ':'))  # 压缩数据去空格
                mtgsig = self.get_mtgsig(url, body)
                h = {
                    "Host": "game.meituan.com",
                    "Connection": "keep-alive",
                    "Content-Length": "2401",
                    'accessToken': '',
                    "mtgsig": mtgsig,
                    "User-Agent": self.ua,
                    "Content-Type": "application/json;charset=UTF-8",
                    "Accept": "application/json, text/plain, */*",
                    "x-requested-with": "XMLHttpRequest",
                    "actoken": self.actoken,
                    'mtoken': self.ck,
                    "Origin": "https://mgc.meituan.com",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    # "Referer": f"https://mgc.meituan.com/h5/gamehallv2.html?inner_source=10102_ch290&f=android&token=AgFXIxdLTEtVLswl3aJH_Vh80Q79nmM7UFeewkfVFXBL4Qwx9ZaXjnd5zLh_CUJkm--dHQ-0l9jH1QAAAAC1HgAAcdk87pFda7nvWTIk0vcHu81tNStEfzIUvuJzRYLp_goE4K6L2zIuCPaPfJ5TUhfS&userid=4208094795&utm_source=xiaomi&utm_medium=android&utm_term=1200190207&version_name=12.19.207&utm_content=38a5cc27b89946099157f5d8488f40f9a171003093481337514&utm_campaign=AgroupBgroupC0D300E0Gmine&ci=351&msid=38a5cc27b89946099157f5d8488f40f9a1710030934813375141710654811064&uuid=000000000000016066FDF138B43928771EF787713DCF1A171003093481310199&p_appid=10",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": f"token={self.ck};mt_c_token={self.ck};uuid={self.uuid}"
                }
                if isdl:
                    r = requests.post(url, headers=h, data=body, timeout=10, verify=False,proxies=proxy)
                else:
                    r = requests.post(url, headers=h, data=body, timeout=10, verify=False)
                rj = r.json()
                if rj['msg'] == 'ok' and rj['data']['taskList'] != []:
                    self.data_list = rj['data']['taskList']
                    return True
                elif not rj['data']['taskList']:
                    return False
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num}-{self.name} 获取游戏任务异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except Exception as e:
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
                    'Cookie': f'token={self.ck}'
                }
                if isdl:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False)

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
                    'Cookie': f'token={self.ck}'
                }
                if isdl:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False)
                else:
                    r = requests.get(url, headers=self.t_h, timeout=10, verify=False)
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
                    r = requests.get(url, headers=self.t_h, params=params, timeout=10, verify=False)
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
                    'Cookie': f'token={self.ck}'
                }
                data = {
                    "taskId": self.id,
                    "externalStr": "",
                    "riskParams": {
                        "uuid": self.uuid,
                        "platform": 4,
                        "fingerprint": self.zw,
                        "version": "12.19.209",
                        "app": 0,
                        "cityid": "351"
                    },
                    "gameType": 10102
                }
                body = json.dumps(data)
                r = self.Getmtgsig_data(
                    'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/receiveMgcTaskReward?yodaReady=h5&csecplatform=4&csecversion=2.3.1',
                    headers, body)
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
                    'Cookie': f'token={self.ck}',
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
                    # 'mtgsig': get_xsmtg(),
                }
                if isdl:
                    r = requests.get('https://game.meituan.com/coin-marketing/login/loginMgc', headers=headers,
                                     params=params, timeout=10, verify=False)
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
                    # 'mtgsig': get_xsmtg(),
                }
                data = {
                    "protocolId": self.qdid,
                    "data": {},
                    "riskParams": {
                        "ip": "",
                        "uuid": self.uuid,
                        "platform": self.platform,
                        "version": "12.19.209",
                        "app": 0,
                        "fingerprint": self.zw,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken
                }
                if self.qdid == 10024:
                    while True:
                        if isdl:
                            r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                              json=data, params=params, timeout=10, verify=False)
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
                                              params=params, timeout=10, verify=False)
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
                                          params=params, timeout=10, verify=False)
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
                    # 'mtgsig': get_xsmtg(),
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
                        "version": "12.19.209",
                        "app": 0,
                        "fingerprint": self.zw,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken,
                }
                if isdl:
                    r = requests.post('https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                                      json=data,
                                      params=params, timeout=10, verify=False)
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
                    # 'mtgsig': get_xsmtg(),
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
                        "version": "12.19.209",
                        "app": 0,
                        "fingerprint": self.zw,
                        "cityId": "351"
                    },
                    "acToken": self.qdactoken,
                    "mtToken": self.ck
                }
                if isdl:
                    r = requests.post(
                        'https://game.meituan.com/coin-marketing/msg/post', headers=headers,
                        json=get_data,
                        params=params, timeout=10, verify=False
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
                    # 'mtgsig': get_xsmtg(),
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
                        "version": "12.19.209",
                        "app": 0,
                        "fingerprint": self.zw,
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

    def runq_jrtb(self):
        try_count = 5
        while try_count > 0:
            try:
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
                    r = requests.get(url, headers=headers, timeout=10, verify=False)
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
                                r = requests.get(url1, headers=headers, timeout=10, verify=False)
                            else:
                                r = requests.get(url1, headers=headers, timeout=10, verify=False)
                            # if isprint:
                            #     print(r.json())
                            #     print()
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
                                    self.startmsg += f'💰今日团币: {coins}\n'
                                    return True
                            elif 'ok' in r.text and r.json()['data'] == []:
                                self.coins = coins
                                self.endmsg += f'💰今日团币: {coins}\n'
                                return True
                            else:
                                if isprint:
                                    self.startmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                                try_count -= 1
                                time.sleep(random.randint(2, 5))
                                continue
                        else:
                            self.coins = coins
                            self.startmsg += f'💰今日团币: {coins}\n'
                            return True
                    break
                else:
                    if isprint:
                        self.startmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                    try_count -= 1
                    time.sleep(random.randint(2, 5))
                    continue
            except:
                if isprint:
                    self.startmsg += f'🆔账号{self.num}-{self.name} 获取今日团币异常：还有{try_count - 1}次重试机会\n'
                try_count -= 1
                time.sleep(random.randint(2, 5))
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
                    r = requests.get(url, headers=headers, timeout=10, verify=False)
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
                                r = requests.get(url1, headers=headers, timeout=10, verify=False)
                            else:
                                r = requests.get(url1, headers=headers, timeout=10, verify=False)
                            # if isprint:
                            #     print(r.json())
                            #     print()
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

    def run_game2(self):
        i_num = 0
        for i in self.ids:
            zong = len(self.ids)
            self.id = i
            if self.id in self.noids:
                pass
            else:
                if self.id in [386, 510, 511, 332]:
                    i_num += 1
                    a = 0
                    while a < 5:
                        a += 1
                        if isprint:
                            print(
                                f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id} 第{a}次')
                        if self.get_game():
                            self.post_id()
                            continue
                        else:
                            break
                    continue
                else:
                    i_num += 1
                    if isprint:
                        print(
                            f'\n🆔账号{self.num}-{self.name}({self.usid}) 任务{i_num}/{zong} id: {self.id}')
                    if self.get_game():
                        self.post_id()
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
        # self.llid = 17622
        # if self.get_ll():
        #     self.post_ll()
        #     self.qdid = 10014
        #     self.qd()
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
            'Cookie': f'token={self.ck}'
        }
        if isdl:
            r = requests.get(url, headers=h, timeout=10, verify=False)
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
                    'Cookie': f'token={self.ck}'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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
                    'Cookie': f'token={self.ck}'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'scratchSource': '1',
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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
                    'Cookie': f'token={self.ck}'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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
                    'Cookie': f'token={self.ck}'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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
                    'Cookie': f'token={self.ck}'
                }
                sjc = int(time.time() * 1000.0000001)
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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
                    'Cookie': f'token={self.ck}'
                }
                params = {
                    'yodaReady': 'h5',
                    'csecplatform': '4',
                    'csecversion': '2.3.1',
                    # 'mtgsig': get_xsmtg(),
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

    def main(self):
        if self.login():
            if self.act():
                if self.startcxtb():
                    if self.coin_login():
                        self.runq_jrtb()
                        if self.coins > jrtb_nums:
                            self.startmsg += f'🚀今日团币已经达到{jrtb_nums}不再运行！\n'
                            self.endmsg += f'🆔账号{self.num}-{self.name}({self.usid}) 🎁今天已经跑过啦\n'
                            if self.endcxtb():
                                if self.tj_bchd():
                                    if self.uid is not None:
                                        self.wxpusher()
                                        ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                              '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                        ts_all.append(ts)
                                        print(f'{self.startmsg}{self.endmsg}')
                                    else:
                                        ts = {'序号': self.num, '用户': self.name, '今日团币': self.coins,
                                              '总共团币': f'{int(self.wcxtb)}({int(self.wcxtb) / 1000}元)'}
                                        ts_all.append(ts)
                                        print(f'{self.startmsg}{self.endmsg}')
                        else:
                            isgame = self.get_new_gameid()
                            if isgame and self.ids != []:
                                # if 717 not in self.ids:
                                #     self.game_gift()
                                self.startmsg += f'✅游戏中心获取任务成功！🚀即将运行所有任务\n'
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
                            elif isgame and self.ids == []:
                                self.startmsg += f'✅游戏中心已经全部完成！🚀即将运行小说和团币中心任务\n'
                                print(self.startmsg)
                            else:
                                if nzidrun:
                                    self.ids = [15610, 15224, 15293, 15604, 15813, 15177, 15601, 15605, 15326, 15837,
                                                15458,
                                                15457,
                                                15603, 15606, 15324, 15810, 15607, 15618, 16656, 15608, 16498, 15169,
                                                15609,
                                                15302,
                                                15171, 15172, 15282, 15287, 15173, 323, 330, 507, 509, 672, 768]
                                    self.startmsg += f'⛔️游戏中心获取任务失败，使用内置id！🚀即将运行游戏中心任务和团币中心任务\n'
                                    print(self.startmsg)
                                    self.run_game2()
                                else:
                                    self.startmsg += f'⛔️游戏中心获取任务失败，未开启内置id运行!🚀即将运行团币中心任务\n'
                                    print(self.startmsg)
                            if self.get_xslist():
                                self.run_xsrw()
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
                else:
                    self.startmsg += '⛔️获取运行前团币失败\n'
                    print(self.startmsg)
            else:
                self.startmsg += '⛔️获取act失败\n'
                print(self.startmsg)
        else:
            self.startmsg += '⛔️️登录失败️\n'
            print(self.startmsg)

    def get_xslist(self):
        self.xs_headers = {
            # "retrofit_exec_time": self.timestamp_milliseconds(),
            "Referer": "https://msc.meituan.com/73a62054aadc4526/6227/service",
            "User-Agent": self.ua,
            "M-SHARK-TRACEID": "101000000000000038E9FFD887F741C5BCE0A6A3F9D849C2A16592906xdrw3528218cdd781702178856961163393",
            "Accept-Encoding": "gzip",
            "clientVersion": "1.2.0",
            "uuid": self.uuid,
            "platform": "4",
            "yodaVersion": "1.18.0.179",
            "appVersion": "12.19.209",
            "token": self.ck,
            "clientType": "android",
            "yodaReady": "native",
            "appType": "group",
            "novelScene": "0199",
            "adBookId": "2611385",
            "Content-Type": "application/json",
            "Host": "web.meituan.com",
            "Connection": "Keep-Alive",
        }
        r = requests.get('https://web.meituan.com/novel/marketing/task/listV2?clientAppVersion=6',
                         headers=self.xs_headers)
        # r = requests.get('https://web.meituan.com/novel/marketing/task/listV2',
        #                  headers=self.xs_headers)
        if '操作成功' in r.text:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) 获取小说任务成功！')
            self.xslist = r.json().get('data', None)
            time.sleep(random.randint(1, 3))
            return True
        else:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ⛔️获取小说任务失败！')
            time.sleep(random.randint(1, 3))
            return False

    def get_xsid(self):
        headers = {
            # "retrofit_exec_time": self.timestamp_milliseconds(),
            "Referer": "https://msc.meituan.com/73a62054aadc4526/6227/service",
            "User-Agent": self.ua,
            "M-SHARK-TRACEID": "101000000000000038E9FFD887F741C5BCE0A6A3F9D849C2A16592906xdrw3528218cdd781702178856961163393",
            "Accept-Encoding": "gzip",
            "clientVersion": "1.2.0",
            "uuid": self.uuid,
            "platform": "4",
            "yodaVersion": "1.18.0.179",
            "appVersion": "12.19.204",
            "token": self.ck,
            "clientType": "android",
            "yodaReady": "native",
            "appType": "group",
            "novelScene": "0199",
            "adBookId": "2611385",
            "Content-Type": "application/json",
            "Host": "web.meituan.com",
            # "mtgsig": "{'a1': '1.1', 'a2': 1705210566109, 'a3': '1705207770058CCSCKCCe67dcc3e61b3db1bf3f9e3b1c7aaaa883129', 'a5': 'p/q6y/VVJya//sJFOQVZjbVFgnuAD+P4', 'a6': 'hs1.4cc8P/oEcPnEVSLCbPATiLpS/SEx2PtOn9gl+fy5ugnXN+jI26oGzQDexAB7AKBL9MLQa+3hdYp5R8FyGDs76Fv/+b3RfNGzp7WOMiJ5fH+ELoJEuxPK7r5F/RZ6ZuFZIYoBAe2hzCchU/UuxEUHIpHgO6MyqfhNJScPSO8BBhZRQXRwFJ+SqvkC2oiYtSpTCS+KojN+3plAj5fjDq8yPGj8pcC2Vv2m6Ri0Ujwa3VxhF1b5vS7KTnhmLX6kwDn8BF2OHCXcEd6j33djG3D8PoYgU/TwPq1rHNKkbX0GM3TrYc3edu3k4a0S0jbyQLr+4bhZ0SkiV5Ie03wu/lMksW7ECNwnxNJtJPIs7pJprLrc=', 'x0': 4, 'd1': '693c48f536c46dd0da9991745ff82524'}",
            "Connection": "Keep-Alive",
        }
        data = {
            'jobId': self.jobId,
            'property': self.property,
            'fingerprint': self.zw,
        }
        # r = requests.post('https://web.meituan.com/novel/marketing/task', headers=headers, json=data)
        data = json.dumps(data)
        r = self.Getmtgsig_data('https://web.meituan.com/novel/marketing/task', headers, data)

        if '操作成功' in r.text:
            self.xsid = r.json()['data']['taskId']
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) 获取小说id✅成功{self.jobId}({self.xsid}) {r.json()}')
            time.sleep(random.randint(1, 3))
            return True
        else:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ⛔️获取小说id失败{self.jobId} {r.json()}')
            time.sleep(random.randint(1, 3))
            return False

    def get_xsrw(self):
        self.xs_headers = {
            # "retrofit_exec_time": self.timestamp_milliseconds(),
            "Referer": "https://msc.meituan.com/73a62054aadc4526/6227/service",
            "User-Agent": self.ua,
            "M-SHARK-TRACEID": "101000000000000038E9FFD887F741C5BCE0A6A3F9D849C2A16592906xdrw3528218cdd781702178856961163393",
            "Accept-Encoding": "gzip",
            "clientVersion": "1.2.0",
            "uuid": self.uuid,
            "platform": "4",
            "yodaVersion": "1.18.0.179",
            "appVersion": "12.19.209",
            "token": self.ck,
            "clientType": "android",
            "yodaReady": "native",
            "appType": "group",
            "novelScene": "0199",
            "adBookId": "2611385",
            "Content-Type": "application/json",
            "Host": "web.meituan.com",
            "Connection": "Keep-Alive",
        }
        if self.title == '听书赚美团币':
            url = 'https://web.meituan.com/novel/marketing/task/audio/process'
            data = {
                'process': self.condition,
                'fingerprint': self.zw,
                'audioPartnerType': 1,
                'taskProperty': 4
            }
        else:
            url = 'https://web.meituan.com/novel/marketing/task/process'
            data = {
                'taskId': f"{self.xsid}",
                'process': self.condition,
                'fingerprint': self.zw,
            }
        # r = requests.post('https://web.meituan.com/novel/marketing/task/process', headers=self.xs_headers, json=data)

        data = json.dumps(data)
        r = self.Getmtgsig_data(url, self.xs_headers, data)

        if '操作成功' in r.text:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ✅领取{self.xsid}成功 {r.json()}')
            time.sleep(random.randint(1, 3))
            return True
        else:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ⛔️领取{self.xsid}失败 {r.json()}')
            time.sleep(random.randint(1, 3))
            return False

    def post_xsrw(self):
        data = {
            'taskId': f"{self.xsid}",
            'fingerprint': self.zw,
        }
        # r = requests.post('https://web.meituan.com/novel/marketing/task/coin', headers=self.xs_headers, json=data)
        data = json.dumps(data)
        r = self.Getmtgsig_data('https://web.meituan.com/novel/marketing/task/coin', self.xs_headers, data)
        if '操作成功' in r.text:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ✅完成{self.xsid}成功 {r.json()}')
            time.sleep(random.randint(1, 3))
            return True
        else:
            if isprint:
                print(
                    f'🆔账号{self.num}-{self.name}({self.usid}) ⛔️完成{self.xsid}失败 {r.json()}')
            time.sleep(random.randint(1, 3))
            return False

    def run_xsrw(self):
        for data in self.xslist:
            zt = data['status']
            self.title = data['title']
            self.xsid = data.get('taskId', None)
            self.jobId = data['jobId']
            self.property = data['property']
            self.condition = data['award']['steps'][-1]['condition']
            if isprint:
                print(
                    f"{self.title} 状态: {zt} taskid:{self.xsid} jobId: {self.jobId} property: {self.property} condition: {self.condition}")
            if zt == 1 or zt == 0:
                if self.get_xsid():
                    time.sleep(random.randint(10, 60))
                    if self.get_xsrw():
                        time.sleep(random.randint(3, 8))
                        self.post_xsrw()
                        time.sleep(random.randint(3, 8))
                        pass
            elif zt == 2:
                if self.get_xsid():
                    time.sleep(random.randint(10, 60))
                    self.post_xsrw()
                    time.sleep(random.randint(3, 8))
            else:
                pass


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    print = partial(print, flush=True)
    msg = """
🔔当前版本V4.19自备接口版
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
        bf = 1
    else:
        bf = int(bf)
        print(f'✅设置最大并发数: {bf}')

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
