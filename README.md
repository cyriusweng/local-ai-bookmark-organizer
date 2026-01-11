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
1.  **Link Rot:** Detects and removes dead links (including "Soft 404s" and domain parking pages).
2.  **Lack of Context:** Crawls websites to fetch titles, keywords, and descriptions.
3.  **Disorganization:** Uses AI to generate a **Dynamic Taxonomy** based on your specific content, then categorizes every link automatically.

### ✨ Key Features

* **🔒 Privacy First:** Powered by local LLMs (Llama 3, Qwen 2.5) via Ollama. No data upload.
* **🕵️‍♂️ Anti-Fingerprinting:** Uses `curl_cffi` to simulate real browser TLS fingerprints, bypassing basic anti-bot protections (403/406 errors).
* **🌳 Dynamic Taxonomy:** The AI analyzes your tags to build a custom classification tree (Category > Subcategory) tailored to *your* interests, rather than forcing preset categories.
* **🛡️ Data Integrity:** Step-by-step pipeline with autosave. No bookmark is left behind.
* **⚡ Auto-Setup:** Includes a one-click script to install dependencies, homebrew, and models.

### 🚀 Quick Start (Automated)

We provide a `setup.sh` script that handles everything: installing Homebrew, Ollama, pulling the AI model, creating a Python virtual environment, and fixing file paths.

1.  **Clone/Download** this repository.
2.  **Place your bookmarks file** (exported from Chrome/Edge/Vivaldi) into the folder and rename it to `bookmarks.html`.
3.  **Run the setup script:**

```bash
chmod +x setup.sh
./setup.sh
```

4.  The script will create a working directory (default: `bookmarks-cleaner-session`). Enter it:

```bash
cd bookmarks-cleaner-session
source venv/bin/activate
```

### 🛠️ Usage Pipeline

The processing is divided into **5 steps** to ensure stability. Run them sequentially:

#### Step 1: Ingestion
Parses your HTML file into a raw JSON format.
```bash
python pipeline.py --step 1
```

#### Step 2: Enrichment (The Crawler)
Visits every link to check availability and fetch metadata (Title, Description, Keywords). Handles timeouts and "Soft 404s".
```bash
python pipeline.py --step 2
```

#### Step 3: Analysis (Tagging)
Uses the Local LLM to analyze the metadata and assign micro-tags to each bookmark.
```bash
python pipeline.py --step 3
```

#### Step 3.5: Taxonomy Generation (The Brain)
The AI looks at all generated tags and builds a hierarchical classification tree (JSON) specifically for you.
```bash
python pipeline.py --step 35
```

#### Step 4: Categorization
Assigns every bookmark to a `Category > Subcategory` based on the tree generated in Step 3.5.
```bash
python pipeline.py --step 4
```

#### Step 5: Export
Generates a `final_bookmarks.html` file strictly compatible with Netscape Bookmark standards (importable to Vivaldi, Chrome, Firefox, etc.).
```bash
python pipeline.py --step 5
```

---

### 🧰 Utilities

#### Quick Audit Tool (`bookmark_cleaner.sh`)
If you don't want to reorganize everything and just want a quick report on dead links, run the shell script:

```bash
./bookmark_cleaner.sh bookmarks.html
```
It generates a CSV report showing HTTP Status Codes and recommendations (Keep/Delete).

---

### ⚠️ Disclaimer
This tool involves web scraping. While it uses anti-fingerprinting techniques, aggressive scraping may lead to temporary IP bans from certain websites. Use with caution.

---
<br>

<span id="chinese"></span>

## 🇨🇳 中文文档

### 📖 项目简介

**Local AI Bookmark Organizer** 是一个基于本地大语言模型（Local LLM）的智能书签治理工具。它致力于将杂乱无章的浏览器书签转化为结构清晰的知识库。

与传统的书签工具不同，本项目**完全本地运行**（基于 Ollama），确保您的浏览隐私数据绝对安全，不会上传至任何云端服务器。

它主要解决以下痛点：
1.  **死链清理：** 自动检测并标记 404、DNS 错误以及“软 404”（域名过期页）。
2.  **信息缺失：** 自动爬取网页标题、描述和关键词，补充上下文。
3.  **分类混乱：** AI 不会使用预设分类，而是根据您的书签内容，**动态生成**最适合您的分类树，并自动归类。

### ✨ 核心功能

* **🔒 隐私优先：** 依赖 Ollama 本地运行 (支持 Llama 3, Qwen 2.5 等)，数据不出本机。
* **🕵️‍♂️ 抗指纹爬虫：** 集成 `curl_cffi`，模拟真实浏览器 TLS 指纹，有效绕过常见的反爬虫拦截 (403/406)。
* **🌳 动态分类体系：** AI 会先“阅读”你所有的书签，然后为您量身定制一套分类层级（Category > Subcategory）。
* **🛡️ 鲁棒性设计：** 分步流水线设计，支持断点续传。
* **⚡ 一键部署：** 提供自动化脚本，自动解决环境依赖。

### 🚀 快速开始

我们提供了一个 `setup.sh` 脚本，可自动完成环境配置（检测/安装 Homebrew、Ollama、拉取模型、创建 Python 虚拟环境、修正路径）。

1.  **下载/Clone** 本仓库。
2.  **准备书签：** 从浏览器导出书签，重命名为 `bookmarks.html`，放入项目根目录。
3.  **运行部署脚本：**

```bash
chmod +x setup.sh
./setup.sh
```

4.  脚本执行完毕后，会创建一个工作目录（默认为 `bookmarks-cleaner-session`）。进入该目录并激活环境：

```bash
cd bookmarks-cleaner-session
source venv/bin/activate
```

### 🛠️ 使用指南

处理流程被拆分为 **5 个步骤**，请按顺序执行：

#### Step 1: 摄入 (Ingestion)
将 HTML 书签解析为标准化的 JSON 格式。
```bash
python pipeline.py --step 1
```

#### Step 2: 浓缩 (Enrichment)
通过抗指纹浏览器模拟器访问每个链接，获取 HTTP 状态码、网页标题和 SEO 描述。自动识别死链。
```bash
python pipeline.py --step 2
```

#### Step 3: 透视 (Analysis)
调用本地 AI 模型，根据网页元数据为每个书签打上 Micro-Tags（微标签）。
```bash
python pipeline.py --step 3
```

#### Step 3.5: 构建体系 (Taxonomy Gen)
**（核心亮点）** AI 宏观分析所有标签，生成一棵 MECE（完全穷尽且互斥）的分类树。
```bash
python pipeline.py --step 35
```

#### Step 4: 归类 (Categorization)
依据上一步生成的分类树，将每个书签精确归类到 `主分类 > 子分类` 中。
```bash
python pipeline.py --step 4
```

#### Step 5: 建造 (Export)
生成完全兼容 Netscape 标准的 `final_bookmarks.html`，可直接导入 Vivaldi、Chrome、Edge 等浏览器。
```bash
python pipeline.py --step 5
```

---

### 🧰 辅助工具

#### 快速体检脚本 (`bookmark_cleaner.sh`)
如果您不想进行 AI 重组，只想快速检查有哪些死链，可以使用这个 Shell 脚本：

```bash
./bookmark_cleaner.sh bookmarks.html
```
它会生成一份 CSV 报告，列出所有链接的状态码和处理建议（保留/删除）。

---

### ⚠️ 免责声明
本项目包含网页爬虫功能。尽管使用了抗指纹技术，但短时间内高频访问可能会导致您的 IP 被部分网站暂时封禁，请按需调整代码中的延迟参数。
