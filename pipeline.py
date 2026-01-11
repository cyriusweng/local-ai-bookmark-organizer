import os
import json
import argparse
import time
from bs4 import BeautifulSoup
import ollama
from tqdm import tqdm
import urllib3
from urllib.parse import urlparse

# 引入抗指纹浏览器库
from curl_cffi import requests as crequests

# --- 1. 全局配置 (Configuration) ---
BASE_DIR = '/Users/cyriusweng/0-Inbox/bookmarks'
INPUT_HTML = os.path.join(BASE_DIR, 'bookmarks.html')

FILE_RAW = os.path.join(BASE_DIR, '1_raw.json')
FILE_ENRICHED = os.path.join(BASE_DIR, '2_enriched.json')
FILE_TAGGED = os.path.join(BASE_DIR, '3_tagged.json')
FILE_CATEGORIZED = os.path.join(BASE_DIR, '4_categorized.json')
OUTPUT_FINAL = os.path.join(BASE_DIR, 'final_bookmarks.html')

MODEL_NAME = 'qwen2.5:3b'
IMPERSONATE_BROWSER = "chrome124"
TIMEOUT = 15

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 工具函数：提取域名 ---
def get_domain(url):
    try:
        domain = urlparse(url).netloc
        return domain if domain else "Unknown Domain"
    except:
        return "Invalid URL"

