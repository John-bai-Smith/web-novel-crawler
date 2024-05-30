import requests
from bs4 import BeautifulSoup
import random
import time

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
}
   
def get_index(url_index, url_root):
    """从小说的目录页获取每章对应的网址，将url和目录名保存在列表中返回"""   
    req = requests.get(url = url_index, headers = header, timeout = 10)
    req.encoding = "utf-8"
    print(req.text)
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
    ran = random.randint(1,3)
    time.sleep(ran)
    
    # 解析网页内容
    req.encoding = "utf-8"
    bes = BeautifulSoup(req.text, "lxml")
    texts = bes.find("div", id = "content")
    texts_list = texts.text.replace("章节报错", "") 
    return texts_list       
        
def get_content(novel_name, url_index, url_root, num = 0):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    target = get_index(url_index, url_root)
    with open("D:/download/" + novel_name + ".txt", "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for tar in target[num:]:            
            texts_list = get_chapter(tar) # 抓取单章的内容            
            print(f"正在下载{num}：{tar[1]}")
            file.write(tar[1]) # 写入章节标题
            for line in texts_list: # 逐行写入章节内容
                file.write(line)            
            num = num + 1  # 章节计数加1
    
if __name__ == '__main__':
    # 目前可以使用的网站 url_root
    # 1. "https://www.bqguu.cc" 
    # 2. "https://www.uuks5.com"
    # 已经失效的网站
    # 1. "https://www.31xs.com"
    # 2. "https://www.ddxs.com"
    
    novel_name = "怪物被杀就会死"
    url_root = "https://www.bqguu.cc"
    url = "https://www.bqguu.cc/book/1542/"
    num = 0 # 决定了从第几章开始新增，用于增量式更新文本内容
        
    get_content(novel_name, url, url_root, num)