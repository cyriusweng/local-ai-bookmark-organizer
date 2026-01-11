#!/bin/bash

# ==========================================
# AI Bookmark Organizer - 自动化环境部署脚本
# 功能: 安装 Homebrew -> Ollama -> 模型 -> Python Venv -> 依赖库 -> 修正路径
# ==========================================

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 目标模型 (与 pipeline.py 保持一致)
TARGET_MODEL="qwen2.5:3b"

# 1. 检查并安装 Homebrew
echo -e "${CYAN}[1/6] 检查系统环境 (Homebrew)...${NC}"
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}未检测到 Homebrew，正在请求安装...${NC}"
    echo -e "${YELLOW}注意: 安装 Homebrew 可能需要管理员密码 (sudo)${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 配置 Homebrew 环境变量 (针对 Apple Silicon Mac)
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo -e "${GREEN}Homebrew 已安装。${NC}"
fi

# 2. 检查并安装 Ollama
echo -e "${CYAN}[2/6] 检查 AI 运行环境 (Ollama)...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}未检测到 Ollama，正在通过 Homebrew 安装...${NC}"
    brew install ollama
    
    # 启动 Ollama 服务
    echo -e "${YELLOW}正在启动 Ollama 服务...${NC}"
    brew services start ollama
    
    # 等待服务启动
    echo "等待 Ollama 服务就绪..."
    sleep 5
else
    echo -e "${GREEN}Ollama 已安装。${NC}"
fi

# 确保 Ollama 服务正在运行
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Ollama 服务未运行，正在尝试启动...${NC}"
    ollama serve &
    sleep 5
fi

# 3. 拉取 AI 模型
echo -e "${CYAN}[3/6] 检查 AI 模型 (${TARGET_MODEL})...${NC}"
if ollama list | grep -q "${TARGET_MODEL}"; then
    echo -e "${GREEN}模型 ${TARGET_MODEL} 已存在，跳过下载。${NC}"
else
    echo -e "${YELLOW}正在拉取模型 ${TARGET_MODEL} (这可能需要几分钟，取决于网速)...${NC}"
    ollama pull ${TARGET_MODEL}
fi

# 4. 设置项目工作目录
# 优先使用用户传入的参数，否则默认为 bookmarks-cleaner-session
WORK_DIR="${1:-bookmarks-cleaner-session}"
echo -e "${CYAN}[4/6] 配置工作目录: ${WORK_DIR}${NC}"

if [ ! -d "$WORK_DIR" ]; then
    mkdir -p "$WORK_DIR"
    echo -e "${GREEN}目录已创建。${NC}"
fi

# 检查当前目录下是否有核心代码，如果有则复制进去
if [ -f "pipeline.py" ]; then
    cp pipeline.py "$WORK_DIR/"
    echo -e "已将 pipeline.py 复制到工作目录。"
else
    echo -e "${RED}错误: 当前目录下找不到 pipeline.py，请确保脚本与代码在同一文件夹。${NC}"
    exit 1
fi

if [ -f "requirements.txt" ]; then
    cp requirements.txt "$WORK_DIR/"
else
    # 如果没有文件，自动生成
    echo -e "beautifulsoup4\nollama\ntqdm\nurllib3\ncurl_cffi" > "$WORK_DIR/requirements.txt"
    echo -e "已自动生成 requirements.txt。"
fi

# 进入工作目录
cd "$WORK_DIR" || exit

# 5. 路径修正 (关键步骤)
# 将 pipeline.py 中的硬编码绝对路径修改为相对路径，使脚本随处可用
echo -e "${CYAN}[5/6] 正在修正代码中的硬编码路径...${NC}"
# macOS 下 sed -i 需要一个空字符串作为备份扩展名
if grep -q "/Users/cyriusweng/0-Inbox/bookmarks" pipeline.py; then
    sed -i '' "s|BASE_DIR = '/Users/cyriusweng/0-Inbox/bookmarks'|BASE_DIR = os.path.dirname(os.path.abspath(__file__))|g" pipeline.py
    echo -e "${GREEN}路径修正成功！现在脚本将使用当前目录作为 BASE_DIR。${NC}"
else
    echo -e "${GREEN}代码路径似乎不需要修正或已被修改。${NC}"
fi

# 6. 配置 Python 虚拟环境
echo -e "${CYAN}[6/6] 配置 Python 虚拟环境 (venv)...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境已创建。${NC}"
fi

# 激活环境并安装依赖
echo -e "${YELLOW}正在激活环境并安装依赖 (这可能需要一点时间)...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${CYAN}==========================================${NC}"
echo -e "${GREEN}🎉 部署完成！一切就绪。${NC}"
echo -e "${CYAN}==========================================${NC}"
echo -e "请按以下步骤运行程序："
echo -e "1. 进入目录:  ${YELLOW}cd ${WORK_DIR}${NC}"
echo -e "2. 激活环境:  ${YELLOW}source venv/bin/activate${NC}"
echo -e "3. 放入书签:  ${YELLOW}将你的 bookmarks.html 放入该文件夹${NC}"
echo -e "4. 运行脚本:  ${YELLOW}python pipeline.py --step 1${NC}"
echo -e ""
