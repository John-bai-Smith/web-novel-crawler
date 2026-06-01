import re
from pathlib import Path

def build_ad_regex(keywords):
    """把广告词变成模糊正则"""
    
    regex_list = []
    for kw in keywords:
        # 在字与字之间允许插入任意非单词字符
        pattern = "[^\\w]*".join(kw)
        regex_list.append(pattern)
    return "|".join(f"(?:{r})" for r in regex_list)

def clean_text(input_file, output_file, keywords=None):
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
        keywords = ["手打无错", "速读谷", "更新不易", "记住我们网", "最新小说首发", "写到这里读者", "写到这里书友"]

    # 编译广告正则
    ad_pattern = re.compile(build_ad_regex(keywords))
    
    wrong_count = 0
    ad_count = 0
    
    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8") as fout:

        for line in fin:
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
                ad_count = ad_count + 1
    
    print(f"共修正错别字{wrong_count}个，去除广告{ad_count}句。")


if __name__ == "__main__":
    suffix = ".txt"
    name = "input"
    folder = "kaf-cli_v1.3.6-3_windows_386"
    
    parent_dir = Path(__file__).resolve().parent.parent
    input_txt = parent_dir / folder / (name + suffix)     # 原文件
    output_txt = parent_dir / folder / (name + "_cleaned" + suffix)   # 清洗后文件

    clean_text(input_txt, output_txt)