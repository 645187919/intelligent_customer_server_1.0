import jieba
from gensim import corpora
from gensim.corpora import Dictionary
from gensim.similarities import Similarity
from jieba import analyse

import aiml
import os
import sys

from mytest.aiccdb.mysqlhelper import MysqlHelper


def fuzzy_query(keyword):
    # 第一个问题：not enough arguments for format string
    # 出现这类问题，主要是字符串中包含了%号，python 认为它是转移符，而实际我们需要的就是%， 这个时候，可以使用%%来表示
    # 第二个问题：/为转义字符，需要将这里的‘转义
    # 组装需要的SQL查询语句。
    sql = 'select * from KeFu where questions like \'%%' + keyword + '%%\' limit 5'
    # sql='select * from Teacher'
    print(sql)
    # 与Mysql数据库进行连接
    helper = MysqlHelper('192.168.112.200', 3306, 'test1', 'root', 'root')
    # 获取SQL查询所有的查询结果
    one = helper.get_all(sql)
    print(one)
    if one:
        for exmple in one:
            print("问题："+exmple[0]+"\n"+"答案："+exmple[1])

    else:
        print("输出为None")

def accurate_query(keyword):

    sql = 'select * from KeFu where questions like \'%%' + keyword + '%%\''
    # sql='select * from Teacher'
    print(sql)
    # 与Mysql数据库进行连接
    helper = MysqlHelper('192.168.112.200', 3306, 'test1', 'root', 'root')
    # 获取SQL查询所有的查询结果
    one = helper.get_all(sql)
    print(one)
    if one:
        for exmple in one:
            print("问题："+exmple[0]+"\n"+"答案："+exmple[1])

    else:
        print("输出为None")

stopwords = set(open('stopwords.txt',encoding='utf8').read().strip('\n').split('\n'))   #读入停用词
# 添加自定义的词库用于分割或重组模块不能处理的词组。
jieba.load_userdict("userdict.txt")

# 删除句子中的停词
def del_stopword(line):
    # text3.clear()
    #这一点也是Python相对于其他语言来说占内存的一个原因吧？
    text3=[]
    for x in jieba.lcut(line):
        # print(x)
        if x not in stopwords:
            text3.append(x)
    return text3

# 方案二：通过Doc2Bow将分词后的句子转化为对应的向量，然后构成一个词库，通过用余弦定理来计算和输入句子相似的句子
# 并进行推荐
#方案二中可以添加根据返回的句子的相似度的大小来进一步判断是返回一个确切的问题（相似度大）还是返回多个相似的问题供用户选择（
# 相似度小的情况）
def doc2bow():
    file = open("questions.txt",encoding='utf8')
    corpora_documents = []
    # text1=[]
    text2=[]
    lines = file.readlines()
    print(lines)
    for line in lines:
        # print(line)
        line_strip = line.strip('\n')
        # print(line_strip)
        text2.append(line_strip)
        # print("text2:"+str(text2))


        text1=del_stopword(line_strip)
        # text2=text1

        # for x in jieba.lcut(line):
        #     # print(x)
        #     if x not in stopwords:
        #         text1.append(x)
        # # str(text1).strip("\n")
        # text2=text1
        corpora_documents.append(text1)
        # # print(corpora_documents)
        # text1=[]
    print(corpora_documents)

    # 生成字典：Dictionary(183 unique tokens: ['\n', '品种', '贷款', '贷款期限', '申请']...)
    dictionary = corpora.Dictionary(corpora_documents)
    # #判断对应的词典向量是否存在
    if os.path.exists("E:\ITCC\mytest\dict.txt"):
        dictionary=Dictionary.load('dict.txt')#加载
    else:
        dictionary.save('dict.txt') #保存生成的词典
        dictionary=Dictionary.load('dict.txt')#加载

    print(dictionary)
    # 生成向量语料：[[(0, 1), (1, 1), (2, 1)], [(0, 1), (3, 1)], [(0, 1), (2, 1), (4, 1), (5, 1)]...]
    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    print(corpus)
    # 生成语料model便于后面使用
    if os.path.exists("corpuse.mm"):
        corpus=corpora.MmCorpus('corpuse.mm')#加载
    else:
        corpora.MmCorpus.serialize('corpuse.mm',corpus)#保存生成的语料
        corpus=corpora.MmCorpus('corpuse.mm')#加载
    # 生成对应的相似度模型：max_features:最大的特征数也可以理解为维度，也就是字典中单词数的最大值为多少
    similarity = Similarity('-Similarity-index', corpus, num_features=400)
    test_data_1 = s
    test_cut_raw_1 =del_stopword(test_data_1)
    print(test_cut_raw_1)
    test_corpus_1 = dictionary.doc2bow(test_cut_raw_1)
    similarity.num_best = 5
    print(similarity[test_corpus_1])  # 返回最相似的样本材料,(index_of_document, similarity) tuples
    for sample in similarity[test_corpus_1]:
        index = sample[0]
        #相似度为1直接执行精确查找返回对应的答案
        if sample[1]==1:
            print("你的问题是："+str(text2[int(index)])+"相似度："+str(sample[1]))
            break
        #相似度大于某个值则将代表该问题可能是用户想要询问的问题
        elif sample[1]>=0.8:
            print("你要问的问题是不是："+str(text2[int(index)])+"相似度："+str(sample[1]))
        #否则就返回一组问题让用户挑选
        else:
            print("相似的句子："+str(text2[int(index)])+"相似度："+str(sample[1]))
    #实验效果
    # for line in lines:
    #     test_data_1 = line
    #     test_cut_raw_1 =del_stopword(test_data_1)
    #     print(test_cut_raw_1)
    #     test_corpus_1 = dictionary.doc2bow(test_cut_raw_1)
    #     similarity.num_best = 5
    #     print(similarity[test_corpus_1])  # 返回最相似的样本材料,(index_of_document, similarity) tuples
    print('################################')

