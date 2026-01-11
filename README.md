<div align="center">

# 🔖 Local AI Bookmark Organizer

**Turn your chaotic bookmark mess into a structured knowledge base using Local LLMs.**

[🇺🇸 English Version](#english) | [🇨🇳 中文文档](#chinese)

</div>

---

<span id="english"></span>

## 🇺🇸 English Version

### 📖 Introduction

**Local AI Bookmark Organizer** is a privacy-first, automated pipeline that cleans, enriches, and reorganizes your browser bookmarks. Unlike cloud-based services, this tool runs entirely on your machine using **Ollama**, ensuring your browsing data never leaves your computer.

It solves three problems:
1.  **Link Rot:** Detects and removes dead links (including "Soft 404s").
2.  **Lack of Context:** Crawls websites to fetch titles and descriptions.
3.  **Disorganization:** Uses AI to generate a **Dynamic Taxonomy** based on your specific content, rather than generic presets.

### ✨ Key Features

* **🌳 Dynamic Taxonomy:** The AI reads your collection first, then invents a classification tree (Category > Subcategory) that fits *your* specific interests.
* **🕵️‍♂️ Anti-Fingerprinting:** Uses `curl_cffi` to simulate real browser TLS fingerprints, accessing sites that normally block Python scripts.
* **⏯️ Resumable Pipeline:** The long-running steps (Step 2, 3, and 4) support **checkpoints**. If the script stops, simply run it again—it will resume exactly where it left off.
* **⚡ Auto-Setup (macOS):** Includes a one-click script to install dependencies, Homebrew, and models.

### ⚙️ Model Recommendations

The default model is `qwen2.5:3b` (balanced for speed/quality). You can change `MODEL_NAME` in `pipeline.py` based on your hardware.

| RAM / VRAM | Recommended Model | Why? |
| :--- | :--- | :--- |
| **8GB (Entry)** | `qwen2.5:3b` | Fast, low memory usage, decent logic. (Default) |
| **16GB (Mid)** | `dolphin-mistral` | **Highly Recommended.** "Uncensored" model that won't refuse to categorize NSFW/Controversial bookmarks. |
| **16GB (Alt)** | `llama3` | Strong logic, but might be "preachy" about certain links. |
| **32GB+ (Pro)** | `mixtral` / `yi:34b` | Superior taxonomy generation, but slower. |

> **Tip:** We recommend **Uncensored Models** (like Dolphin series) because safety-aligned models often refuse to categorize bookmarks related to sensitive topics, gambling, or adult content.

### ⚠️ Limitations

* **Scraping Accuracy:** While we use anti-fingerprinting, some sites may still return CAPTCHAs or "Verify Human" pages. This can mislead the AI. **Pull Requests to improve the crawler are welcome!**
* **Processing Time:** To avoid IP bans, the crawler sleeps between requests. Processing 1,000 links might take 30-60 minutes.

### 🚀 Quick Start (macOS Optimized)

> **Note for Windows/Linux Users:** The core Python code works on any OS, but the `setup.sh` automation script is optimized for macOS. You may need to install Ollama and Python dependencies manually.

1.  **Clone/Download** this repository.
2.  **Place your bookmarks file** (exported from Chrome/Edge/Vivaldi) into the folder and rename it to `bookmarks.html`.
3.  **Run the setup script:**

```bash
chmod +x setup.sh
./setup.sh
```

4.  The script will create a working directory. Enter it:

```bash
cd bookmarks-cleaner-session
source venv/bin/activate
```

### 🛠️ Usage Pipeline

Run these steps sequentially:

#### Step 1: Ingestion
Parses HTML into JSON.
```bash
python pipeline.py --step 1
```

#### Step 2: Enrichment (Resumable)
Crawls metadata. Handles timeouts and "Soft 404s".
```bash
python pipeline.py --step 2
```

#### Step 3: Analysis (Resumable)
Generates micro-tags using Local LLM.
```bash
python pipeline.py --step 3
```

#### Step 3.5: Taxonomy Generation
The AI builds a custom classification tree based on tags from Step 3.
```bash
python pipeline.py --step 35
```

#### Step 4: Categorization (Resumable)
Assigns bookmarks to the generated categories.
```bash
python pipeline.py --step 4
```

#### Step 5: Export
Generates a `final_bookmarks.html` compatible with all major browsers.
```bash
python pipeline.py --step 5
```

---

<span id="chinese"></span>

## 🇨🇳 中文文档

### 📖 项目简介

**Local AI Bookmark Organizer** 是一个基于本地大语言模型（Local LLM）的智能书签治理工具。

与传统工具不同，本项目**完全本地运行**（基于 Ollama），致力于解决死链清理、信息缺失和分类混乱三大痛点。

### ✨ 核心功能

* **🌳 动态分类体系 (杀手级功能):** AI 拒绝使用预设分类。它会先“阅读”你所有的书签，然后**量身定制**一套最契合你个人兴趣领域的分类树。
* **🕵️‍♂️ 抗指纹爬虫:** 集成 `curl_cffi`，模拟真实浏览器 TLS 指纹，有效绕过常见的 Cloudflare 拦截。
* **⏯️ 断点续传:** 最耗时的步骤（Step 2 爬取、Step 3 打标、Step 4 归类）均支持进度保存。随时中断，随时继续。
* **⚡ macOS 一键部署:** 提供自动化脚本，自动解决环境依赖。

### ⚙️ 模型推荐与硬件配置

默认配置为 `qwen2.5:3b`，您可以在 `pipeline.py` 中修改 `MODEL_NAME`。

| 内存 / 显存 | 推荐模型 | 理由 |
| :--- | :--- | :--- |
| **8GB (入门)** | `qwen2.5:3b` | 速度快，显存占用低，逻辑足够处理分类任务。（默认） |
| **16GB (主流)** | `dolphin-mistral` | **强烈推荐。** 这是一个 "Uncensored" (无审查) 模型，不会因为书签包含敏感内容（如成人、政治等）而拒绝分类。 |
| **16GB (备选)** | `llama3` | 逻辑能力强，但“道德包袱”较重，可能会拒绝处理某些链接。 |
| **32GB+ (高性能)** | `mixtral` / `yi:34b` | 构建的分类体系更宏观、更精准，但推理速度较慢。 |

> **提示:** 强烈建议使用 **无审查 (Uncensored) 模型**（如 Dolphin 系列）。因为书签库中常包含各种各样的内容，经过安全对齐的模型往往会拒绝处理它们，导致分类失败。

### ⚠️ 局限性

* **爬虫准确性:** 尽管有抗指纹技术，部分网站仍可能返回验证码页面，导致 AI 获取到错误的上下文。**欢迎 Fork 并提交 PR 优化爬虫逻辑！**
* **时间成本:** 为了防止 IP 被封，爬虫在请求之间有强制休眠。处理 1000 个书签通常需要 30-60 分钟。

### 🚀 快速开始 (macOS 优先)

> **Windows/Linux 用户注意:** 核心 Python 代码 (`pipeline.py`) 支持所有系统，但自动化部署脚本 `setup.sh` 针对 macOS 优化。非 Mac 用户需手动安装 Ollama 和依赖库。

1.  **下载** 本仓库。
2.  **准备书签:** 导出书签重命名为 `bookmarks.html`，放入根目录。
3.  **运行部署脚本:**

```bash
chmod +x setup.sh
./setup.sh
```

4.  进入生成的目录并激活环境:

```bash
cd bookmarks-cleaner-session
source venv/bin/activate
```

### 🛠️ 使用指南

请按顺序执行以下步骤：

#### Step 1: 摄入 (Ingestion)
解析 HTML 为 JSON。
```bash
python pipeline.py --step 1
```

#### Step 2: 浓缩 (Enrichment) - *支持断点续传*
访问链接获取标题和描述，自动标记死链。
```bash
python pipeline.py --step 2
```

#### Step 3: 透视 (Analysis) - *支持断点续传*
AI 生成微标签 (Micro-Tags)。
```bash
python pipeline.py --step 3
```

#### Step 3.5: 构建体系 (Taxonomy Gen)
**（核心）** AI 宏观分析所有标签，生成专属分类树。
```bash
python pipeline.py --step 35
```

#### Step 4: 归类 (Categorization) - *支持断点续传*
将书签归入生成的分类体系。
```bash
python pipeline.py --step 4
```

#### Step 5: 建造 (Export)
生成兼容所有浏览器的 `final_bookmarks.html`。
```bash
python pipeline.py --step 5
```

---

### 🧰 辅助工具

**快速体检脚本 (`bookmark_cleaner.sh`)**
如果只想快速生成死链报告（CSV），无需 AI 重组，可直接运行：
```bash
./bookmark_cleaner.sh bookmarks.html
```

---
