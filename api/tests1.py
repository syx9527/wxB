import json
import re
import uuid

import requests
from lxml.etree import HTML

# user = BasicsUserInfo.objects.get(id_number="533122199811201414")
# user1 = UserInfo.objects.get(basics_info=user)
# res = AdminUserInfo.objects.create(user_info=user1, admin_id=user.id_number[-6:], admin_post=user.is_admin)
# print(res)
from api.models import Areas

# Create your tests here.
# openid = "5555"
# UserInfo.objects.create(openid=openid)
# UserInfo.objects.get(openid=)
# BasicsUserInfo.objects.create(name="邵曰信", idNumber="533122199811201414",
#                               native="云南", address="云南省108")

uuid.uuid4()

# for i in range(15, 70):
#     user = BasicsUserInfo.objects.create(name="邵", id_number=f"5331221998112015{i}",
#                                          native="云", address="南")
#     UserInfo.objects.create(openid=uuid.uuid4(), nickName="5", avatarUrl="https://thirdwx.qlogo.cn/", is_valid=True,
#                             basics_info=user)

# user = UserInfo.objects.values()
# for i in user:
#     print(i)

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
}

init_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020"
depth = 0
max_depth = 3


def rget_html(url):
    req = requests.get(url, headers=headers)
    req.encoding = 'GBK'  # 中文解码
    return req.text


def get_id(s):
    res = re.findall(r'(\d+)\.html$', s)
    if not res:
        res = None
    else:
        res = res[0]

    return res


data = []

response = rget_html(init_url)
res = HTML(response)
res = res.xpath('//tr[@class="provincetr"]/td/a')
for i in res:
    item = {}
    url = i.xpath("./@href")[0]
    text = i.xpath("./text()")[0]
    value = get_id(url)
    item['text'] = text
    item['value'] = value
    item["children"] = []
    url_1 = init_url + "/" + url

    # print(item)
    print(value, text)

    area_1 = Areas.objects.create(id=int(value), name=text)

    response = rget_html(url_1)
    res = HTML(response)
    res = res.xpath('//tr[@class="citytr"]/td[2]/a')
    for j in res:
        next_item = {}
        url = j.xpath("./@href")[0]
        text = j.xpath("./text()")[0]
        value = get_id(url)
        next_item['text'] = text
        next_item['value'] = value
        next_item["children"] = []
        url_2 = init_url + "/" + url

        area_2 = Areas.objects.create(id=int(value), name=text, pid=area_1)

        response = rget_html(url_2)
        res = HTML(response)
        res = res.xpath('//tr[@class="countytr"]/td[2]/a')
        for k in res:
            last_item = {}
            url = k.xpath("./@href")[0]
            text = k.xpath("./text()")[0]
            value = get_id(url)
            last_item['text'] = text
            last_item['value'] = value
            # last_item["children"] = []
            next_url = init_url + "/" + url

            area_3 = Areas.objects.create(id=int(value), name=text, pid=area_2)

            next_item["children"].append(last_item)
            # print(last_item)

        item["children"].append(next_item)
    data.append(item)
    print(item)

json_str = json.dumps(data, ensure_ascii=False)

with open("test_data.json", "w", encoding="utf-8") as f:
    f.write(json_str)
