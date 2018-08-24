"""
将火影忍者的人物关系图谱导入neo4j
"""

name_dict = {}
with open("spider/NarutoSpider/files/name_id_detail.txt",'r',encoding="utf-8") as f_detail:
    for line in f_detail.readlines():
        name_array = line.strip().split("\t")
        name = name_array[0]
        id = name_array[1]
        intro = name_array[2]
        templist = list()
        templist.append(id)
        templist.append(intro)
        name_dict[name] = templist

print(len(name_dict))

from py2neo import Graph, Node, Relationship,NodeMatcher
from config import graph



with open("spider/NarutoSpider/files/naruto_relation.txt") as f:
    for line in f.readlines():
        rela_array=line.strip("\n").split("\t")
        print(rela_array)
        name_0 = rela_array[0]
        # if name_0 in name_dict.keys():
        id_0 = name_dict[name_0][0]
        intro_0 = name_dict[name_0][1]

        name_1 = rela_array[1]
        id_1 = name_dict[name_1][0]
        intro_1 = name_dict[name_1][1]
        graph.run("MERGE(p: NarutoPerson{Name: '%s',Id: '%s', Intro:'%s'})" % (name_0, id_0, intro_0))
        graph.run("MERGE(p: NarutoPerson{Name: '%s',Id: '%s', Intro:'%s'})" % (name_1, id_1, intro_1))
        graph.run(
            "MATCH(e: NarutoPerson), (cc: NarutoPerson) \
            WHERE e.Name='%s' AND cc.Name='%s'\
            CREATE(e)-[r:%s{relation: '%s'}]->(cc)\
            RETURN r" % (rela_array[0], rela_array[1], rela_array[2],rela_array[2])
        )

"""
由于宇智波斑没有在详细页出现，所以，直接给空？？
最后是直接删除在naruto_relation.txt中的以下记录：
宇智波斑	宇智波带土	师傅
"""