import os
from bs4 import BeautifulSoup

# --- 配置 ---
BASE_DIR = '/Users/cyriusweng/0-Inbox/bookmarks'
ORIGINAL_FILE = os.path.join(BASE_DIR, 'bookmarks.html')     # 原始文件 (Step 1 的输入)
FINAL_FILE = os.path.join(BASE_DIR, 'final_bookmarks.html')  # 最终文件 (Step 5 的输出)

def normalize_url(url):
    """
    清洗 URL 以防止因末尾斜杠导致的误判
    例如: 'http://google.com' 和 'http://google.com/' 应视为同一个
    """
    if not url: return ""
    u = url.strip()
    if u.endswith('/'):
        return u[:-1]
    return u

def extract_urls(filepath):
    """从 HTML 文件中提取所有 URL"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return set(), 0
    
    print(f"📖 正在读取: {os.path.basename(filepath)} ...")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    links = soup.find_all('a')
    
    # 使用集合 (Set) 来存储唯一的 URL
    unique_urls = set()
    total_count = 0
    
    for link in links:
        href = link.get('href')
        if href and href.startswith('http'):
            norm_url = normalize_url(href)
            unique_urls.add(norm_url)
            total_count += 1
            
    return unique_urls, total_count

def run_verification():
    print("-" * 40)
    print("🔍 启动完整性校验程序")
    print("-" * 40)

    # 1. 提取原始数据
    orig_set, orig_total = extract_urls(ORIGINAL_FILE)
    print(f"✅ 原始文件: 总链接 {orig_total} 个 | 去重后唯一链接 {len(orig_set)} 个")

    # 2. 提取新数据
    final_set, final_total = extract_urls(FINAL_FILE)
    print(f"✅ 新生成文件: 总链接 {final_total} 个 | 去重后唯一链接 {len(final_set)} 个")

    print("-" * 40)

    # 3. 核心比对逻辑 (集合运算)
    # 丢失的 = 原有的唯一链接 - 现有的唯一链接
    missing_urls = orig_set - final_set
    
    # 4. 输出报告
    if len(missing_urls) == 0:
        print("🎉 完美！没有丢失任何数据。")
        print("   所有原始链接都已存在于新文件中。")
    else:
        print(f"⚠️  警告: 发现 {len(missing_urls)} 个链接在转换过程中丢失！")
        print("   丢失列表如下:")
        for i, url in enumerate(missing_urls, 1):
            print(f"   {i}. {url}")
            
    print("-" * 40)
    
    # 5. 额外检查：有没有新增加的？(通常不应该有，除非 AI 幻觉或者是纠错了 URL)
    added_urls = final_set - orig_set
    if len(added_urls) > 0:
        print(f"ℹ️  提示: 新文件比旧文件多出了 {len(added_urls)} 个唯一链接 (可能是 URL 格式化差异导致)。")

if __name__ == "__main__":
    run_verification()