# 方案一：拿到未匹配的句子做分词处理后得到想要的关键词之后再做SQL的模糊查询进行相似问题的推荐
def sql_query():
    # 添加自定义的停用词库，去除句子中的停用词。
    jieba.analyse.set_stop_words("stopwords.txt")
    # 添加自定义的词库用于分割或重组模块不能处理的词组。
    jieba.load_userdict("userdict.txt")
    #添加自定义的权重值词库
    jieba.analyse.set_idf_path("idf.txt.big")
    # 通过TF-IDF算法提取出句子中的词，然后打印出TF-IDF值最高的前N个词和他们的TF-IDF值。
    for x, w in jieba.analyse.extract_tags(s, topK=5, withWeight=True):
        print('%s %s' % (x, w))
    print('#' * 40)
    result = jieba.analyse.extract_tags(s, topK=5, withWeight=True)
    print('result:' + str(result))

    if result:
        if len(result) == 1:
            # 直接拿到这个词进行SQL查询
            keyword=result[0]
            print('只有一个关键词时的keyword:'+str(keyword))
            fuzzy_query(str(keyword[0]))

        else:
            # 拿出前N个关键词并比较他们权值的大小
            # （当然这里还可以做进一步处理比如比较返回的几个关键词的权值大小，如果前几个词的权值大小相同可以全部取出来）
            key1 = result[0]
            key2 = result[1]
            finalKey=[]
            #直接将前两个关键词传到SQL中查询
            finalKey.append(key1[0])
            finalKey.append(key2[0])
            print('有多个关键词时的keyword:'+str(finalKey))
            # query(str(finalKey))
            # print('finalKey:'+finalKey)
    else:
        print('关键词为空')


if __name__ == '__main__':
    # doc2bow()

    # Kernel()是一个公共的接口
    k = aiml.Kernel()
    print("hi, 我是小安客服机器人，请问您要办理什么业务？")
    # 初始化Kernel
    k.bootstrap(learnFiles="cn-startup.xml", commands="load aiml cn")

    while True:

        s = k.respond(input(">"))
        print('返回的语句是：' + s)
        #如果返回的语句是以#开头的就说明知识库中没有匹配的question，则需要做进一步的处理
        if s.startswith('#'):
            #将未知的问题记录到日志文件中，便于后续工作
            file = open("new_questions.txt",'a+',encoding='utf-8')
            file.write(s+'\n')
            file.close()

        #
        #     print(s)
        #     sql_query()
            doc2bow()
