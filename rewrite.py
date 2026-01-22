import random

# 你 testcctv.txt 的参考源
TEST_FILE = "testcctv.txt"

# 上游同步来的 IPTV 文件
UPSTREAM_FILE = "upstream.txt"

# 输出文件（覆盖你的仓库）
OUTPUT_FILE = "Hangzhou_Telecom_Unicast.txt"

# 你要求的默认 IP 池（排除 102 和 109）
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
with open(TEST_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if "," in line:
            name, url = line.strip().split(",", 1)
            base = url.split("/PLTV")[1]  # 取后半段
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

# 输出文件
out = open(OUTPUT_FILE, "w", encoding="utf-8")

for name, base in channels:
    # 统一频道名格式
    clean_name = name.replace("高清", "").replace("综合", "").replace("CCTV", "CCTV-").replace("--", "-")

    # 如果 testcctv.txt 有对应频道
    if clean_name in test_map:
        bases = test_map[clean_name]
    else:
        # testcctv.txt 没有 → 使用默认 IP 池
        bases = [base]

    # 生成多线路
    for b in bases:
        ips = DEFAULT_IPS.copy()
        random.shuffle(ips)
        for ip in ips:
            out.write(f"{clean_name},{'rtsp://' + ip + ':554/PLTV' + b}\n")

out.close()
