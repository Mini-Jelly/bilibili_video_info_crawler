# firstGet.py
# 读取链接文本文件？链接会过期，除非你在短时间内将链接全部获取（可用JavaScript脚本），后续更新预告

import requests
import datetime
import os

# ================== 全局参数配置 ==================
# up主的id
global_upId = ""
# 请求的链接
# 需要从up主所有视频页码中的最后一页开始能保证顺序，不过无所谓，到后面导出为表格数据的话你可以自己筛选
global_url = ""
# 本脚本获取链接是需要cookie的，也就是需要在登录状态下的，打开F12查看并复制即可
global_Cookie = ""

# ================== 函数定义 ==================
def get_existing_bvs(file_path):
    """
    读取文件中的已有 BV 号，返回集合用于去重
    """
    if not os.path.exists(file_path):
        return set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        bvs = set()
        for line in lines:
            line = line.strip()
            if line.startswith("BV") and len(line) >= 10 and line[2] == "1":
                # 匹配 BV1xxx 格式（B站 BV 号一般以 BV 开头）
                # 暂时不知道有没有BV2XX
                bvs.add(line)
        print(f"✅ 已从文件中加载 {len(bvs)} 个 BV 号用于去重")
        return bvs
    except Exception as e:
        print(f"❌ 读取旧文件失败！错误: {e}")
        return set()


def save_bvs_to_file(new_bvs, author_name, file_path):
    """
    将新的 BV 号列表写入文件，插入到最前面，避免重复
    """
    existing_bvs = get_existing_bvs(file_path)

    # 过滤重复项
    new_unique_bvs = []
    for bv in new_bvs:
        if bv not in existing_bvs:
            new_unique_bvs.append(bv)

    if not new_unique_bvs:
        print("ℹ️ 没有新增的 BV 号，无需更新文件。")
        return

    # 生成时间戳
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    # 构建新内容（新数据在前，旧数据在后）
    content_lines = [
        f"===【UP主】: {author_name}【保存时间】: {now}【新增 BV 号数量】: {len(new_unique_bvs)}===",
        *new_unique_bvs,
    ]
    if len(existing_bvs) != 0:
        content_lines.append(f"--- 以下为历史记录（共 {len(existing_bvs)} 条） ---")

    # 读取原文件，并添加元信息
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                old_content = f.read().strip()  # 读取文件内容，并去掉前后多余的空白字符
            # 如果文件内容不为空，将内容添加到 content_lines 列表中
            if old_content:
                content_lines.append(old_content)
        except Exception as e:
            print(f"⚠️ 无法读取旧文件内容：{e}")

    # 写入文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))
        print(f"✅ 新增 {len(new_unique_bvs)} 个 BV 号，已写入文件: {file_path}")
    except Exception as e:
        print(f"❌ 写入文件失败！错误: {e}")


def getBV():
    """
    获取指定用户最新视频列表，并与已有文件合并去重，新数据插入头部。
    """
    headers = {
        "Cookie": global_Cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Referer": f"https://space.bilibili.com/{global_upId}/upload/video",
    }

    try:
        print("🟡正在请求数据...")
        response = requests.get(url=global_url, headers=headers, timeout=10)
        response.raise_for_status()
        jsonData = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败！错误信息: {e}")
        exit(1)

    if jsonData["code"] != 0:
        print(
            f"❌ 获取数据失败！错误码: {jsonData['code']}, 错误信息: {jsonData['message']}"
        )
        exit(1)

    print("✅ 数据获取成功，开始解析JSON数据...")

    # 提取 UP 主名字（从第一个视频或接口返回中获取）
    try:
        author_name = jsonData["data"]["list"]["vlist"][0]["author"]
    except (IndexError, KeyError) as e:
        print("⚠️ 无法提取 UP 主名字，默认使用 'unknown'。")
        author_name = "unknown"

    # 获取当前时间用于命名
    output_dir = "bvids"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{author_name}.txt"
    file_path = os.path.join(output_dir, filename)

    # 提取所有 BV 号
    new_bvs = []
    vlist = jsonData["data"]["list"]["vlist"]
    for index in vlist:
        bvid = index.get("bvid", "")
        if bvid:
            new_bvs.append(bvid)

    print(f"📊 已解析出 {len(new_bvs)} 个 BV 号")

    # 保存到文件（插入头部 + 去重）
    save_bvs_to_file(new_bvs, author_name, file_path)


# ================== 主程序入口 ==================
if __name__ == "__main__":
    getBV()
