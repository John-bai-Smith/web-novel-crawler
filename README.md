目前只支持一个网页：[31小说](https://www.31xs.com/)

使用时在main函数中修改小说名和对应的目录页url即可

————————————————————————————————————————————————

2024/05/15 更新

发现31小说加入了反爬机制，尝试很久无法突破反爬，无奈之下走起了歪门邪道

通过Quicker模拟人类操作浏览器，访问网址并保存html，再用python脚本处理本地html。

此方法理论上十分强大，除了有需要点击“我不是机器人”或做选图片测试的那种检测，一般不会被服务器拒绝。

缺点就是，速度很慢。

Quicker动作库链接如下：

[反爬-下载html](https://getquicker.net/Sharedaction?code=aaf6e0b2-35dc-4040-c2d6-08dc74bc40ca&fromMyShare=True)

使用流程：

0. 确认脚本和Quicker读取文件的路径是否正确（默认是绝对路径，不同计算机上需要单独设置），确认小说名和网址

1. 在小说目录页手动保存html，命名为`content.html`，放在`.\files\`目录下

2. 运行 `extract_chapter_info.py`，获得`chapter_name.txt`和`chapter_url`文件

3. 运行Quicker动作，下载html

4. 将下载好的html文件移动到`.\files\`目录下，运行`local_crawler.py`，获得小说文件
