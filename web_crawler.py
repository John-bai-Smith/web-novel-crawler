import requests
from bs4 import BeautifulSoup
import random
import time

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
   
def get_index(url_index):
    """从小说的目录页获取每章对应的网址，将url和目录名保存在列表中返回"""   
    url_root = "https://www.31xs.com/"
    req = requests.get(url = url_index, headers = header)
    req.encoding = "utf-8"
    bes = BeautifulSoup(req.text, "lxml")
    texts = bes.find("div", id = "list")
    chapters = texts.find_all("a") #该函数可以返回list下的标签为a的所有信息
    words = [] #创建空的列表，存入每章节的url与章节名称
    #对标签a内的内容进行提取
    for chapter in chapters:
        name = chapter.string #取出字符串，可以看出字符串只有章节号与章节名称，刚好符合我们所需
        url1 = url_root + chapter.get("href") #获得每一章节小说的url，可从html代码中看到每一个"href"前边均缺少初始的url，因此需要加上
        word = [url1, name] #以列表格式存储
        words.append(word) #最终加入总的大列表中并返回
    return words

def get_chapter(tar):
    """依次抓取每章的文本内容"""
    while True:
        try:
            req = requests.get(url = tar[0], headers = header, timeout = 1000)
            break
        except Exception as e:
            print(f"出现错误：{e}，正在重新运行...")
            time.sleep(1) # 请求失败后延迟1s再次请求
    
    # 通过延时来降低爬虫的请求频率，减小被反爬的风险                
    ran = random.randint(2,5)
    time.sleep(ran)
    
    # 解析网页内容
    req.encoding = "utf-8"
    bes = BeautifulSoup(req.text, "lxml")
    texts = bes.find("div", id = "content")
    texts_list = texts.text.replace("章节报错", "") 
    return texts_list       
        
def get_content(novel_name, url_index, num = 0):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    target = get_index(url_index)
    header = {"User-Agent":
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"}
    with open("D:/download/" + novel_name + ".txt", "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for tar in target[num:]:            
            texts_list = get_chapter(tar) # 抓取单章的内容            
            print(f"正在下载{num}：{tar[1]}")
            file.write(tar[1]) # 写入章节标题
            for line in texts_list: # 逐行写入章节内容
                file.write(line)            
            num = num + 1  # 章节计数加1
    
if __name__ == '__main__':
    novel_name = "梦回大明春"
    url = "https://www.31xs.com/149/149961/" 
    num = 0 # 决定了从第几章开始新增，用于增量式更新文本内容    
    get_content(novel_name, url, num)