import requests
import datetime
import time
import csv
import os
import re

# ================== 全局配置 ==================
API_URL = "https://api.bilibili.com/x/web-interface/view"
BVID_DIR = "bvids"
OUTPUT_DIR = "results"


# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ================== 提取 BV 号函数 ==================
def extract_bv_numbers_from_file(file_path):
    """
    从单个 txt 文件中提取所有 BV 号
    假设文件中每行或任意位置可能包含 BV1xx... 格式
    """
    BV_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 提取所有符合格式的 BV 号（BV + 10位字符）
        matches = re.findall(r"BV[0-9A-Za-z]{10}", content)
        BV_list.extend(matches)
    except Exception as e:
        print(f"❌ 读取文件失败: {file_path} | 错误: {e}")
    return BV_list


# ================== 获取视频信息函数 ==================
def fetch_video_info(bv_number):
    """
    根据 BV 号获取视频数据
    返回包含详细信息的字典
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Host": "api.bilibili.com",
        "Connection": "keep-alive",
    }
    params = {"bvid": bv_number}

    # 默认失败返回值
    default_data = {
        "BV号": bv_number,
        "作者": -1,
        "作者id": -1,
        "视频时长": -1,
        "发布时间": -1,
        "播放量": -1,
        "点赞": -1,
        "dislike": -1,
        "投币": -1,
        "收藏": -1,
        "转发": -1,
        "评论": -1,
        "弹幕": -1,
        "估价(evaluation)": -1,
        "视频排名": -1,
        "视频分区(旧)": -1,
        "视频分区(新)": -1,
        "点赞率": -1,
    }

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["code"] == 0:
            # 数据预处理
            video_data = data["data"]
            stat = video_data["stat"]

            play_count = stat["view"]
            like_count = stat["like"]
            pub_time = datetime.datetime.fromtimestamp(video_data["pubdate"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            # 计算点赞率
            like_rate = like_count / play_count if play_count > 0 else 0

            return {
                "BV号": bv_number,
                "标题": video_data["title"],
                "作者": video_data["owner"]["name"],
                "作者id": video_data["owner"]["mid"],
                "视频时长": video_data["duration"],
                "发布时间": pub_time,
                "播放量": play_count,
                "点赞": like_count,
                "dislike": stat["dislike"],
                "投币": stat["coin"],
                "收藏": stat["favorite"],
                "转发": stat["share"],
                "评论": stat["reply"],
                "弹幕": stat["danmaku"],
                "估价(evaluation)": stat["evaluation"],
                "视频排名": stat["now_rank"],
                "视频分区(旧)": video_data["tname"],
                "视频分区(新)": video_data["tname_v2"],
                "点赞率": round(like_rate * 100, 2),
            }
        else:
            print(f"⚠️ API 错误 [{bv_number}]: {data.get('message', '未知')}")
            return default_data

    except Exception as e:
        print(f"❌ 请求失败 [{bv_number}]: {e}")
        return default_data


# ================== 主函数 ==================
def main():
    # 获取当前时间用于文件命名
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    # 获取所有 txt 文件
    if not os.path.exists(BVID_DIR):
        print(f"📁 目录不存在: {BVID_DIR}")
        return

    txt_files = [f for f in os.listdir(BVID_DIR) if f.lower().endswith(".txt")]
    if not txt_files:
        print(f"📁 未在 '{BVID_DIR}' 找到任何 .txt 文件。")
        return

    print(f"📄 共找到 {len(txt_files)} 个文件，开始逐个处理...")

    # 定义 CSV 表头
    fieldnames = [
        "BV号",
        "标题作者",
        "作者id",
        "视频时长（秒）",
        "发布时间",
        "播放量",
        "点赞",
        "dislike",
        "投币",
        "收藏",
        "转发",
        "评论",
        "弹幕",
        "估价(evaluation)",
        "视频排名",
        "视频分区(旧)",
        "视频分区(新)",
        "点赞率",
    ]

    # 逐个处理每个文件
    for file_name in txt_files:
        file_path = os.path.join(BVID_DIR, file_name)
        print(f"\n🟡 正在处理txt文件: {file_name}")

        # 提取 BV 号
        bv_numbers = extract_bv_numbers_from_file(file_path)
        if not bv_numbers:
            print(f"❌ 未在 {file_name} 中提取到有效 BV 号")
            continue

        print(f"✅ 在 {file_name} 提取到 {len(bv_numbers)} 个 BV 号")

        # 构造输出文件名：原文件名（不含扩展名） + 时间戳
        name_without_ext = os.path.splitext(file_name)[0]
        output_filename = f"{name_without_ext}_{current_time}.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print("🟡开始根据BV号发送请求...")
        # print(f"正在导出数据至: {output_path}")

        # 写入 CSV
        success_count = 0
        try:
            with open(
                output_path, "w", encoding="utf-8-sig", newline="", errors="ignore"
            ) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for i, bv in enumerate(bv_numbers, start=1):
                    print(f"🔍 [{i}/{len(bv_numbers)}] 请求: {bv}")
                    info = fetch_video_info(bv)
                    writer.writerow(info)
                    if info["播放量"] != -1:
                        success_count += 1
                    time.sleep(0.5)  # 防止请求过快被限流

            print(
                f"✅ 文件 '{file_name}' 处理完成！成功获取 {success_count}/{len(bv_numbers)} 条数据。"
            )

        except Exception as e:
            print(f"❌ 写入文件失败 {output_path}: {e}")

    print(f"\n🎉 所有文件处理完毕！结果已保存至 '{OUTPUT_DIR}' 目录。")


if __name__ == "__main__":
    main()
