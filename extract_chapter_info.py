from bs4 import BeautifulSoup
import os
import shutil

def delete_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)  # 删除文件
        elif os.path.isdir(path):
            shutil.rmtree(path)  # 删除目录
            
def read_html(filename):
    """从本地读取一个HTML文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    return html

def get_chapter_list_local(html_name, url_root):
    content_html = read_html(html_name)
    bes = BeautifulSoup(content_html, "lxml")
    texts = bes.find("div", id = "list")
    chapters = texts.find_all("a") #该函数可以返回list下的标签为a的所有信息
    words = []
    #对标签a内的内容进行提取
    for chapter in chapters:
        name = chapter.string #取出字符串，可以看出字符串只有章节号与章节名称，刚好符合我们所需
        url1 = url_root + chapter.get("href") #获得每一章节小说的url，可从html代码中看到每一个"href"前边均缺少初始的url，因此需要加上
        word = [url1, name]
        words.append(word)           
    return words

def write_files(words, file_1, file_2):
    with open(file_1, "a", encoding = "utf-8") as file_url, open(file_2, "a", encoding = "utf-8") as file_name:
        for word in words:       
            file_url.write(word[0] + '\n')
            file_name.write(word[1] + '\n')
        
if __name__ == '__main__':
    url_root = 'https://www.31xs.com'
    file_address = 'files/'
    html_file_path = file_address + 'content.html'
    url_file_path = file_address + 'chapter_url.txt'
    name_file_path = file_address + 'chapter_name.txt'
    
    # 清理可能存在的历史文件
    delete_if_exists(url_file_path)
    delete_if_exists(name_file_path)
     
    words = get_chapter_list_local(html_file_path, url_root)
    write_files(words, url_file_path, name_file_path)