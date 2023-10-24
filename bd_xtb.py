"""

time：2023.10.24
定时：一天至少3-5次
正常是每天700+币
new Env('美团小团币游戏中心');
抓包小程序或者app或者网页的token=Agxxxx  只要token后面的值
环境变量: 名称：bd_mttoken   值：Agxxxxxxxxxx
多账号新建变量或者用 & 分开
并发变量: bd_xtbbf = 1   默认不设置为1

更新日志：
10.24: 关闭授权，开源
9.26: 优化报错，并发变量
9.24: 新增账号并发运行
9.23: 新增每日获取小团币，异常重试

"""
import random
import base64
import os
import requests
import time
import string
from functools import partial
from user_agent import generate_user_agent
import threading


class Mttb:
    def __init__(self, ck, num):
        self.num = num
        self.ck = ck
        self.name = None
        self.name = None
        self.usid = None
        self.actoken = None
        self.xtb = None
        self.wcxtb = None
        self.ids = []
        self.ids1 = []
        self.id = None
        self.tid = None
        self.ua = generate_user_agent(os='android')
        self.t_h = None
        self.msg = ''
        self.start = ''
        self.end = ''

    def main(self):
        if self.login():
            self.act()
            self.cxtb()
            if self.get_ids():
                self.get_id()

    def login(self):
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

            if 'username' in r.text:
                rj = r.json()
                self.name = rj["user"]["username"]
                self.usid = rj["user"]["id"]
                xx = f'😶账号{self.num}\n🆔{self.name}\n'
                self.start += xx
                return True
            else:
                print(r.json())
        except Exception as e:
            print(f'登录异常：{e}')
            exit(0)

    def act(self):
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login'
            h = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Length': '307',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': self.ua,
                'Content-Type': 'application/json;charset=UTF-8',
                'cookie': f'token={self.ck}'
            }
            sing = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            data = {
                "mtToken": self.ck,
                "deviceUUID": '0000000000000A3467823460D436CAB51202F336236F6A167191373531985811',
                "mtUserId": self.usid,
                "idempotentString": sing
            }
            r = requests.post(url, headers=h, json=data)
            if r.json()['data']['loginInfo']['accessToken'] is not None:
                self.actoken = r.json()['data']['loginInfo']['accessToken']
            else:
                print(r.json())
        except Exception as e:
            print(f'获取token异常：{e}')
            exit(0)

    def cxtb(self):
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/skuExchange/resource/counts?sceneId=3&gameId=10102'
            self.t_h = {
                'Accept': 'application/json, text/plain, */*',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': self.ua,
                'Content-Type': 'application/json;charset=UTF-8',
                'mtgsig': '',
                'actoken': self.actoken,
                'mtoken': self.ck,
                'cookie': f'token={self.ck}'
            }
            r = requests.get(url, headers=self.t_h)
            rj = r.json()
            if rj['msg'] == 'ok':
                data = rj['data']
                for d in data:
                    if self.xtb is not None:
                        self.wcxtb = d['count']
                        xx = f'💰当前小团币: {int(self.wcxtb)}({int(self.wcxtb) / 1000}元)\n'
                        self.end += xx
                    else:
                        self.xtb = d['count']
                        xx = f'💰小团币: {int(self.xtb)}({int(self.xtb) / 1000}元)\n'
                        self.start += xx
                        print(self.start)
        except Exception as e:
            print(f'🆔{self.name}>>>⚠️查询团币异常：{e}')

    def get_ids(self):
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/queryMgcTaskInfo'
            data = {
                "externalStr": "",
                "riskParams": {}
            }
            r = requests.post(url, headers=self.t_h, json=data)
            rj = r.json()
            if rj['msg'] == 'ok':
                data_list = r.json()['data']['taskList']
                for i in data_list:
                    self.ids.append(i['id'])
                if self.ids:
                    random.shuffle(self.ids)
                    # print(self.ids)
                    return True
            else:
                print(f'{self.name}>>>获取任务失败！')
        except Exception as e:
            print(f'获取任务异常：{e}')
            exit(0)

    def get_id(self):
        for idd in self.ids:
            self.id = idd
            if self.get_game():
                self.post_id()
        xx = f'😊账号{self.num}\n🆔{self.name}>>>🎉运行完成！\n'
        self.end += xx
        self.cxtb()
        bchd = int(self.wcxtb) - int(self.xtb)
        xx = f'🔔获取小团币: {bchd}\n'
        self.end += xx
        print(self.end)

    def b64(self):
        y_bytes = base64.b64encode(self.tid.encode('utf-8'))
        y_bytes = y_bytes.decode('utf-8')
        return y_bytes

    def get_game(self):
        try:
            self.tid = f'mgc-gamecenter{self.id}'
            self.tid = self.b64()
            url = f'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/finishV2?taskId={self.tid}'
            r = requests.get(url, headers=self.t_h)
            if r.status_code == 200:
                if r.json()['msg'] == 'ok':
                    # print(f'{self.name}>>>{self.id} 领取任务成功！')
                    time.sleep(1)
                    return True
                elif '完成过' in r.text:
                    # print(f'{self.name}>>>{self.id} 完成过领取任务成功！')
                    time.sleep(1)
                    return True
                else:
                    print(f'🆔{self.name}>>>🌚任务状态: {r.text}')
            else:
                print(f'🆔{self.name}>>>请求错误: ', r.status_code)
        except Exception as e:
            print(f'🆔{self.name}>>>⚠️获取任务异常：{e}')

    def post_id(self):
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/receiveMgcTaskReward?yodaReady=h5&csecplatform=4&csecversion=2.1.0&mtgsig={}'
            data = {
                "taskId": self.id,
                "externalStr": "",
                "riskParams": {}
            }
            r = requests.post(url, headers=self.t_h, json=data)
            if r.status_code == 200:
                if r.json()['msg'] == 'ok':
                    # print(f'{self.name}>>>{self.id},完成任务！\n')
                    time.sleep(1)
                elif '异常' in r.text:
                    # print(f'{self.name}>>>{self.id},状态异常，任务不可领奖！\n')
                    time.sleep(1)
                else:
                    print(f'{self.name}>>>{self.id},{r.text}\n')
                    time.sleep(1)
            else:
                print('请求错误!')
        except Exception as e:
            print(f'🆔{self.name}>>>⚠️完成任务异常：{e}')


