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

# 读取上游 IPTV
channels = []
with open(UPSTREAM_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if "," in line and "/PLTV" in line:
            name, url = line.strip().split(",", 1)
            base = url.split("/PLTV", 1)[1]
            channels.append((name, base))
        else:
            print(f"跳过无效行（没有 /PLTV）: {line.strip()}")

def normalize_name(name):
    name = name.replace("高清", "").replace("频道", "")
    name = name.replace("CCTV", "CCTV-")
    name = name.replace("--", "-")
    if "CCTV-" in name:
        parts = name.split("CCTV-")[1]
        num = ""
        for c in parts:
            if c.isdigit():
                num += c
            else:
                break
        return f"CCTV-{num}综合"
    return name.strip()

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for name, base in channels:
        clean_name = normalize_name(name)
        bases = test_map.get(clean_name, [base])
        ips = DEFAULT_IPS.copy()
        random.shuffle(ips)
        for b in bases:
            for ip in ips:
                out.write(f"{clean_name},rtsp://{ip}:554/PLTV{b}\n")

print("✅ rewrite.py 执行完毕，输出文件已生成：jinhuatelecomiptv.txt")
