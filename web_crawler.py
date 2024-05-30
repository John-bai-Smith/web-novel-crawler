import requests
from bs4 import BeautifulSoup
import random
import time
import sys

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

# 创建一个字典，键是url_root的值，值是查找参数
find_index_params = {
    "https://www.uuks5.com": ('ul', {'id': 'chapterList'}),
    "https://www.bqguu.cc": ('div', {'class': 'listmain'}),
}

find_content_params = {
    "https://www.uuks5.com": ('div', {'id': 'TextContent'}),
    "https://www.bqguu.cc": ('div', {'id': 'chaptercontent'}),
}

def get_novel(novel_name, url_index, url_root, num = 0):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    index_list = get_index(url_index, url_root)
    with open("D:/download/" + novel_name + ".txt", "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for chapter_list in index_list[num:]:         
            print(f"正在下载{num}：{chapter_list[1]}")
            paragraphs_list = get_chapter(url_root, chapter_list) # 抓取单章的内容
            file.write(f'\n\n\n{chapter_list[1]}\n') # 写入章节标题
            for line in paragraphs_list: # 逐行写入章节内容
                line = line.get_text().strip()
                if line:            
                    file.write(f'    {line}\n')            
            num = num + 1  # 章节计数加1
            
            # 通过延时来降低爬虫的请求频率，减小被反爬的风险                
            ran = random.randint(1,3)
            time.sleep(ran)

def get_index(url_index, url_root):
    """从小说的目录页获取每章对应的网址，将url和目录名保存在列表中返回"""   
    bes = get_page(url_index)
    index_list = process_index_page(url_root, bes)    
    return index_list

def get_page(url_index):
    """获取网页的html文本内容"""
    req = requests.get(url = url_index, headers = header, timeout = 10)
    req.encoding = "utf-8"
    bes = BeautifulSoup(req.text, "lxml")
    return bes

def process_index_page(url_root, beautifulsoup):
    """对目录页的html内容进行处理，获得章节网址-章节标题的列表"""
    texts = extract_text(url_root, beautifulsoup, find_index_params)
    index_list = extract_index_list(texts)       
    return index_list

def extract_text(url_root, beautifulsoup, find_params):
    tag_name, attrs = find_params.get(url_root)
    if tag_name is not None:
        if attrs is not None:
            texts = beautifulsoup.find(tag_name, **attrs)
        else:
            texts = beautifulsoup.find(tag_name)
            
        if texts is None:
            print('No texts found')
            sys.exit()          
    else:
        print(f'No parameters found for url_root: {url_root}')
        sys.exit()
    return texts

def extract_index_list(texts):
    """提取内容得到章节网址-章节标题的列表"""
    words = [] #创建空的列表，存入每章节的url与章节名称
    
    chapters = texts.find_all("a") #该函数可以返回list下的标签为a的所有信息
    #对标签a内的内容进行提取
    for chapter in chapters:
        name = chapter.string #取出字符串，可以看出字符串只有章节号与章节名称，刚好符合我们所需
        url1 = url_root + chapter.get("href") #获得每一章节小说的url，可从html代码中看到每一个"href"前边均缺少初始的url，因此需要加上
        word = [url1, name] #以列表格式存储
        words.append(word) #最终加入总的大列表中并返回  
    return words

def get_chapter(url_root, chapter_list):
    """依次抓取每章的文本内容"""
    while True:
        try:
            bes = get_page(chapter_list[0])
            break
        except Exception as e:
            print(f"出现错误：{e}，正在重新运行...")
            time.sleep(1) # 请求失败后延迟1s再次请求
    
    texts_list = process_chapter_page(url_root, bes)
    return texts_list       
        
def process_chapter_page(url_root, beautifulsoup):
    """处理章节页"""
    texts = extract_text(url_root, beautifulsoup, find_content_params)
    par_list = extract_paragraph(texts)
    return par_list

def extract_paragraph(texts):
    par_list = texts.find_all("p")
    return par_list
    
if __name__ == '__main__':
    # 目前可以使用的网站 url_root
    # 1. "https://www.bqguu.cc" 
    # 2. "https://www.uuks5.com"
    # 已经失效的网站
    # 1. "https://www.31xs.com"
    # 2. "https://www.ddxs.com"
    
    novel_name = "这游戏也太真实了"
    url_root = "https://www.uuks5.com"
    url = "https://www.uuks5.com/book/489939/"
    num = 0 # 决定了从第几章开始新增，用于增量式更新文本内容
    
    # 下一步优化方案，把抓取页面封装为一个函数，抓取目录的抓取章节函数中调用抓取页面
    # 把目录和章节的内容处理封装为单独的函数
    # 把章节内容去除多余内容封装为单独的函数
    get_novel(novel_name, url, url_root, num)