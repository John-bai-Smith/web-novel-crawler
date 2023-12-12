import requests
from bs4 import BeautifulSoup
import random
import time

def get_index():
    """从小说的目录页获取每章对应的网址"""
    url = "https://www.31xs.com/149/149961/" 
    url_root = "https://www.31xs.com/"
    header = {
        # "Accept": "*/*",
        # "Accept-Encoding": "gzip, deflate, br",
        # "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        # "Cookie": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    req = requests.get(url = url, headers = header)
    req.encoding = "utf-8" #"utf-8"
    html = req.text
    bes = BeautifulSoup(html, "lxml")
    texts = bes.find("div", id = "list")
    chapters = texts.find_all("a") #该函数可以返回list下的标签为a的所有信息
    words = [] #创建空的列表，存入每章节的url与章节名称
    ##对标签a内的内容进行提取
    for chapter in chapters:
        name = chapter.string #取出字符串，可以看出字符串只有章节号与章节名称，刚好符合我们所需
        url1 = url_root + chapter.get("href") #获得每一章节小说的url，可从html代码中看到每一个"href"前边均缺少初始的url，因此需要加上
        word = [url1, name] #以列表格式存储
        words.append(word) #最终加入总的大列表中并返回
    return words

def get_chapter(tar, header):
    """依次抓取每章的文本内容"""
    while True:
        try:
            req = requests.get(url = tar[0], headers = header, timeout = 1000)
            break
        except Exception as e:
            print(f"出现错误：{e}，正在重新运行...")
                    
    ran = random.randint(2,5)
    time.sleep(ran)
    req.encoding = "utf-8"
    html = req.text
    bes = BeautifulSoup(html,"lxml")
    texts = bes.find("div", id = "content")
    texts_list = texts.text.replace("章节报错", "")
    return texts_list
        
        
def get_content(novel_name, num = 0):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    target = get_index()
    header = {"User-Agent":
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    with open("D:/download/" + novel_name + ".txt", "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for tar in target[num:]:            
            texts_list = get_chapter(tar, header) # 抓取单章的内容            
            print(f"正在下载{num}：{tar[1]}")
            file.write(tar[1])  # 写入章节标题
            for line in texts_list: # 逐行写入章节内容
                file.write(line)            
            num = num + 1  # 章节计数加1
    
if __name__ == '__main__':
    novel_name = "梦回大明春"
    num = 0 # 决定了从第几章开始新增，用于增量式更新文本内容    
    get_content(novel_name, num)