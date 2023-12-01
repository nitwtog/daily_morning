import json
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import requests
import json


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
wenxin_key = os.environ["WENXIN_KEY"]
wenxin_secret = os.environ["WENXIN_SECRET"]

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
    url = f'http://v1.yiketianqi.com/api?unescape=1&version=v9&appid={tianqi_id}&appsecret={tianqi_secret}&version=v61&city=%E4%B8%8A%E6%B5%B7&province=%E4%B8%8A%E6%B5%B7'
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



def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
        
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={wenxin_key}&client_secret={wenxin_secret}"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def main(weather, data_info):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": f"""       
现在你要给你的女朋友写一份每日早安，你现在有一个可以参考的很粗糙的模板，如下：

“今天是{{Today.DATA}}，星期{{Week.DATA}}

{{holiday.DATA}}，节气：{{solarTerms.DATA}}

宜：{{ 请注意找出与学习、生活、出行、工作相关的5-6个词语 }}

今年过去{{dayOfYear.DATA}}天，距离你生日还有{{birthday_left.DATA}}天

天气：{{weather.DATA}} ；最高：{{tmp.max}} 最低{{tmp.min}} 

{{对天气信息的描述，给出天气的相关建议}}#简单描述

今天是想你的第{{love_days.DATA}}天

我想说的是：{{words.DATA}}
”
现在你要给你的女朋友写一份每日早安,以下是今天的上海天气情况：
{weather}
    我将一些关键的信息抽取了出来，这些东西是要重点进行描述的
{data_info}
但是你的女朋友觉得你这个模板每天都一样太过于单调了，请对于air_tips.value， 以及 words.value进行改写修正。比如针对天气情况给出更多建议，并且不要使用刻板相同的表达方式，你的女朋友希望每天都能看到一些更有意思的早安。请注意，不要输出其他内容，不要重复问题，直接生成早安内容，不要过多回复。注意，女朋友想要模板之外的更多表达，请不要完全按照粗糙的模板填充内容，给出创意性质生成！注意，不要太肉麻，宜和忌部分适当选用3-5个词，与给出信息相符即可"""
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)
    return response.text



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

wenxin_response = json.loads(main(weather, data))['result']
new_words = []
for word in wenxin_response.split('\n\n'):
    if len(word) > 20:
        new_words.extend([word[i:i+20] for i in range(0,len(word),20)])
    else:
        new_words.append(word)

print_word = {}
for k,i in enumerate(new_words):
    print_word[f'word{k}'] = {"value":i}



print(print_word)
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
res = wm.send_template(user_id, template_id, wenxin_data)
print(res)
