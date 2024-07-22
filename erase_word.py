# 用于去除爬到的文本中插入的垃圾词语、短句
import json
file_address = 'demo_files/erase_word/'

name = '呢喃诗章'
if name == '新建文本文档':
    file_name = file_address + name + '.txt'
else:
    file_name = name + '.txt'
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
    counts_word = [0] * len(erase_words)
    for line in lines:
        for i, word in enumerate(erase_words):       
            counts_word[i] = counts_word[i] + line.count(word)
            line = line.replace(word, '')
        if line:
            f.write(line)
    for i, word in enumerate(erase_words):
        if counts_word[i] > 0:
            print(f"{i + 1}: 关键词 '{word}' 检测到 {counts_word[i]} 次")