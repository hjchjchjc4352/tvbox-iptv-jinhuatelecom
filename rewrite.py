import random
import os
import re

# ================= 基本文件 =================
TEST_FILE = "testcctv.txt"
UPSTREAM_FILE = "upstream.txt"
LOGO_M3U = "Hangzhou_Telecom_Unicast_ONLINE_LOGO.m3u"

OUTPUT_TXT = "jinhuatelecomiptv.txt"
OUTPUT_M3U = "jinhuatelecomiptv.m3u"

EPG_URL = "https://myepg.org/Zhejiang_Telecom_IPTV/EPG/hz_uni_epg.xml.gz"

# ================= IP =================
DEFAULT_IPS = [
    "115.233.43.100",
    "115.233.43.101",
    "115.233.43.103",
    "115.233.43.104",
    "115.233.43.105",
    "115.233.43.106",
    "115.233.43.107",
    "115.233.43.108",
    "115.233.43.110",
    "115.233.43.111",
]

SPECIAL_CHANNEL = "金华新闻综合"
TARGET_GENRE = "地方标清,#genre#"

# ================= 读取 testcctv.txt =================
test_map = {}
test_full_urls = {}

if os.path.exists(TEST_FILE):
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "," not in line:
                continue

            name, url = line.split(",", 1)
            test_full_urls.setdefault(name, []).append(url)

            if "/PLTV" in url:
                base = url.split("/PLTV", 1)[1]
                test_map.setdefault(name, []).append(base)

# ================= 读取 upstream =================
with open(UPSTREAM_FILE, "r", encoding="utf-8") as f:
    upstream_lines = [l.strip() for l in f if l.strip()]

existing_channels = set()
for l in upstream_lines:
    if "," in l and not l.endswith("#genre#"):
        existing_channels.add(l.split(",", 1)[0])

# ================= 插入 金华新闻综合 =================
final_lines = []
inserted = False

for line in upstream_lines:
    final_lines.append(line)

    if line == TARGET_GENRE and not inserted:
        if SPECIAL_CHANNEL not in existing_channels and SPECIAL_CHANNEL in test_full_urls:
            for url in test_full_urls[SPECIAL_CHANNEL]:
                final_lines.append(f"{SPECIAL_CHANNEL},{url}")
            inserted = True

# ================= 生成 TXT =================
output_lines = []

for line in final_lines:
    if line.endswith(",#genre#"):
        output_lines.append(line)
        continue

    if "," in line and "/PLTV" in line:
        name, url = line.split(",", 1)

        # 金华新闻综合：保持原样
        if name == SPECIAL_CHANNEL:
            output_lines.append(line)
            continue

        base = url.split("
