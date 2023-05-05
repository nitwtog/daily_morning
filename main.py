from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

api_id = os.environ["API_ID"]
api_secret = os.environ["API_SECRET"]


def get_holiday():
    url = "https://www.mxnzp.com/api/holiday/single/"+str(today.date()).replace('-','') +f"?app_id={api_id}&app_secret={api_secret}"
    res = requests.get(url).json()
    holiday = res['data']
    result = {"日期":holiday['date'],"星期几": holiday['weekDay'],"天干地支":holiday['yearTips'], "节日":holiday['typeDes'], "宜":holiday['suit'], "忌":holiday['avoid'], "这一年的第几天":holiday['dayOfYear'],"节气":holiday['solarTerms']}
    return result

def get_weather():
  url = "https://www.mxnzp.com/api/weather/current/" + city + f"?app_id={api_id}&app_secret={api_secret}"
  res = requests.get(url).json()
  weather = res['data']
  return weather['weather'], str(weather['temp'])+"度"

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

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


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
holiday = get_holiday()
data = {"weather":{"value":wea},
        "temperature":{"value":temperature},
        "love_days":{"value":get_count()},
        "birthday_left":{"value":get_birthday()},
        "words":{"value":get_words(), "color":get_random_color()},
        "Today":{"value":holiday['日期']},
        "Week":{"value":holiday['星期几']},
        "holiday":{"value":holiday['节日']},
        "suit":{"value":holiday['宜']},
        "avoid":{"value":holiday['忌']},
        "dayOfYear":{"value":str(holiday['这一年的第几天'])+"天"},
        "solarTerms":{"value":holiday['节气']},
        }
print(data)
res = wm.send_template(user_id, template_id, data)
print(res)