if __name__ == '__main__':
    print = partial(print, flush=True)
    print('🔔当前版本V10.24\n🔔tg频道：https://t.me/dzr_byg')

    token = os.environ.get("bd_mttoken")
    if token is None:
        print(f'⛔️未获取到ck变量：请检查变量是否填写')
        exit(0)
    if '&' in token:
        tokens = token.split('&')
    else:
        tokens = [token]

    bf = os.environ.get("bd_xtbbf")
    if bf is None:
        print(f'⛔️为设置并发变量，默认1')
        bf = 2

    print(f'✅获取到{len(tokens)}个账号')
    print(f'🔔设置并发数: {bf}')


    def run_account(tk, n):
        run = Mttb(tk, n)
        run.main()


    threads = []
    s_e = []
    for i in range(len(tokens)):
        a = i + 1
        s_e.append(a)
        t = threading.Thread(target=run_account, args=(tokens[i], a,))
        threads.append(t)
        if str(len(threads)) == str(bf):
            print(f'==================⏳账号{s_e[0]}-{s_e[-1]}==================')
            for t in threads:
                t.start()
                time.sleep(5)
            print(f'⏳账号{s_e[0]}-{s_e[-1]}任务运行中！')
            for t in threads:
                t.join()
            threads = []
            s_e = []
            time.sleep(5)
    if threads == [] and s_e == []:
        print(f'🔔全部账号运行完成！！！')
    else:
        print(f'==================账号{s_e[0]}-{s_e[-1]}==================')
        for t in threads:
            t.start()
            time.sleep(3)
        print(f'⏳账号{s_e[0]}-{s_e[-1]}任务运行中！')
        for t in threads:
            t.join()
        threads = []
        s_e = []
        time.sleep(5)
        print(f'🔔全部账号运行完成！！！')
