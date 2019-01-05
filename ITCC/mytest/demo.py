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
        corpora_documents.append(text1)
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
    if similarity[test_corpus_1] :
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
def sql_query(s):
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
        keyword=result[0]
        print('只有一个关键词时的keyword:'+str(keyword))
        fuzzy_query(str(keyword[0]))
    else:
        print('关键词为空')

if __name__ == '__main__':

    s="输入的问题"
    #第一步：模糊匹配
    sql_query(s)
    #第二步：算法模型匹配
    doc2bow(s)
