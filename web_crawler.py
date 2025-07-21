import requests
from bs4 import BeautifulSoup
import random
import time
import json
import signal
import sys
import unicodedata
import re
file_address = 'demo_files/web_crawler/'

# 从JSON文件中读取字典
with open(f'{file_address}find_dictionary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    header = data['header']  # 访问标头
    find_encoding = data['find_encoding']  # 页面编码方式
    find_index_params = data['find_index_params']  # 目录页标签
    find_content_params = data['find_content_params'] # 章节页标签
    find_extract_params = data['find_extract_params'] # 章节内容标签
    find_page_num = data['find_page_num']  # 单章的页数
    url_root_list = data['url_root_list']  # 源网站列表
    ignore_html_check = data['ignore_html_check']  # 章节url不需要包含html

skip_chapter = '展开全部章节'
start_time = time.time()

def get_novel(url_index, num_start = 0, num_stop = float('inf')):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    num = num_start
    url_root = get_url_root(url_index)
    index_list = get_index(url_index, url_root)
    with open(novel_name + ".txt", "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for chapter_list in index_list[num:]:
            current_time = time.time()
            # 判断是否需要跳过当前章节
            if skip_chapter in chapter_list[0]:
                print(f"已跳过{num}：{chapter_list[0]}")
                num = num + 1
                continue
            else:
                chapter_tmp = pad_to_width(chapter_list[0], 40)        
                print(f"正在下载{num}：{chapter_tmp}  已运行时间：{format_time(current_time - start_time)}")
            
            file.write(f'\n\n\n{chapter_list[0]}\n\n') # 写入章节标题
            
            for chapter_url in chapter_list[1:]:
                if chapter_url:        
                    paragraphs_list = get_chapter(url_root, chapter_url) # 抓取单章的内容
                    # 逐行写入章节内容
                    first_iteration = True  # 标志变量，表示是否是第一次循环
                    for line in paragraphs_list:
                        line = line.get_text().strip()
                        if first_iteration: # 只在第一次循环时执行
                            line = check_chapter_name(chapter_list[0], line) # 检查章节内容的第一行是否包含标题，若有则将其删除
                            first_iteration = False  # 更新标志变量
                        if line:
                            file.write(f'    {line}\n\n')
                else:
                    print(f"空链接{num}：{chapter_list[0]}，已跳过")
                    continue
            if num >= num_stop:
                break
            num = num + 1  # 章节计数加1
            
            # 通过延时来降低爬虫的请求频率，减小被反爬的风险
            ran = random.randint(3,5)
            time.sleep(ran)
        
    # 后处理
    post_process(num - num_start) 

def check_chapter_name(chapter_name, line):
    """去除章节内容第一行中的章节标题"""
    
    # 发现有的网站目录页的章节标题中不带“-”，但章节内容第一行中的标题带“-”，
    # 因此需要用正则表达式替换，同时不能把章节标题后面紧跟着的别的字符给误删掉
    # 去除多余标题时忽略英文字母大小写
    
    chapter_name_without_spaces = chapter_name.replace(" ", "") # 移除空格
    
    # 创建一个正则表达式模式，允许在每个字符之间插入一个可选的非字母字符（不包括中文字符和中文双引号）
    pattern = re.compile(rf"({''.join([f'[{char.lower()}{char.upper()}]' + r'[^\"“”\u4e00-\u9fa5]*' for char in chapter_name_without_spaces])})", re.IGNORECASE)
    
    # 使用正则表达式替换匹配的部分为空字符串
    return pattern.sub('', line, count = 1)
    
def get_display_width(s):
    """计算字符串的显示宽度"""
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in 'WF':
            width += 2
        else:
            width += 1
    return width

def omit_too_long_string(s, width):
    """将显示宽度过大的字符串调整为固定宽度，末尾替换为省略号"""
    ellipsis = '...'
    ellipsis_width = get_display_width(ellipsis)
    
    if get_display_width(s) <= width:
        return s
    
    truncated_width = width - ellipsis_width
    truncated_string = ''
    current_width = 0
    
    for char in s:
        char_width = 2 if unicodedata.east_asian_width(char) in 'WF' else 1
        if current_width + char_width > truncated_width:
            break
        truncated_string += char
        current_width += char_width
    
    return truncated_string + ellipsis + ' ' * (truncated_width - current_width)

def pad_to_width(s, width):
    """填充字符串使其达到指定的显示宽度"""
    current_width = get_display_width(s)
    if current_width < width:
        return s + ' ' * (width - current_width)
    else:
        return omit_too_long_string(s, width)
    
def get_index(url_index, url_root):
    """从小说的目录页获取每章对应的网址，将url和目录名保存在列表中返回"""   
    bes = get_page(url_index, url_root)
    index_list = process_index_page(url_root, bes)
    # ********************************************************** #
    # 增量更新时在此处加断点，查看index_list的值
    # ********************************************************** #    
    return index_list

def get_page(url_page, url_root):
    """获取网页的html文本内容"""
    req = requests.get(url = url_page, headers = header, timeout = 1000)
    req.encoding = find_encoding.get(url_root)
    bes = BeautifulSoup(req.text, "lxml")
    return bes

def process_index_page(url_root, beautifulsoup):
    """对目录页的html内容进行处理，获得章节网址-章节标题的列表"""
    texts = extract_text(url_root, beautifulsoup, find_index_params)
    index_list = extract_index_list(url_root, texts)       
    return index_list

def extract_text(url_root, beautifulsoup, find_params):
    """提取已抓取的文本中带有特定标签的部分"""
    tag_name, attrs = find_params.get(url_root)
    texts = beautifulsoup.find(tag_name, **attrs)
    return texts

def extract_index_list(url_root, texts):
    """提取内容得到章节网址-章节标题的列表"""
    words = [] #创建空的列表，存入每章节的url与章节名称
    
    chapters = texts.find_all("a") #该函数可以返回list下的标签为a的所有信息
    #对标签a内的内容进行提取
    for chapter in chapters:
        name = chapter.string #取出字符串，可以看出字符串只有章节号与章节名称，刚好符合我们所需
        url1 = url_root + chapter.get("href") #获得每一章节小说的url，可从html代码中看到每一个"href"前边均缺少初始的url，因此需要加上
        if '.html' in url1 or url_root in ignore_html_check:  #判断url是否为正确的链接
            word = [name, url1] #以列表格式存储
            page_num = find_page_num.get(url_root)
            if page_num > 1:           
                for number in list(range(2, page_num + 1)):
                    url_tmp = url1.replace(".html", "") + "_" + str(number) + ".html"
                    word.append(url_tmp)          
            words.append(word) #最终加入总的大列表中并返回
    return words

def get_chapter(url_root, chapter_url):
    """依次抓取每章的文本内容"""
    while True:
        try:
            if chapter_url:
                bes = get_page(chapter_url, url_root)
                try:
                    texts_list = process_chapter_page(url_root, bes)
                except requests.exceptions.RequestException as e:
                    print(f"出现网络错误：{e}，正在重新运行...")
                    time.sleep(5) # 网络请求失败后延迟5s再次请求
                except AttributeError as e:
                    print(f"出现错误：{e}，正在重新运行...")
                    time.sleep(1) # 请求失败后延迟1s再次请求        
                if texts_list:    
                    break
            else: # 当链接为空时跳过
                print(f"get_chapter()接收到空链接")
                break
        except Exception as e:
            print(f"出现错误：{e}，正在重新运行...")
            time.sleep(1) # 请求失败后延迟1s再次请求 
    return texts_list       
        
def process_chapter_page(url_root, beautifulsoup):
    """处理章节页，获得章节内容文本"""
    texts = extract_text(url_root, beautifulsoup, find_content_params)
    tag = find_extract_params.get(url_root)
    if tag:
        par_list = extract_paragraph(texts, tag)
    else:
        par_list = texts
    return par_list

def extract_paragraph(texts, tag):
    """根据xml标签tag提取文本"""
    par_list = texts.find_all(tag)
    return par_list

def get_url_root(url):
    """根据url获取对应的网站首页的网址"""
    url_root = ""
    for url_rt in url_root_list:
        if url_rt in url:
            url_root = url_rt
            break
    return url_root

def post_process(total_num):
    """打印脚本总运行时间和每章平均耗时"""
    total_time = count_total_time()
    average_time = round(total_time / total_num)
    print("****     执行成功     ****")
    print(f"共下载{total_num}章，耗时{format_time(total_time)}，平均每章耗时{format_time(average_time)}")

def count_total_time():
    return time.time() - start_time

def format_time(seconds):
    if seconds < 60:
        return f"{round(seconds)}秒"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{round(m)}分钟{round(s)}秒"
    else:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{round(h)}小时{round(m)}分钟"

def signal_handler(sig, frame):
    print("****     程序中断     ****")
    print(f"共运行{format_time(count_total_time())}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
    
if __name__ == '__main__':
    num_start = 3537 # 决定了从第几章开始新增，用于增量式更新文本内容，默认为0
    num_stop = 739 # 决定了从第几章结束新增，用于增量式更新文本内容，默认为无穷大
    novel_name = "呢喃诗章"
    url_index = "https://www.biquge123.uk/51669"
    get_novel(url_index, num_start)
    # get_novel(url_index, num_start, num_stop)