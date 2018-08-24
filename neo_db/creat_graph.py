from py2neo import Graph, Node, Relationship,NodeMatcher
from config import graph

with open("./raw_data/relation.txt") as f:
    for line in f.readlines():
        rela_array=line.strip("\n").split(",")
        print(rela_array)
        graph.run("MERGE(p: Person{cate:'%s',Name: '%s'})" % (rela_array[3], rela_array[0]))
        graph.run("MERGE(p: Person{cate:'%s',Name: '%s'})" % (rela_array[4], rela_array[1]))
        graph.run(
            "MATCH(e: Person), (cc: Person) \
            WHERE e.Name='%s' AND cc.Name='%s'\
            CREATE(e)-[r:%s{relation: '%s'}]->(cc)\
            RETURN r" % (rela_array[0], rela_array[1], rela_array[2],rela_array[2])

        )

"""
常用语句:
(1)查找与指定人名相关的其他人
MATCH (p1:Person{Name:'史湘云' })--(p2:Person) RETURN p2.Name
或者
MATCH (p:Person{Name:'史湘云' })--(Person) RETURN p.Name
或者
Match (relation{Name:'史湘云'})--(Person) RETURN Person.Name

返回:
"贾母"
"薛宝钗"
"林黛玉"
"贾宝玉"

(2)返回史湘云的关联人物
match(p:Person) where p.Name="史湘云" return p

(3)查找两个人直接的关系
MATCH (:Person {Name: '史湘云' })-[r]->(:Person{Name:"贾母"}) RETURN r

返回：
{
  "relation": "孙女"
}

(4)查找史湘云的“朋友”
MATCH (:Person {Name: '史湘云' })-[r:朋友]->(Person) return Person.Name
返回:
"薛宝钗"
"林黛玉"
"贾宝玉"
"""