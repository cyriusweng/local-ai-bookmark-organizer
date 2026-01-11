#!/bin/bash

# ==========================================
# Vivaldi/Chrome 书签清理与检测脚本
# 作者: Axis (For Cyrius)
# 功能: 提取书签 -> 去重 -> 检测存活 -> 抓取标题 -> 生成CSV报告
# ==========================================

# 检查输入参数
if [ "$#" -ne 1 ]; then
    echo "用法: $0 <path_to_bookmarks.html>"
    echo "示例: $0 ~/Desktop/bookmarks_1_9_26.html"
    exit 1
fi

INPUT_FILE="$1"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_CSV="bookmark_report_${TIMESTAMP}.csv"
TEMP_URL_LIST="temp_urls_${TIMESTAMP}.txt"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== 开始处理书签文件: $INPUT_FILE ===${NC}"

# 1. 提取 URL 并去重
# Vivaldi 导出的格式通常包含 HREF="..."
echo -e "${YELLOW}[Step 1/3] 正在扫描并去重 URL...${NC}"
grep -oE 'HREF="([^"#]+)"' "$INPUT_FILE" | cut -d'"' -f2 | sort | uniq > "$TEMP_URL_LIST"

TOTAL_URLS=$(wc -l < "$TEMP_URL_LIST" | tr -d ' ')
echo -e "${GREEN}共找到 $TOTAL_URLS 个唯一的 URL。${NC}"

# 初始化 CSV 文件头
echo "Status_Code,Final_URL,Page_Title,Recommendation" > "$OUTPUT_CSV"

# 2. 循环检测
echo -e "${YELLOW}[Step 2/3] 开始逐个访问 (设置延迟以避免被封禁)...${NC}"

CURRENT=0
while IFS= read -r url; do
    ((CURRENT++))
    
    # 进度条效果
    printf "[%d/%d] Checking: %s ... " "$CURRENT" "$TOTAL_URLS" "${url:0:40}"

    # 使用 curl 获取状态码和标题
    # -L: 跟随重定向
    # --max-time 10: 10秒超时，避免卡死
    # -A: 伪装成浏览器 User-Agent，防止被拦截
    response=$(curl -s -L -w "%{http_code}" -o /tmp/curl_body_out --max-time 15 \
        -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
        "$url")
    
    http_code="${response: -3}" # 获取最后3位状态码
    
    # 提取标题 (尝试从下载的临时文件中提取 <title>)
    page_title=$(grep -oE '<title>[^<]+' /tmp/curl_body_out | sed 's/<title>//' | head -n 1)
    
    # 清洗标题中的逗号和引号，防止破坏 CSV 格式
    page_title=$(echo "$page_title" | tr -d '\n\r' | sed 's/"/""/g' | sed 's/,/ /g')
    
    # 简单的分类/保留建议逻辑
    recommendation="Check Manually"
    if [[ "$http_code" == "200" ]]; then
        echo -e "${GREEN}[OK - 200]${NC}"
        recommendation="Keep"
    elif [[ "$http_code" =~ ^3 ]]; then
        echo -e "${GREEN}[Redirect - $http_code]${NC}"
        recommendation="Update URL"
    elif [[ "$http_code" == "404" ]]; then
        echo -e "${RED}[Dead - 404]${NC}"
        recommendation="DELETE"
    elif [[ "$http_code" == "000" ]]; then
        echo -e "${RED}[Network Error]${NC}"
        recommendation="Check DNS/VPN"
    else
        echo -e "${YELLOW}[Status $http_code]${NC}"
        recommendation="Review"
    fi

    # 如果标题为空，且连接成功，标记为 No Title
    if [[ -z "$page_title" ]]; then
        page_title="[No Title Detected]"
    fi

    # 写入 CSV
    echo "$http_code,\"$url\",\"$page_title\",$recommendation" >> "$OUTPUT_CSV"

    # 3. 避免访问过快
    # 建议设置 1-2 秒，如果 URL 很多，可以适当减小，但太快会被 Google/Cloudflare 拦截
    sleep 1.5

done < "$TEMP_URL_LIST"

# 清理临时文件
rm "$TEMP_URL_LIST"
rm /tmp/curl_body_out 2>/dev/null

echo -e "${CYAN}=== 完成! ===${NC}"
echo -e "结果已保存至: ${GREEN}$OUTPUT_CSV${NC}"
echo -e "建议使用 Excel 或 Numbers 打开该 CSV 文件，按 'Recommendation' 或 'Page_Title' 排序进行整理。"