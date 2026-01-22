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
            if "," in line and "/PLTV" in line:
                name, url = line.strip().split(",", 1)
                base = url.split("/PLTV", 1)[1]
                test_map.setdefault(name, []).append(base)

with open(UPSTREAM_FILE, "r", encoding="utf-8") as f:
    upstream_lines = f.readlines()

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for line in upstream_lines:

        line = line.strip()

        # 分类行格式：分类名,#genre#
        if line.endswith(",#genre#"):
            out.write(line + "\n")
            continue

        # 频道行
        if "," in line and "/PLTV" in line:
            name, url = line.split(",", 1)
            base = url.split("/PLTV", 1)[1]

            # testcctv.txt 优先
            if name in test_map:
                bases = test_map[name]
            else:
                bases = [base]

            # 多线路生成
            for b in bases:
                ips = DEFAULT_IPS.copy()
                random.shuffle(ips)
                for ip in ips:
                    out.write(f"{name},rtsp://{ip}:554/PLTV{b}\n")

print("rewrite.py 执行完毕")
