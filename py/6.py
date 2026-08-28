import hashlib
import json
import requests
import os

JSON_URL = "https://tb.yubo.qzz.io/json"
LOCAL_CACHE_PATH = "py/json_cache.json"  # 用于记录上一次内容的缓存文件

def check_content_changed():
    try:
        # 1. 获取远程最新的 JSON 内容
        response = requests.get(JSON_URL, timeout=10)
        remote_data = response.text
        
        # 2. 计算当前远程内容的 MD5
        remote_md5 = hashlib.md5(remote_data.encode('utf-8')).hexdigest()
        
        # 3. 读取本地上一次记录的缓存文件
        local_md5 = ""
        if os.path.exists(LOCAL_CACHE_PATH):
            with open(LOCAL_CACHE_PATH, 'r', encoding='utf-8') as f:
                local_md5 = f.read().strip()
                
        # 4. 对比 MD5
        if remote_md5 == local_md5:
            print("✨ 远程 JSON 内容无变化，跳过同步。")
            return False
            
        # 5. 如果有变化，把新的 MD5 写入本地缓存
        os.makedirs(os.path.dirname(LOCAL_CACHE_PATH), exist_ok=True)
        with open(LOCAL_CACHE_PATH, 'w', encoding='utf-8') as f:
            f.write(remote_md5)
            
        print("🚀 检测到远程 JSON 内容已更新，开始执行同步...")
        return True
    except Exception as e:
        print(f"❌ 检查更新失败: {e}")
        return False

if __name__ == "__main__":
    if check_content_changed():
        # === 在这里写你原本的台标下载、处理、保存逻辑 ===
        pass