# --- 模块 1: 摄入 (Ingestion) ---
def step1_ingestion():
    print("🚩 [Step 1] 开始摄入书签...")
    if not os.path.exists(INPUT_HTML):
        print(f"❌ 错误: 找不到 {INPUT_HTML}")
        return

    with open(INPUT_HTML, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    items = soup.find_all('a')
    bookmarks = []
    
    print(f"🔍 扫描到 {len(items)} 个链接。正在清洗数据...")
    for item in items:
        url = item.get('href')
        if url and url.startswith('http'):
            bookmarks.append({
                "id": len(bookmarks),
                "url": url,
                "user_title": item.text.strip(),
            })
            
    with open(FILE_RAW, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)
    print(f"✅ [Step 1] 完成。已保存至 {FILE_RAW}")


# --- 模块 2: 浓缩 (Enrichment) ---
def step2_enrichment():
    print("🚩 [Step 2] 开始高鲁棒性抓取...")
    if not os.path.exists(FILE_RAW):
        print("❌ 请先运行 Step 1")
        return

    with open(FILE_RAW, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)

    SOFT_404_INDICATORS = ["domain for sale", "domain expired", "404 not found", "page not found", "godaddy"]

    for bm in tqdm(bookmarks, desc="Fetching Metadata"):
        if 'status' in bm and bm['status'] != 'pending': continue

        try:
            response = crequests.get(bm['url'], impersonate=IMPERSONATE_BROWSER, timeout=TIMEOUT, verify=False)
            
            if response.status_code in [404, 410]:
                bm['status'] = 'dead'
            elif response.status_code in [401, 403, 406, 429, 503]:
                bm['status'] = 'alive_but_blocked'
                bm['site_title'] = bm['user_title']
            elif 200 <= response.status_code < 300:
                if response.encoding is None: response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else ""

                if any(ind in title.lower() for ind in SOFT_404_INDICATORS):
                    bm['status'] = 'dead'
                else:
                    bm['status'] = 'alive'
                    bm['site_title'] = title
                    meta_keys = soup.find('meta', attrs={'name': 'keywords'})
                    bm['seo_keywords'] = meta_keys.get('content', '')[:800] if meta_keys else ""
                    meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    bm['seo_description'] = meta_desc.get('content', '')[:800] if meta_desc else ""
            else:
                bm['status'] = f'unknown_{response.status_code}'
        except Exception as e:
            bm['status'] = 'error'
            bm['error_detail'] = str(e)[:30]

        if bm['id'] % 10 == 0:
            with open(FILE_ENRICHED, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, indent=2, ensure_ascii=False)

    with open(FILE_ENRICHED, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)
    print(f"✅ [Step 2] 完成。")


# --- 模块 3: 全维度透视 (Analysis - Maximum Information Density) ---
def step3_analysis():
    print(f"🚩 [Step 3] AI 全维度深度分析 (适配 Dolphin-Llama3 直出模式)...")
    if not os.path.exists(FILE_ENRICHED):
        print("❌ 请先运行 Step 2")
        return

    with open(FILE_ENRICHED, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)

    for bm in tqdm(bookmarks, desc="AI Processing"):
        if 'ai_tags' in bm: continue

        domain_fallback = f"Domain: {get_domain(bm['url'])}"
        
        # 逻辑保留：死链但有用户命名的，依然尝试分析
        if bm.get('status') == 'dead' and len(bm['user_title']) < 5:
            bm['ai_tags'] = f"Dead Link, {domain_fallback}"
            continue

        print(f"\n[正在分析]: {bm['user_title']}")
        
        # 依然构建高密度上下文，确保 Dolphin 也能看到这些信息
        context_input = f"""
        - User's Bookmark Title: {bm['user_title']}
        - Page Meta Title: {bm.get('site_title', 'N/A')}
        - URL Structure: {bm['url']}
        - SEO Keywords: {bm.get('seo_keywords', 'N/A')}
        - Content Summary: {bm.get('seo_description', 'N/A')}
        """
        
        # --- 修改点 1: 针对 Dolphin-Llama3 的 Prompt 优化 ---
        # 移除了所有 <think> 相关的指令，改为标准的指令跟随格式
        prompt = f"""
        You are a smart bookmark organizer.
        
        [Task]
        Identify the fundamental essence of this bookmark based on the provided context.
        
        [Context Information]
        {context_input}
        
        [Rules]
        1. **Crucial**: Trust the 'User's Bookmark Title' the most. It reveals the user's specific intent.
        2. **Crucial**: Output **ONLY** the tags, separated by commas!!!
        3. MUST NOT output any introductory text, explanations, or "Here are the tags". Output ONLY JUST the tags.
        4. Never output like: "Based on the provided context information, I would categorize this bookmark as follows:", or "And here are the corresponding tags:".
        
        [Example Output]
        Python, Data Visualization, Matplotlib
        """

        try:
            # Dolphin 系列通常很听话，不使用 stream 也可以，但保留 stream 可以让你看到进度
            stream = ollama.chat(
                model=MODEL_NAME, 
                messages=[{'role': 'user', 'content': prompt}],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                print(content, end='', flush=True) # 实时打印 tags，方便确认
            print("") # 换行
            
            # --- 修改点 2: 简化的解析逻辑 ---
            # 直接清理首尾空白和可能的引号
            result = full_response.strip().replace('"', '').replace("'", "")
            
            # 简单的脏数据过滤
            if len(result) < 2 or "sorry" in result.lower() or "cannot" in result.lower():
                bm['ai_tags'] = domain_fallback
            else:
                bm['ai_tags'] = result
                
        except Exception as e:
            print(f"❌ Error: {e}")
            bm['ai_tags'] = domain_fallback

        # 每 10 条保存一次 (不需要像 R1 那么频繁了，因为速度会快很多)
        if bm['id'] % 10 == 0:
            with open(FILE_TAGGED, 'w', encoding='utf-8') as f:
                json.dump(bookmarks, f, indent=2, ensure_ascii=False)

    with open(FILE_TAGGED, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)
    print(f"✅ [Step 3] 完成。")

# --- 模块 3.5: 上帝视角 (Taxonomy Generation) ---
# 这一步是连接 "微观标签" 和 "宏观分类" 的桥梁
def step3_5_taxonomy_gen():
    print(f"🚩 [Step 3.5] AI 构建动态分类体系 (基于 {MODEL_NAME})...")
    if not os.path.exists(FILE_TAGGED):
        print("❌ 请先运行 Step 3")
        return

    import collections
    
    # 1. Python 负责脏活：收集、清洗、去重、统计频率
    with open(FILE_TAGGED, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)

    all_tags = []
    print("   -> 正在聚合所有标签...")
    for bm in bookmarks:
        if 'ai_tags' in bm and "Domain:" not in bm['ai_tags']:
            # 分割、去空、转小写以便统计（但保留原格式用于展示）
            tags = [t.strip() for t in bm['ai_tags'].split(',') if len(t.strip()) > 1]
            all_tags.extend(tags)

    # 统计频率
    tag_counts = collections.Counter(all_tags)
    unique_tags_count = len(tag_counts)
    print(f"   -> 共发现 {len(all_tags)} 个标签，其中去重后有 {unique_tags_count} 个唯一标签。")

    # 策略：取 Top 500 高频标签 + 随机 100 个低频标签作为样本，
    # 既保证核心分类准确，又照顾到长尾内容，防止 token 溢出（虽然 Qwen 支持长文本，但太长会影响推理质量）
    most_common = [t[0] for t in tag_counts.most_common(500)]
    
    # 构建 Prompt context
    tags_block = ", ".join(most_common)
    
    print("   -> 正在请求 AI 归纳分类树 (这可能需要 1-2 分钟)...")
    
    prompt = f"""
    [Context]
    I have a collection of browser bookmarks tagged with the following keywords. 
    These are the most frequent tags used in my collection:
    
    {tags_block}
    
    [Task]
    Analyze these tags to understand the user's interests and work domains.
    Create a Hierarchical Taxonomy (Classification System) that covers these topics.
    
    [Requirements]
    1. Summarize these into 10-15 High-Level Categories (Level 1).
    2. For each Level 1 category, provide 3-6 distinct Sub-Categories (Level 2).
    3. The system must be MECE (Mutually Exclusive, Collectively Exhaustive).
    4. Keep category names professional, concise, and academic (English).
    
    [Output Format]
    Return ONLY a JSON object. No markdown formatting, no explanations.
    Structure:
    {{
        "Taxonomy": {{
            "Category Name 1": ["Subcat A", "Subcat B", "Subcat C"],
            "Category Name 2": ["Subcat X", "Subcat Y"]
        }}
    }}
    """

    try:
        response = ollama.chat(
            model=MODEL_NAME, # 此时应为 qwen2.5:3b
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.2} # 低温度，保证逻辑严密
        )
        
        content = response['message']['content']
        # 清洗可能存在的 Markdown 代码块标记
        content = content.replace("```json", "").replace("```", "").strip()
        
        taxonomy = json.loads(content)
        
        # 保存这个生成的分类树，供 Step 4 使用
        TAXONOMY_FILE = os.path.join(BASE_DIR, 'taxonomy_config.json')
        with open(TAXONOMY_FILE, 'w', encoding='utf-8') as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)
            
        print(f"✅ [Step 3.5] 分类树构建完成！已保存至 {TAXONOMY_FILE}")
        print("   -> 预览生成的顶级分类:")
        for key in taxonomy.get("Taxonomy", {}).keys():
            print(f"      - {key}")

    except Exception as e:
        print(f"❌ Error extracting taxonomy: {e}")
        print(f"Raw output was: {content[:100]}...")


