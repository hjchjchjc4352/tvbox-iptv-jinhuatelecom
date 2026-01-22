import random
import os

TEST_FILE = "testcctv.txt"
UPSTREAM_FILE = "upstream.txt"
OUTPUT_FILE = "jinhuatelecomiptv.txt"

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

# 读取 testcctv.txt
test_map = {}
if os.path.exists(TEST_FILE):
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "," in line:
                name, url = line.strip().split(",", 1)
                base = url.split("/PLTV")[1]
                if name not in test_map:
                    test_map[name] = []
                test_map[name].append(base)

# 读取上游 IPTV
channels = []
with open(UPSTREAM_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if "," in line:
            name, url = line.strip().split(",", 1)
            base = url.split("/PLTV")[1]
            channels.append((name, base))

def normalize_name(name):
    """智能频道名处理：CCTV1综合高清 → CCTV-1综合"""
    name = name.replace("高清", "").replace("频道", "")
    name = name.replace("综合", "综合")
    name = name.replace("CCTV", "CCTV-")
    name = name.replace("--", "-")
    # CCTV-1综合高清 → CCTV-1综合
    if "CCTV-" in name:
        parts = name.split("CCTV-")[1]
        num = ""
        for c in parts:
            if c.isdigit():
                num += c
            else:
                break
        return f"CCTV-{num}综合"
    return name

out = open(OUTPUT_FILE, "w", encoding="utf-8")

for name, base in channels:
    clean_name = normalize_name(name)

    # testcctv.txt 有对应频道
    if clean_name in test_map:
        bases = test_map[clean_name]
    else:
        bases = [base]

    # 多线路生成
    for b in bases:
        ips = DEFAULT_IPS.copy()
        random.shuffle(ips)
        for ip in ips:
            out.write(f"{clean_name},rtsp://{ip}:554/PLTV{b}\n")

out.close()
print("Rewrite completed successfully.")
