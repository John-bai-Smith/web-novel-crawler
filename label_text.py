## 用于在小说中部分章节缺失内容时，直接在calibre用编辑器打开EPUB文件，添加内容
## 注意：每段前加了两个空格，需要在calibre编辑器里用查找替换将两个空格替换为缩进两字符
file_address = 'demo_files/label_text/'

name = '新建文本文档'
file_name = file_address + name + '.txt'
file_modified_name = file_address + name + '_lebeled.txt'

def add_xml_label(file, file_modified):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(file_modified, 'w', encoding='utf-8') as f:
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:  # 如果行不为空，可以去除空行
                # EPUB文件的段落缩进可以直接在格式文件里设置
                f.write(f'<p class="calibre1">{stripped_line}</p>\n')

def add_blank_line(file, file_modified):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(file_modified, 'w', encoding='utf-8') as f:
        for i in range(len(lines)):
            current_line = lines[i].strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else None
            if current_line:  # 如果当前行不为空
                if next_line:  # 如果下一行也不为空
                    f.write(f'{current_line}\n\n')
                else:  # 如果下一行为空
                    f.write(f'{current_line}\n')
            else:
                f.write(f'\n')
                
if __name__ == '__main__':
    # add_xml_label(file_name, file_modified_name)
    add_blank_line(file_name, file_modified_name)