# --- 模块 4: 架构 (Architecture - 动态分类版) ---
def step4_categorization():
    print(f"🚩 [Step 4] AI 归类执行 (基于动态生成的分类树)...")
    
    TAXONOMY_FILE = os.path.join(BASE_DIR, 'taxonomy_config.json')
    if not os.path.exists(FILE_TAGGED):
        print("❌ 请先运行 Step 3")
        return
    
    # 读取 AI 在 Step 3.5 生成的分类树
    custom_taxonomy = {}
    if os.path.exists(TAXONOMY_FILE):
        with open(TAXONOMY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            custom_taxonomy = data.get("Taxonomy", {})
            print("   -> 已加载自定义分类树。")
    else:
        print("⚠️ 未找到分类树文件，请先运行 Step 3.5！(或者在此处回退到硬编码列表)")
        return

    # 将字典转换为 Prompt 友好的字符串
    taxonomy_str = json.dumps(custom_taxonomy, indent=2)

    with open(FILE_TAGGED, 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)

    for bm in tqdm(bookmarks, desc="Categorizing"):
        if 'category' in bm: continue 

        tags = bm.get('ai_tags', '')
        
        # 简单逻辑：死链和纯域名回退
        if "Domain:" in tags:
            bm['category'] = "Unsorted Websites"
            bm['subcategory'] = tags.split("Domain:")[-1].strip()
            continue

        prompt = f"""
        Task: Assign this bookmark to the most appropriate Category and Subcategory from the provided Taxonomy.
        
        [Input Bookmark]
        Title: {bm['user_title']}
        Tags: {tags}
        
        [Reference Taxonomy Tree]
        {taxonomy_str}
        
        [Rules]
        1. You MUST choose one Category (Level 1) and one Subcategory (Level 2) strictly from the Reference list.
        2. Do not invent new categories.
        3. Output format: "Category > Subcategory"
        """

        try:
            # Qwen 2.5 3B 非常适合这种 "Selection" 任务
            response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
            result = response['message']['content'].strip()
            
            # 简单的清洗
            result = result.split('\n')[0].replace('"', '').replace("'", "")
            
            if ">" in result:
                parts = result.split(">")
                bm['category'] = parts[0].strip()
                bm['subcategory'] = parts[1].strip()
            else:
                # 如果 AI 只输出了一个词，尝试在 taxonomy 里找它是属于哪个大类的
                found = False
                for main, subs in custom_taxonomy.items():
                    if result in main:
                        bm['category'] = main
                        bm['subcategory'] = "General"
                        found = True
                        break
                    for sub in subs:
                        if result in sub:
                            bm['category'] = main
                            bm['subcategory'] = sub
                            found = True
                            break
                if not found:
                    bm['category'] = "Miscellaneous"
                    bm['subcategory'] = result
        except:
            bm['category'] = "Error"
            bm['subcategory'] = "Manual Review"

    # 以前的 "Sub-step 4.2: 分类剪枝" 逻辑依然可以用，这里省略以节省篇幅，建议保留原文件中的那部分代码
    
    with open(FILE_CATEGORIZED, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)
    print(f"✅ [Step 4] 完成。")

# --- 模块 5: 建造 (Export - Vivaldi/Chrome 兼容增强版) ---
def step5_export():
    import html  # [新增] 引入 HTML 转义库
    
    print("🚩 [Step 5] 生成 Vivaldi 兼容的 HTML 书签文件...")
    if not os.path.exists(FILE_CATEGORIZED): 
        print("❌ 未找到分类文件，请先运行 Step 4")
        return
        
    with open(FILE_CATEGORIZED, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 构建内存中的分类树
    tree = {}
    count = 0
    for item in data:
        # 兼容处理
        main = item.get('category', 'Uncategorized').strip()
        sub = item.get('subcategory', 'General').strip()
        
        # 简单的层级清理
        if not main: main = "Uncategorized"
        if not sub: sub = "General"
        
        if main not in tree: tree[main] = {}
        if sub not in tree[main]: tree[main][sub] = []
        tree[main][sub].append(item)
        count += 1

    print(f"   -> 准备导出 {count} 个书签...")

    # 写入 Netscape 标准书签格式 (严格兼容模式)
    with open(OUTPUT_FINAL, 'w', encoding='utf-8') as f:
        # [关键修复 1] 添加标准头部和 META 标签，防止浏览器乱码或解析失败
        f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
        f.write('\n')
        f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
        f.write('<TITLE>AI Bookmarks</TITLE>\n')
        f.write('<H1>Bookmarks</H1>\n')
        f.write('<DL><p>\n')
        
        # 排序逻辑
        sorted_keys = sorted(tree.keys(), key=lambda x: (x == "Dead Links", x == "Unsorted Websites", x == "Websites by Domain", x))
        
        for main_cat in sorted_keys:
            # [关键修复 2] 对分类名称也进行转义
            safe_main = html.escape(main_cat)
            f.write(f'    <DT><H3>{safe_main}</H3>\n')
            f.write('    <DL><p>\n')
            
            for sub_cat, items in sorted(tree[main_cat].items()):
                safe_sub = html.escape(sub_cat)
                f.write(f'        <DT><H3>{safe_sub}</H3>\n')
                f.write('        <DL><p>\n')
                
                for item in items:
                    url = item.get('url', '#')
                    title = item.get('user_title', 'Untitled')
                    
                    # [关键修复 3] 核心：对 URL 和标题进行 HTML 转义
                    # 如果不转义，URL 里的 "&" 或标题里的引号会导致导入中断
                    safe_url = html.escape(url)
                    safe_title = html.escape(title)
                    
                    f.write(f'            <DT><A HREF="{safe_url}">{safe_title}</A>\n')
                
                f.write('        </DL><p>\n')
            f.write('    </DL><p>\n')
        f.write('</DL><p>\n')
            
    print(f"🎉 任务全部完成！最终文件已生成: {OUTPUT_FINAL}")
    print("   -> 现在请尝试导入 Vivaldi，应该能显示完整目录结构了。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 修改点 1：在 choices 里加上 35，否则终端会报错说 "invalid choice"
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 35, 4, 5])
    args = parser.parse_args()

    if args.step == 1: 
        step1_ingestion()
    elif args.step == 2: 
        step2_enrichment()
    elif args.step == 3: 
        step3_analysis()
    elif args.step == 35:  # 修改点 2：绑定新写的分类树生成函数
        step3_5_taxonomy_gen()
    elif args.step == 4: 
        step4_categorization()
    elif args.step == 5: 
        step5_export()
