## 用于在小说中部分章节缺失内容时，直接在calibre用编辑器打开EPUB文件，添加内容
## 注意：每段前加了两个空格，需要在calibre编辑器里用查找替换将两个空格替换为缩进两字符

name = '新建文本文档'
file_name = name + '.txt'
file_modified_name = name + '_modified.txt'

def add_xml_label(file, file_modified):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(file_modified, 'w', encoding='utf-8') as f:
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:  # 如果行不为空
                f.write(f'<p class="calibre1">  {stripped_line}</p>\n')
            else:
                f.write(line)  # 如果行为空，原样写回

def add_blank_line(file, file_modified):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(file_modified, 'w', encoding='utf-8') as f:
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:  # 如果行不为空
                f.write(f'{stripped_line}\n\n')
            else:
                f.write(line)  # 如果行为空，原样写回
                
if __name__ == '__main__':
    # add_xml_label(file_name, file_modified_name)
    add_blank_line(file_name, file_modified_name)