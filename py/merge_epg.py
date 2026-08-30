import xml.etree.ElementTree as ET
import urllib.request
import os
import gzip

# 定义你要合并的 EPG 远程源地址列表（已完美支持 .xml 和 .gz 格式）
EPG_URLS = [
    # 51zmt 的经典国内节目单（含央视、卫视及部分省级频道详情，自动支持 .gz 解压）
    "http://epg.51zmt.top:8000/e1.xml.gz",
    "https://epg.v1.mk/fy.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/main/output/4g.xml"  # 替换成你的第二个 EPG 源地址
]

def download_xml(url, output_path):
    """下载并自动解压 XML 或 Gzip 压缩的 XML 文件"""
    print(f"正在下载 EPG 源: {url}")
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            
            # 如果链接以 .gz 结尾，或者内容特征符合 gzip 压缩，则自动解压
            if url.endswith('.gz') or content.startswith(b'\x1f\x8b'):
                print(" -> 检测到 Gzip 压缩包，正在自动解压...")
                content = gzip.decompress(content)
                
            with open(output_path, 'wb') as f:
                f.write(content)
                
        print(f"下载并处理成功: {output_path}")
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False

def parse_epg(file_path):
    """解析 EPG 文件的 channel 和 programme 节点"""
    if not os.path.exists(file_path):
        return [], []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        channels = root.findall('channel')
        programmes = root.findall('programme')
        return channels, programmes
    except Exception as e:
        print(f"解析 XML 出错 {file_path}: {e}")
        return [], []

def merge_multiple_epgs():
    temp_files = []
    all_channels = []
    all_programmes = []
    
    # 1. 依次下载并解析所有源
    for i, url in enumerate(EPG_URLS):
        temp_file = f"temp_epg_{i}.xml"
        if download_xml(url, temp_file):
            temp_files.append(temp_file)
            channels, programmes = parse_epg(temp_file)
            all_channels.extend(channels)
            all_programmes.extend(programmes)
            
    if not temp_files:
        print("错误：没有成功下载任何 EPG 源！")
        return False

    print(f"\n总计获取到原始频道节点: {len(all_channels)} 个，节目单节点: {len(all_programmes)} 个")

    # 2. 根节点构建
    root = ET.Element('tv')
    
    # 3. 频道去重 (基于 channel id)
    seen_channels = set()
    unique_channels_count = 0
    for channel in all_channels:
        ch_id = channel.get('id')
        if ch_id and ch_id not in seen_channels:
            seen_channels.add(ch_id)
            root.append(channel)
            unique_channels_count += 1
            
    # 4. 节目单去重 (基于 频道id + 开始时间 + 结束时间)
    seen_programmes = set()
    unique_programmes_count = 0
    for prog in all_programmes:
        ch = prog.get('channel')
        start = prog.get('start')
        stop = prog.get('stop')
        if ch and start and stop:
            prog_key = (ch, start, stop)
            if prog_key not in seen_programmes:
                seen_programmes.add(prog_key)
                root.append(prog)
                unique_programmes_count += 1

    print(f"合并后去重结果 -> 频道: {unique_channels_count} 个，节目单: {unique_programmes_count} 条")

    # 5. 生成最终的合并 EPG 文件
    output_filename = "epg.xml"
    tree = ET.ElementTree(root)
    # 美化 XML 格式缩进
    ET.indent(tree, space="  ", level=0)
    tree.write(output_filename, encoding='utf-8', xml_declaration=True)
    print(f"全新合并 EPG 已成功生成: {output_filename}")

    # 6. 清理临时下载文件
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    return True

if __name__ == '__main__':
    merge_multiple_epgs()
