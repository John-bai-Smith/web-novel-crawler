import re
import unicodedata
import chardet
from pathlib import Path
from web_crawler import pad_to_width


_CHAPTER_NUMBER = r"[0-9]+|[零〇○一二三四五六七八九十百千万两]+"
_EXCESS_CHAPTER_TITLE_PATTERN = re.compile(
    rf"^(?:第\s*(?:{_CHAPTER_NUMBER})\s*[卷部篇]\s*)?"
    rf"[^\w\r\n]*第\s*({_CHAPTER_NUMBER})\s*章\s*(.*?)\s*$"
)


def _normalize_chapter_number(number_text):
    """把阿拉伯数字或常见中文数字统一成便于比较的字符串。"""
    number_text = unicodedata.normalize("NFKC", number_text)
    if number_text.isdigit():
        return str(int(number_text))

    digit_values = {
        "零": 0,
        "〇": 0,
        "○": 0,
        "一": 1,
        "二": 2,
        "两": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    unit_values = {
        "十": 10,
        "百": 100,
        "千": 1000,
        "万": 10000,
        "亿": 100000000,
    }

    if not any(char in unit_values for char in number_text):
        return str(int("".join(
            str(digit_values[char]) for char in number_text
        )))

    total = 0
    section = 0
    current_digit = 0
    for char in number_text:
        if char in digit_values:
            current_digit = digit_values[char]
        elif char in unit_values:
            unit = unit_values[char]
            if unit < 10000:
                section += (current_digit or 1) * unit
            else:
                section += current_digit
                total += section * unit
                section = 0
            current_digit = 0

    return str(total + section + current_digit)


def _normalize_chapter_title(title):
    """忽略标题中的空格和标点，仅保留用于比较的正文。"""
    title = unicodedata.normalize("NFKC", title)
    return re.sub(r"[\W_]+", "", title).casefold()


def _parse_chapter_heading(line):
    """解析章节标题，返回章节号和规范化标题组成的签名。"""
    normalized_line = unicodedata.normalize("NFKC", line)
    match = _EXCESS_CHAPTER_TITLE_PATTERN.match(normalized_line)
    if match is None:
        return None

    chapter_number, chapter_title = match.groups()
    return (
        _normalize_chapter_number(chapter_number),
        _normalize_chapter_title(chapter_title),
    )


class _ExcessChapterNameCleaner:
    """依据标题签名和正文间隔识别连续出现的重复章节标题。"""

    def __init__(self, max_gap=5):
        if max_gap < 0:
            raise ValueError("max_gap must be greater than or equal to 0")
        self.max_gap = max_gap
        self.last_heading = None
        self.nonempty_lines_since_heading = 0

    def clean_line(self, line):
        heading = _parse_chapter_heading(line)
        if heading is None:
            if line.strip():
                self.nonempty_lines_since_heading += 1
            return line, None

        if (
            heading == self.last_heading
            and self.nonempty_lines_since_heading <= self.max_gap
        ):
            return "", heading

        self.last_heading = heading
        self.nonempty_lines_since_heading = 0
        return line, None

def build_ad_regex(keywords):
    """把广告词变成模糊正则；关键词中的英文字母忽略大小写"""

    regex_list = []
    for kw in keywords:
        # 在字与字之间允许插入任意字符（包括中文）
        pattern = ".*".join(re.escape(ch) for ch in kw)
        # 内联开关 (?i:...) 让英文字母不区分大小写，作用范围仅限当前关键词
        regex_list.append(f"(?i:{pattern})")
    return "|".join(regex_list)

def clean_text(
    input_file,
    output_file,
    record,
    keywords=None,
    excess_chapter_max_gap=5,
):
    """去除txt文本中的广告行，并修复错别字:
    param input_file: 原始txt文件路径
    param output_file: 清洗后txt文件路径
    param keywords: 广告关键词列表
    param excess_chapter_max_gap: 重复标题之间允许的最大非空正文行数
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
            "速读谷", "速讀谷", "74文学网", "82中文网", "得奇小说", "deqixs", \
            "记住我们网", "最新小说首发", "写到这里读者", "写到这里书友", \
            "全网最快小说站", "小说网首发", "搜索小说网", "收藏唯一网址", "查看最新地址", \
            "记住更新地址",  "提醒您查看最新内容", "请到查看", \
            "本章未完", "点击下一页继续阅读", "??????????", "wapcom", "追书app"]

    # 编译广告正则
    ad_pattern = re.compile(build_ad_regex(keywords))
    
    wrong_count = 0
    ad_count = 0
    excess_chapter_name_count = 0
    excess_chapter_name_record = Path(record).with_name("excess_chapter_name.txt")
    excess_chapter_name_cleaner = _ExcessChapterNameCleaner(
        max_gap=excess_chapter_max_gap
    )
    
    # 先检测编码
    with open(input_file, 'rb') as f_in:
        raw_data = f_in.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    with open(input_file, "r", encoding=encoding) as fin, \
         open(output_file, "w", encoding=encoding) as fout, \
         open(record, "w", encoding=encoding) as frec, \
         open(excess_chapter_name_record, "w", encoding=encoding) as fexc:

        for line_no, line in enumerate(fin, start=1):
            # 1. 错别字替换
            for wrong, correct in typo_dict.items():
                if wrong in line:
                    line = line.replace(wrong, correct)
                    wrong_count = wrong_count + 1

            # 2. 去除多余的章节标题
            original_line = line
            line, removed_heading = excess_chapter_name_cleaner.clean_line(line)
            if removed_heading is not None:
                line_no_normal = pad_to_width(str(line_no), 12)
                fexc.write(f"[line {line_no_normal}] {original_line}")
                if not original_line.endswith(("\n", "\r")):
                    fexc.write("\n")
                excess_chapter_name_count = excess_chapter_name_count + 1

                # 标题占满整行时不再向正文写入空行
                if not line.strip():
                    continue

            # 3. 正则广告检测
            matches = ad_pattern.findall(line)
            if len(matches) < 1:
                fout.write(line)
            else:
                line_no_normal = pad_to_width(str(line_no), 12)
                frec.write(f"[line {line_no_normal}] {line}")
                ad_count = ad_count + 1
    
    print(
        f"共修正错别字{wrong_count}个，去除广告{ad_count}句，"
        f"去除冗余标题{excess_chapter_name_count}个。"
    )


if __name__ == "__main__":
    file_name = "578-628.txt"
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