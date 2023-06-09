"""

time：2023.6.9
cron: 40 59 15 * * *
new Env('10点30-15');
自行抓包抢券接口，填写变量，不会抓包进群看群文件有视频。qq群:858019699
bd_mtt = 抓取的完整cookie或者token=xxxxxxxxxxxxxxxx
mtFingerprint抢券按钮抓取的在请求体的参数 变量填写如下
bd_mtf = H5dfp_2.0.0_tttt_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
mtgsig在请求头里面 变量填写如下
bd_mtg = {"a1":"1.1","a2":xxx,"a3":"xxx".......}

"""

import time
import requests
from os import environ, path
from datetime import datetime
from functools import partial
import threading


def load_send():
    global send
    cur_path = path.abspath(path.dirname(__file__))
    if path.exists(cur_path + "/SendNotify.py"):
        try:
            from SendNotify import send
            print("加载通知服务成功！")
        except:
            send = False
            print('加载通知服务失败~')
    else:
        send = False
        print('加载通知服务失败~')


def get_environ(key, default="", output=True):
    def no_read():
        if output:
            print(f"⛔️未填写环境变量 {key} 请添加")
            exit(0)
        return default

    return environ.get(key) if environ.get(key) else no_read()


class Mt30_15():
    def __init__(self, ck, mtg, mtf):
        self.msg = ""
        self.ck = ck
        self.mtg = mtg
        self.mtf = mtf
        self.id = 'DBFA760914E34AFF9D8B158A7BC4D706'
        self.data = {
            "cType": "mti",
            "fpPlatform": 3,
            "wxOpenId": "",
            "appVersion": "",
            "mtFingerprint": self.mtf
        }
        self.headers = {
            'Host': 'promotion.waimai.meituan.com',
            'Connection': 'keep-alive',
            'Content-Length': '2464',
            'sec-ch-ua': 'Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'mtgsig': self.mtg,
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2012K10C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 EdgA/113.0.1774.50',
            'sec-ch-ua-platform': '"Android"',
            'Origin': 'https://market.waimai.meituan.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://market.waimai.meituan.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
            'cookie': self.ck,
        }

    def login(self):
        # 将字符串转换成字典
        cookie_dict = {}
        for c in self.ck.split('; '):
            key, value = c.split('=', 1)
            cookie_dict[key] = value

        # 获取token的值
        token_value = cookie_dict.get('token', None)
        # print(token_value)

        xx_url = "https://open.meituan.com/user/v1/info/auditting?fields=auditAvatarUrl,auditUsername"
        xx_h = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 TitansX/12.9.1 KNB/1.2.0 android/11 mt/com.sankuai.meituan/12.9.404 App/10120/12.9.404 MeituanGroup/12.9.404",
            "token": token_value,
            "Accept": "*/*",
            "Origin": "https://mtaccount.meituan.com",
            "X-Requested-With": "com.sankuai.meituan",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://mtaccount.meituan.com/user/person-info?source=group&f=android&token=AgFCKGlUmmAb3-liWLPLRFREUMN_UfifQmdWqQHkXbtyxiLzWJIggcYhskOuMlDSfJV68o1m3IOSQhEAAAB5GAAAG0mMr3-jFYCqs7hw2m29EtqnOLFuR5LqSHPbbrcle38zF4rNW7g5NV7VIpzwHjs9BNQllh0dfRxUnkXn3uQhFw&userid=2397926276&utm_source=xiaomi&utm_medium=android&utm_term=1200090404&version_name=12.9.404&utm_content=38ce19a7119647ad807dc4a9f79d95bea167834767450734288&utm_campaign=AgroupBgroupC0D200E0Gmine&ci=351&msid=38ce19a7119647ad807dc4a9f79d95bea1678347674507342881684036948278&uuid=0000000000000E24DD29E7937427FB728662DB0BF69CDA167834767461947782&p_appid=10",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            rxx = requests.get(xx_url, headers=xx_h)
            if rxx.status_code == 200:
                xx = f'🚀登录用户：{rxx.json()["user"]["username"]}\n'
                print(xx)
                self.msg += xx
            else:
                xx = rxx.json()
                print(xx)
                exit(0)
        except Exception as e:
            xx = f"⛔️登录异常\n{e}\nck可能失效：{self.ck}\n\n"
            print(xx)
            exit(0)

    def yz(self):
        yz_url = "https://promotion.waimai.meituan.com/lottery/limitcouponcomponent/info"
        params_yz = {
            'couponReferIds': self.id,
            'actualLng': '104.671708',
            'actualLat': '31.049494',
            'geoType': '2',
        }
        headers = {
            'Host': 'promotion.waimai.meituan.com',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2012K10C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 EdgA/113.0.1774.50',
            'sec-ch-ua-platform': '"Android"',
            'Origin': 'https://market.waimai.meituan.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://market.waimai.meituan.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
            'Cookie': self.ck
        }

        try:
            ryz = requests.get(yz_url, headers=headers, params=params_yz)
            if ryz.json()['msg'] == '成功':
                qm = f'{ryz.json()["data"]["couponInfo"][self.id]["couponName"]} 满{ryz.json()["data"]["couponInfo"][self.id]["priceLimit"]}减{ryz.json()["data"]["couponInfo"][self.id]["couponValue"]}'
                xx = f'🎁待抢神券：{qm}\n\n'
                print(xx)
                self.msg += xx
            elif ryz.json()['msg'] == '未登录':
                xx = f'💔登录失败，ck可能失效咯\n当前token：{self.ck}\n\n'
                print(xx)
                exit(0)
        except Exception as e:
            xx = f"⛔️请求异常\n{e}\nck可能失效：{self.ck}\n\n"
            print(xx)
            exit(0)

    def qiang(self):
        qiang_url = "https://promotion.waimai.meituan.com/lottery/limitcouponcomponent/fetchcoupon"
        params = {
            'couponReferId': self.id,
            'actualLng': '104.671692',
            'actualLat': '31.049475',
            'geoType': '2',
            'gdPageId': '306477',
            'pageId': '306004',
            'version': '1',
            'utmSource': '',
            'utmCampaign': 'wmsq-457896',
            'instanceId': '16620226080900.11717750606071209',
            'componentId': '16620226080900.11717750606071209',
        }
        now_time2 = datetime.now()
        sj = now_time2.strftime("%H:%M:%S.%f")
        try:
            rqiang = requests.post(qiang_url, params=params, headers=self.headers, json=self.data)
            if rqiang.status_code == 200:
                if rqiang.json()["msg"] == "抢券成功！":
                    xx = f"⏰当前时间：{sj}\n✅抢券成功！\n\n"
                    print(xx)
                elif rqiang.json()["msg"] == "未登录":
                    xx = f"⏰当前时间：{sj}\n💔ck可能失效啦\n当前token:{self.ck}\n\n"
                    print(xx)
                elif rqiang.json()["msg"] == "已领取":
                    xx = f"⏰当前时间：{sj}\n🎁已领取\n\n"
                    print(xx)
                elif rqiang.json()["msg"] == "来晚了，券抢完了~":
                    xx = f"⏰当前时间：{sj}\n💔来晚了，券抢完了~\n\n"
                    print(xx)
                else:
                    xx = f'⏰当前时间：{sj}\n⛔️{rqiang.json()["msg"]}\n\n'
                    print(xx)
            else:
                xx = f"⏰当前时间：{sj}\n⛔️403⛔️\n\n"
                print(xx)
        except Exception as e:
            xx = f"⏰当前时间：{sj}⛔️请求异常\n{e}\nck可能失效：{self.ck}\n\n"
            print(xx)
            exit(0)

    def jg(self):
        qiang_url = "https://promotion.waimai.meituan.com/lottery/limitcouponcomponent/fetchcoupon"
        params = {
            'couponReferId': self.id,
            'actualLng': '104.671692',
            'actualLat': '31.049475',
            'geoType': '2',
            'gdPageId': '306477',
            'pageId': '306004',
            'version': '1',
            'utmSource': '',
            'utmCampaign': 'wmsq-457896',
            'instanceId': '16620226080900.11717750606071209',
            'componentId': '16620226080900.11717750606071209',
        }
        print(f"🔔开始检查抢券结果🔔\n")
        now_time = datetime.now()
        sj = now_time.strftime("%H:%M:%S.%f")
        q = 0
        while True:
            try:
                rqiang = requests.post(qiang_url, params=params, headers=self.headers, json=self.data)
                if rqiang.status_code == 200:
                    if rqiang.json()["msg"] == "已领取":
                        xx = f'✅抢券成功！\n\n'
                        print(xx)
                        self.msg += xx
                        if send:
                            send("🔔10点美团抢券30-15通知", self.msg)
                        break

                    elif rqiang.json()["msg"] == "来晚了，券抢完了~":
                        xx = f"💔来晚了，券抢完了~\n\n"
                        print(xx)
                        self.msg += xx
                        if send:
                            send("🔔10点美团抢券30-15通知", self.msg)
                        break
                    else:
                        xx = f'️⛔️{rqiang.json()["msg"]}\n\n'
                        print(xx)
                        self.msg += xx
                        if send:
                            send("🔔上午场美团抢券25-12通知", self.msg)
                        break
                else:
                    xx = f"⏰当前时间：{sj}\n⛔️403⛔️\n\n"
                    print(xx)
                    q += 1
                    if q == 5:
                        self.msg += xx
                        if send:
                            send("🔔10点美团抢券30-15通知", self.msg)
                        break
                    continue
            except Exception as e:
                xx = f"⏰当前时间：{sj}⛔️请求异常\n{e}\nck可能失效：{self.ck}\n\n"
                print(xx)
                self.msg += xx
                if send:
                    send("🔔10点美团抢券30-15通知", self.msg)
                break


if __name__ == '__main__':
    print = partial(print, flush=True)
    load_send()
    print("🔔开始美团抢券30-15🔔\n")
    bd_mtt = get_environ("bd_mtt")
    bd_mtg = get_environ("bd_mtg")
    bd_mtf = get_environ("bd_mtf")
    run = Mt30_15(bd_mtt, bd_mtg, bd_mtf)
    run.login()
    run.yz()
    qsj = "09:59:57"
    # qsj = "15:44:08"
    print(f"❗❗❗等待时间达到{qsj}❗❗❗\n")
    while True:
        now_time = datetime.now()
        sjms = now_time.strftime("%H:%M:%S")
        if sjms >= qsj:
            threads = []
            for i in range(40):
                thread = threading.Thread(target=run.qiang)
                thread.start()
                threads.append(thread)
                time.sleep(0.1)
            for i in threads:
                i.join()
            run.jg()
            break
        else:
            continue
