import os
import requests

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

    # 1. 获取云端所有的文件名（通过 key 推导或者直接从 URL 中提取）
    # 由于 KV 的 key 可能带后缀（如 CCTV1.png），我们建立一个映射：{ 文件名: 下载直链 }
    cloud_files = {}
    for name_key, url in cloud_data.items():
        # 从 URL 路径中安全解析出真实的文件名和后缀
        filename = os.path.basename(url.split('?')[0])
        cloud_files[filename] = url

    # 2. 获取本地 GitHub 仓库已有的台标文件
    local_files = set(os.listdir(LOGO_DIR))
    # 过滤掉隐藏文件
    local_files = {f for f in local_files if not f.startswith('.')}

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

    # 5. 执行下载（KV里新增的，GitHub同步下载保存）
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    for filename in to_download:
        url = cloud_files[filename]
        file_path = os.path.join(LOGO_DIR, filename)
        try:
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                print(f"📥 [下载新增] {filename}")
            else:
                print(f"⚠️ 下载失败 {filename}, 状态码: {res.status_code}")
        except Exception as e:
            print(f"❌ 下载异常 {filename}: {e}")

    print("✨ 台标备份同步完成！")

if __name__ == "__main__":
    main()
