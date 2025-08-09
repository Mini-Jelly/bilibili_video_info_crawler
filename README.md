# bilibili_video_info_crawler
A Python script I wrote to grab bilibili video information. If bilibili sees it, don't block the interface~~🙏🙏🙏

# 如何使用？
1. 安装Python环境
2. 下载 `firstGet.py` 和 `secondGet.py` 文件
3. 打开B站，打开要获取的UP主的个人主页
4. 看右下角，复制UP主的个人ID，粘贴到`firstGet.py`中的**全局参数配置**
5. 在个人主页中点击**查看更多**
6. F12打开浏览器的开发者工具，点击**网络**
7. 使用 **Ctrl + R** 强制刷新网页
8. 在开发者工具中找到名称为 "search?pn=1&ps=40&tid........" 的一条请求，点开它
9. 复制这条请求右边的**请求网址**，粘贴到`firstGet.py`中的**全局参数配置**
10. 往下拉，找到**cookie**，把**cookie**中的内容也粘贴到`firstGet.py`中的**全局参数配置**
11. 使用Python命令运行脚本，`py ./firstGet.py`，这个时候你就会得到一个txt文件
12. 这个时候运行`py ./secondGet.py`，你就能获取到一个CSV文件，里面的数据就是UP主中第一页的视频数据
13. 如果你想要更多数据，那就切换到你想要获取的视频数据页面，重复6~9步并运行Python脚本
