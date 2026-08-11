import os
import requests
from urllib.parse import unquote

# 配置路径
BASE_PATH = os.getcwd()
LOGO_DIR = os.path.join(BASE_PATH, "logo")  # 仓库中存放台标的文件夹
JSON_API = "https://tb.yubo.qzz.io/json"

def main():
    os.makedirs(LOGO_DIR, exist_ok=True)
    
    print(f"📡 正在获取 Cloudflare KV 索引: {JSON_API}")
    try:
        response = requests.get(JSON_API, timeout=30)
        if response.status_code != 200:
            print(f"❌ 获取云端 JSON 失败，状态码: {response.status_code}")
            return
        cloud_data = response.json() # 格式如：{"CCTV1": "https://.../CCTV1.png", ...}
    except Exception as e:
        print(f"❌ 请求云端接口异常: {e}")
        return

    # 1. 建立完美的映射：将云端 Key/URL 解析为干净的解码文件名
    cloud_files = {}
    for name_key, url in cloud_data.items():
        # 优先使用 KV 的 Key 作为文件名进行解码清理（防止 URL 编码污染）
        clean_key = unquote(unquote(str(name_key)))
        
        # 确保文件名带有 .png 后缀
        if not clean_key.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            filename = clean_key + ".png"
        else:
            filename = clean_key
            
        cloud_files[filename] = url

    # 2. 获取本地 GitHub 仓库已有的台标文件
    if os.path.exists(LOGO_DIR):
        local_files = set(os.listdir(LOGO_DIR))
        local_files = {f for f in local_files if not f.startswith('.')}
    else:
        local_files = set()

    cloud_file_set = set(cloud_files.keys())

    # 3. 计算增删
    to_download = cloud_file_set - local_files
    to_delete = local_files - cloud_file_set

    print(f"📊 同步对比结果 -> 需要新增/更新: {len(to_download)} 个, 需要删除: {len(to_delete)} 个")

    # 4. 执行删除（KV里删了，GitHub同步删）
    for filename in to_delete:
        file_path = os.path.join(LOGO_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ [删除本地] {filename}")

    # 5. 执行下载（保存为干净的正常名字）
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    success_count = 0
    for filename in to_download:
        url = cloud_files[filename]
        file_path = os.path.join(LOGO_DIR, filename)
        try:
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                print(f"📥 [下载保存] {filename}")
                success_count += 1
            else:
                print(f"⚠️ 下载失败 {filename}, 状态码: {res.status_code}")
        except Exception as e:
            print(f"❌ 下载异常 {filename}: {e}")

    print(f"✨ 台标同步完成！成功下载 {success_count} 个文件（名字已全部转为正常字符）。")

if __name__ == "__main__":
    main()
