import json
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
birthday = os.environ['BIRTHDAY']
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]
tianqi_id = os.environ["TIANQI_ID"]
tianqi_secret = os.environ["TIANQI_SECRET"]
rili_key = os.environ["RILI_KEY"]
# news_key = os.environ["news_key"]

def get_holiday():
    # date ='-'.join(str(int(i)) for i in str(today.date()).split('-'))
    date = str(today.date())
    url = f"http://apis.juhe.cn/fapig/calendar/day?date={date}&detail=1&key={rili_key}"
    head = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.get(url, headers=head).json()
    return res['result']

def get_weather():
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)'
    }
    # update data 2023年12月2日 由于接口被攻击，运营商更换http协议
    url = f"http://v0.yiketianqi.com/api?appid={tianqi_id}&appsecret={tianqi_secret}&version=v61&city=%E4%B8%8A%E6%B5%B7&province=%E4%B8%8A%E6%B5%B7"
    res = requests.get(url, headers=headers)
    result = json.loads(res.content)
    return result


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

# def get_news():
#     type = 'caijing'
#     page = "1"
#     page_size = "10"

#     url = f"http://v.juhe.cn/toutiao/index?key={news_key}&type={type}&page={page}&page_size={page_size}"
#     head = {'Content-Type': 'application/x-www-form-urlencoded'}
#     res = requests.get(url, headers=head).json()
#     return res['result']
def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


weather = get_weather()
holiday = get_holiday()
if "value" not in holiday:
    holiday['value'] = "无"
# news = get_news()
data = {"now_temp": {"value": weather['tem']},  # 当前天气
        "max_temp": {"value": weather['tem1']},
        "min_temp": {"value": weather['tem2']},
        "weather": {"value": weather['wea']},
        "air_tips": {"value": weather['air_tips']},
        "air_level": {"value": weather['air_level']},
        "love_days": {"value": get_count()},
        "birthday_left": {"value": get_birthday()},
        "words": {"value": get_words(), "color": get_random_color()},
        "Today": {"value": holiday['date']},
        "Week": {"value": holiday['week']},
        "holiday": {"value": holiday['value']},
        "suit": {"value": holiday['suit']},
        "avoid": {"value": holiday['avoid']},
        "statusDesc": {'value': holiday['statusDesc']},
#         "news":{"value":" \n".join([f"{k+1}. "+i['title'] for k,i in enumerate(news["data"])])}
        }
print(data)

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
res = wm.send_template(user_id, template_id, data)
print(res)
