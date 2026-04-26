import random
import os
import re

# ================= 文件 =================
TEST_FILE = "testcctv.txt"
UPSTREAM_FILE = "upstream.txt"
LOGO_M3U = "Hangzhou_Telecom_Unicast_ONLINE_LOGO.m3u"

OUTPUT_TXT = "jinhuatelecomiptv.txt"
OUTPUT_M3U = "jinhuatelecomiptv.m3u"

OUTPUT_ONE_TXT = "oneiptv.txt"
OUTPUT_ONE_M3U = "oneiptv.m3u"

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

ONE_IP = "115.233.43.111"

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

# ================= 生成多源 TXT =================
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

        base = url.split("/PLTV", 1)[1]
        bases = test_map.get(name, [base])

        for b in bases:
            ips = DEFAULT_IPS.copy()
            random.shuffle(ips)
            for ip in ips:
                output_lines.append(f"{name},rtsp://{ip}:554/PLTV{b}")
    else:
        output_lines.append(line)

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    for l in output_lines:
        f.write(l + "\n")

# ================= 解析 LOGO m3u =================
logo_map = {}

if os.path.exists(LOGO_M3U):
    with open(LOGO_M3U, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("#EXTINF"):
                continue

            name = line.split(",", 1)[1]

            def get(key):
                m = re.search(rf'{key}="([^"]+)"', line)
                return m.group(1) if m else name

            logo_map[name] = {
                "tvg-id": get("tvg-id"),
                "tvg-name": get("tvg-name"),
                "tvg-logo": get("tvg-logo"),
            }

# ================= 生成多源 M3U =================
with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
    f.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')

    current_group = ""

    for line in output_lines:
        if line.endswith(",#genre#"):
            current_group = line.replace(",#genre#", "")
            continue

        if "," not in line:
            continue

        name, url = line.split(",", 1)

        meta = logo_map.get(name, {
            "tvg-id": name,
            "tvg-name": name,
            "tvg-logo": "",
        })

        f.write(
            '#EXTINF:-1 '
            f'tvg-id="{meta["tvg-id"]}" '
            f'tvg-name="{meta["tvg-name"]}" '
            f'tvg-logo="{meta["tvg-logo"]}" '
            f'group-title="{current_group}",'
            f'{name}\n'
        )
        f.write(url + "\n")

# ================= 生成 oneiptv.txt（单源版） =================
one_lines = []
seen_channels = set()

for line in output_lines:
    if line.endswith(",#genre#"):
        one_lines.append(line)
        continue

    if "," not in line:
        continue

    name, url = line.split(",", 1)

    if not url.startswith(f"rtsp://{ONE_IP}:"):
        continue

    if name in seen_channels:
        continue

    seen_channels.add(name)
    one_lines.append(line)

with open(OUTPUT_ONE_TXT, "w", encoding="utf-8") as f:
    for l in one_lines:
        f.write(l + "\n")

# ================= 生成 oneiptv.m3u（单源版） =================
with open(OUTPUT_ONE_M3U, "w", encoding="utf-8") as f:
    f.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')

    current_group = ""

    for line in one_lines:
        if line.endswith(",#genre#"):
            current_group = line.replace(",#genre#", "")
            continue

        if "," not in line:
            continue

        name, url = line.split(",", 1)

        meta = logo_map.get(name, {
            "tvg-id": name,
            "tvg-name": name,
            "tvg-logo": "",
        })

        f.write(
            '#EXTINF:-1 '
            f'tvg-id="{meta["tvg-id"]}" '
            f'tvg-name="{meta["tvg-name"]}" '
            f'tvg-logo="{meta["tvg-logo"]}" '
            f'group-title="{current_group}",'
            f'{name}\n'
        )
        f.write(url + "\n")

print("rewrite.py 执行完成：多源 + 单源 IPTV 已生成")
