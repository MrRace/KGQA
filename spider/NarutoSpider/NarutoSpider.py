

"""
从搜狗网站上爬取现有的人物关系网络
https://www.sogou.com/tupu/person.html?q=%E6%97%8B%E6%B6%A1%E9%B8%A3%E4%BA%BA&id=1588852
"""
from urllib import request
from urllib.parse import quote
import string
import time
import json
from bs4 import BeautifulSoup
import codecs
import os
import requests
from queue import Queue


headers = {}
headers[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
headers["Host"]="www.sogou.com"
headers["Accept-Encoding"]="gzip, deflate, br"


"""
初始化id
之后爬取得到的name和id不断添加到set中
"""
q = Queue()

name_id_file = open("files/name_id.txt",'w',encoding='utf-8')

name_id = {}#存放name_id
name_set = set()
name_set.add("旋涡鸣人")
name_id["旋涡鸣人"] = "1588852"

def download_image(url_img, name):
    url = quote(url_img, safe=string.printable)
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    rsp = resp.content# 二进制的内容
    out_file_name = "images/%s.jpg" % name
    with open(out_file_name, 'wb') as file:
        file.write(rsp)
        return True

def get_json():
    """
    每次爬取总能够得到10个name和id,这些是下一个爬取操作需要用到的name。
    采用广度优先。
    :return:
    """
    temp_name_set = set()
    temp_name_set.add("旋涡鸣人")
    num = 0
    q.put("旋涡鸣人")
    num = 0
    while True:
        num = num + 1
        print("iter num=", num)
        print("queue size=", q.qsize())
        if q.qsize() > 0:
            i = q.get()
            #print("queue size=", q.qsize())
            #print(i)
            url = 'https://www.sogou.com/kmap?query=%s&from=relation&id=' % (i)
            # print(url)
            url = quote(url, safe=string.printable)
            # req = request.Request(url, headers=headers)
            # response = request.urlopen(req, timeout=20)
            #mybody = response.read()
            #mycontent = response.content
            resp = requests.get(url, headers=headers)
            #rsp = resp.content # 二进制的内容
            rsp = resp.text # 返回纯文本的内容
            #= resp.content
            #print(len(rsp))
            rsp = rsp[:-1]
            #print(len(rsp))
            json_rsp = json.loads(rsp)
            nodes = json_rsp["nodes"] # 矩阵对象
            print("len nodes=", len(nodes))
            # 由于采用的是广度优先，所以会逐层遍历
            for p in nodes:
                #print(p)
                id = p["id"]
                name = p["name"]
                if name == "纲手":
                    print(i)
                #print("name=",name)
                if name not in name_set:
                    name_set.add(name)
                    name_id[name] = id
                    q.put(name)# 添加到队列中
                    print("put name=", name)
                else:
                    #print("skip name=", name)
                    pass
                w = p["w"]
                baike = p["baike"]
                level = p["level"]
            print("new set size=", len(name_set))
            # # 获取当前节点对象的连接关系
            # links = json_rsp["links"]
            # for lin in links:
            #     f_node = lin["from"]
            #     t_node = lin["to"]
            #     relation_name = lin["name"]
            #     relation_type = lin["type"]
            # recommenders = json_rsp["recommenders"] 首页的推荐内容
            # print(rsp)
            # html = str(resp.content, encoding='utf-8', errors='ignore')
        else:
            break

    print("name num=", len(name_id))
    # 对结果进行保存
    with open("files/names_id.txt", "w", encoding='utf-8') as f:
        for key_name in name_id:
            temp = key_name + "\t" + name_id[key_name] + "\n"
            f.write(temp)


    """
    发现在涡旋鸣人下，纲手有两个：
    "id": "8520544","name": "千手纲手",
    另一个是："id": "877370","name": "纲手",
    其实两个是相同的。
    
    """

def craw_relation():
    """
    爬取人物之间的关系
    :return:
    """
    relation_file = open("files/naruto_relation.txt", 'w', encoding='utf-8')
    name_id_detail_file = open("files/name_id_detail.txt", 'w', encoding='utf-8')
    # 建立name-id的词典映射表
    name_id_dict = {}
    with open("files/names_id.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            name_id = line.strip().split("\t")
            name = name_id[0]
            id = name_id[1]
            name_id_dict[name] = id
        id_name_dict = dict(zip(name_id_dict.values(), name_id_dict.keys()))

    #
    relation_set = set()
    for name_key in name_id_dict:
        name = name_key
        print(name)
        url = 'https://www.sogou.com/kmap?query=%s&from=relation&id=' % (name)
        url = quote(url, safe=string.printable)
        resp = requests.get(url, headers=headers)
        rsp = resp.text  # 返回纯文本的内容
        rsp = rsp[:-1]
        # 获取节点的基本信息
        json_rsp = json.loads(rsp)
        nodes = json_rsp["nodes"]  # 矩阵对象
        if len(nodes) <= 0:
            print("name=%s nodes is empty,id=%s" % (name, name_id_dict[name]))
        else:
            p = nodes[0]# 只获取当前
            if "img" in p:
                img = p["img"]  # 下载图片
                download_image(img, name)
            else:
                print("name=%s miss img part" % name)
            if "intro" in p:
                intro = p["intro"]  # 该字段并不是都有，只是作为主节点的时候会有
            else:
                intro = ""
                print("name=%s miss intro part" % name)
            detail_msg = name + "\t" + name_id_dict[name] + "\t" + intro + "\n"
            name_id_detail_file.write(detail_msg)
        # 获取当前节点对象的连接关系
        links = json_rsp["links"]
        for lin in links:
            f_node = lin["from"] # 该关系的起始节点
            t_node = lin["to"] # 该关系的终止节点
            relation_name = lin["name"]
            relation_type = lin["type"]
            # 关系可能重复，所以，注意去重
            if f_node in id_name_dict.keys() and t_node in id_name_dict.keys():
                temp = id_name_dict[t_node] + "\t" + id_name_dict[f_node] + "\t" + relation_name + "\n"
                my_key = id_name_dict[t_node] + "|" + id_name_dict[f_node]
                if my_key in relation_set:
                    print("already exist,relation=", my_key)
                    continue
                else:
                    relation_set.add(my_key)
                relation_file.write(temp)
            else:
                print("from_id=%s or to_id=%s maybe miss" % (f_node, t_node))
                continue
        """
        注意，其实有些关系虽然接口返回，但是缺乏对应的name信息
        {
        "from": "8520544",#千手纲手
        "to": "8628808", # 缺乏这个id对应的name信息，其实她师傅是猿飞日斩
        "name": "师傅",
        "type": 2
        },
        另外，宇智波斑，id=1842234 也是没有收录的
        """
if __name__ == "__main__":
    # os.chdir(os.path.join(os.getcwd(), './spider/images'))
    #在爬取过程中不断添加
    # get_json()#爬取完后，发现其实搜狗的录入信息比较少
    craw_relation() # 人物之间关系的抽取
