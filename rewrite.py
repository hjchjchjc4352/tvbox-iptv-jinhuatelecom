import random
import os

TEST_FILE = "testcctv.txt"
UPSTREAM_FILE = "upstream.txt"
OUTPUT_TXT = "jinhuatelecomiptv.txt"
OUTPUT_M3U = "jinhuatelecomiptv.m3u"

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

# ========== 读取 testcctv.txt ==========
test_map = {}          # name -> [base]
test_full_urls = {}    # name -> [full url order]

if os.path.exists(TEST_FILE):
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "," not in line:
                continue

            name, url = line.split(",", 1)

            if "/PLTV" in url:
                base = url.split("/PLTV", 1)[1]
                test_map.setdefault(name, []).append(base)

            test_full_urls.setdefault(name, []).append(url)

# ========== 读取 upstream ==========
with open(UPSTREAM_FILE, "r", encoding="utf-8") as f:
    upstream_lines = [l.strip() for l in f.readlines()]

existing_channels = set()
for l in upstream_lines:
    if "," in l and not l.endswith("#genre#"):
        existing_channels.add(l.split(",", 1)[0])

# ========== 写 txt & 记录顺序 ==========
final_lines = []
inserted_special = False

for i, line in enumerate(upstream_lines):
    final_lines.append(line)

    # 找到“地方标清”分类，准备插入
    if line == TARGET_GENRE and not inserted_special:
        if SPECIAL_CHANNEL not in existing_channels and SPECIAL_CHANNEL in test_full_urls:
            for url in test_full_urls[SPECIAL_CHANNEL]:
                final_lines.append(f"{SPECIAL_CHANNEL},{url}")
            inserted_special = True

# ========== 处理普通频道多线路 ==========
output_lines = []

for line in final_lines:
    if line.endswith(",#genre#"):
        output_lines.append(line)
        continue

    if "," in line and "/PLTV" in line:
        name, url = line.split(",", 1)
        base = url.split("/PLTV", 1)[1]

        if name == SPECIAL_CHANNEL:
            output_lines.append(line)
            continue

        bases = test_map.get(name, [base])

        for b in bases:
            ips = DEFAULT_IPS.copy()
            random.shuffle(ips)
            for ip in ips:
                output_lines.append(f"{name},rtsp://{ip}:554/PLTV{b}")
    else:
        output_lines.append(line)

# ========== 写 TXT ==========
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    for l in output_lines:
        f.write(l + "\n")

# ========== 生成 M3U ==========
with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    current_group = ""

    for line in output_lines:
        if line.endswith(",#genre#"):
            current_group = line.replace(",#genre#", "")
            continue

        if "," in line:
            name, url = line.split(",", 1)
            f.write(f'#EXTINF:-1 group-title="{current_group}",{name}\n')
            f.write(url + "\n")

print("rewrite.py 执行完毕（TXT + M3U）")
