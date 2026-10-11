import re
import chardet
from pathlib import Path
from web_crawler import pad_to_width

def build_ad_regex(keywords):
    """把广告词变成模糊正则；关键词中的英文字母忽略大小写"""

    regex_list = []
    for kw in keywords:
        # 在字与字之间允许插入任意字符（包括中文）
        pattern = ".*".join(re.escape(ch) for ch in kw)
        # 内联开关 (?i:...) 让英文字母不区分大小写，作用范围仅限当前关键词
        regex_list.append(f"(?i:{pattern})")
    return "|".join(regex_list)

def clean_text(input_file, output_file, record, keywords=None):
    """去除txt文本中的广告行，并修复错别字:
    param input_file: 原始txt文件路径
    param output_file: 清洗后txt文件路径
    param keywords: 广告关键词列表
    """

    # 默认错别字修复列表
    typo_dict = {
        "这幺": "这么",
        "怎幺": "怎么",
        "那幺": "那么",
        "要幺": "要么",
        "什幺": "什么",
        "多幺": "多么",
    }
        
    # 默认广告关键词（可按需扩展）
    if keywords is None:
        keywords = ["手打无错", "无错章节", "章节更新", "最新章节", "最新章節", \
            "章节来源于", "更多精彩章节", "立即访问获取章节", \
            "更新不易", "最快更新", "无错更新", "更新最快", \
            "速读谷", "速讀谷", "74文学网", "82中文网", \
            "记住我们网", "最新小说首发", "写到这里读者", "写到这里书友", \
            "全网最快小说站", "小说网首发", "搜索小说网", "收藏唯一网址", "查看最新地址", \
            "记住更新地址",  "提醒您查看最新内容", "请到查看", \
            "本章未完", "点击下一页继续阅读", "??????????", "wapcom", "追书app"]

    # 编译广告正则
    ad_pattern = re.compile(build_ad_regex(keywords))
    
    wrong_count = 0
    ad_count = 0
    
    # 先检测编码
    with open(input_file, 'rb') as f_in:
        raw_data = f_in.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    with open(input_file, "r", encoding=encoding) as fin, \
         open(output_file, "w", encoding=encoding) as fout, \
         open(record, "w", encoding=encoding) as frec:

        for line_no, line in enumerate(fin, start=1):
            # 1. 错别字替换
            for wrong, correct in typo_dict.items():
                if wrong in line:
                    line = line.replace(wrong, correct)
                    wrong_count = wrong_count + 1
            
             # 2. 正则广告检测
            matches = ad_pattern.findall(line)
            if len(matches) < 1:
                fout.write(line)
            else:
                line_no_normal = pad_to_width(str(line_no), 12)
                frec.write(f"[line {line_no_normal}] {line}")
                ad_count = ad_count + 1
    
    print(f"共修正错别字{wrong_count}个，去除广告{ad_count}句。")


if __name__ == "__main__":
    file_name = "input.txt"
    added_suffix = "_old"
    folder = "kaf-cli_v1.3.6-3_windows_386"
    parent_dir = Path(__file__).resolve().parent.parent
    input_txt = parent_dir / folder / file_name  # 原文件
    output_txt = input_txt.with_name("output.txt")  # 清洗后文件
    record_txt = input_txt.with_name("ad_record.txt") # 记录检索出的广告句子
    
    clean_text(input_txt, output_txt, record_txt)
    
    tmp_txt = input_txt
    input_txt.rename(input_txt.with_name(input_txt.stem + added_suffix + input_txt.suffix)) # 将原文件重命名
    output_txt.rename(tmp_txt.with_name(tmp_txt.stem + tmp_txt.suffix))
    