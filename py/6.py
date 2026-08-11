import os
from urllib.parse import unquote

def rename_files():
    logo_dir = "logo"
    if not os.path.exists(logo_dir):
        print(f"❌ 找不到 {logo_dir} 文件夹")
        return

    count = 0
    for filename in os.listdir(logo_dir):
        # 核心：将 URL 编码解码
        decoded_name = unquote(filename)
        
        # 如果解码后的名字和原名不一样，说明需要重命名
        if decoded_name != filename:
            old_path = os.path.join(logo_dir, filename)
            new_path = os.path.join(logo_dir, decoded_name)
            
            # 检查重命名后是否会冲突
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"✅ 重命名: {filename} -> {decoded_name}")
                count += 1
            else:
                print(f"⚠️ 跳过: {decoded_name} 已存在")
    
    print(f"✨ 处理完成，共重命名了 {count} 个文件")

if __name__ == "__main__":
    rename_files()