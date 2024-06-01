from bs4 import BeautifulSoup
from extract_chapter_info import read_html, get_chapter_list_local, delete_if_exists
file_address = 'domo_files/local_crawler/'

def get_chapter_local(chapter_name):
    """依次抓取每章的文本内容"""
    chapter_path = file_address + chapter_name + '.html'
    html = read_html(chapter_path)
    
    if html is None: # 抓取失败
        return None
    
    bes = BeautifulSoup(html, "lxml")
    texts = bes.find("div", id = "content")
    texts_list = texts.text.replace("章节报错", "") 
    return texts_list
        
def get_novel(novel_path, html_file, url_root, num = 0):
    """抓取小说目录，再依次抓取每章内容，增量式写入文件中"""
    target = get_chapter_list_local(html_file, url_root)
    with open(novel_path, "a", encoding = "utf-8") as file:  #写入文件路径 + 章节名称 + 后缀    
        for i, tar in enumerate(target[num:]):
            texts_list = get_chapter_local(str(i) + '-' + tar[1]) # 抓取单章的内容
              
            if texts_list is None: # 抓取失败
                print(f"下载章节{num}：{tar[1]}时出错")
                num = num + 1  # 章节计数加1
                continue
                     
            print(f"正在下载{num}：{tar[1]}")
            file.write(tar[1]) # 写入章节标题
            for line in texts_list: # 逐行写入章节内容
                file.write(line)            
            num = num + 1  # 章节计数加1
    
if __name__ == '__main__':
    novel_name = "怪物被杀就会死"
    novel_address = 'D:/download/'
    novel_path = novel_address + novel_name + ".txt"
    html_file = file_address + 'content.html'
    url_root = 'https://www.31xs.com'
    num = 0 # 决定了从第几章开始新增，用于增量式更新文本内容
    
    delete_if_exists(novel_path) # 清理可能存在的历史文件
    get_novel(novel_path, html_file, url_root, num)