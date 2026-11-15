import os

base_dir = r"D:\antigravity\my fyp project\data\real\rice"
if os.path.exists(base_dir):
    print("Rice directory exists. Files inside:")
    for f in os.listdir(base_dir):
        print(f" - {f}")
else:
    print("Rice directory does NOT exist.")
