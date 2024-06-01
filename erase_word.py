# 用于去除爬到的文本中插入的垃圾词语、短句
import json
file_address = 'domo_files/erase_word/'

name = '新建文本文档'
file_name = file_address + name + '.txt'
file_modified_name = file_address + name + '_erased.txt'

# 从JSON文件中读取需要清除的字符串
with open(f'{file_address}erase_words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    erase_words = data['erase_words']

# 读取文本文件
with open(file_name, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 对每一行进行检查，如果存在需要清除的字符串，将其删除
with open(file_modified_name, 'w', encoding='utf-8') as f:
    for line in lines:
        for word in erase_words:
            line = line.replace(word, '')
        if line:
            f.write(line)