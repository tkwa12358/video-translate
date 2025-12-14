<div align="center">
  <h1>down-video-load</h1>
  <p>一款基于大语言模型(LLM)的视频下载与字幕处理工具，支持视频下载、语音识别、字幕智能断句与翻译</p>

简体中文 / [正體中文](./legacy-docs/README_TW.md) / [English](./legacy-docs/README_EN.md) / [日本語](./legacy-docs/README_JA.md)

📚 **[在线文档](https://github.com/tkwa12358/video-translate)** | 🚀 **[快速开始](https://github.com/tkwa12358/video-translate)** | ⚙️ **[配置指南](https://github.com/tkwa12358/video-translate)**

</div>

## 项目介绍

**down-video-load** 是一款专注于视频下载与本地离线处理的工具。它能够：

- **下载高清视频**：支持 YouTube、Bilibili 等多平台视频下载，最高支持 4K 分辨率。
- **本地语音识别**：内置 **Faster-Whisper** 引擎（默认 Large-v2 模型），无需联网即可生成高精度字幕。
- **智能字幕处理**：利用大语言模型进行字幕断句、校正与翻译，支持中英双语输出。
- **完全本地化**：支持设置代理，保护隐私，所有处理流程均可本地完成（除 LLM API 调用外）。

### 核心特性

- **强制代理下载**：确保网络环境稳定，避免下载失败。
- **清晰度选择**：360p 至 4K 分辨率自由选择。
- **官方字幕优先**：自动抓取视频自带的官方字幕，无官方字幕时才进行转录。
- **极简模型管理**：专注于 Large-v2 模型，拒绝选择困难症。

## 快速开始

### Windows / macOS 用户

1.从 [Release](../../releases) 页面下载最新版本的安装包。
2. 安装并运行程序。
3. **首次启动**：程序会自动检查并提示下载 `Faster-Whisper Large-v2` 模型（约 3GB）。
4. **视频下载**：在设置中配置好代理（如需），粘贴视频链接即可开始下载。
5. **字幕处理**：视频下载完成后，会自动进行转录与翻译处理。

### 源码运行

1. 克隆项目
```bash
git clone https://github.com/tkwa12358/video-translate.git
cd video-translate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行
```bash
python main.py
```

## 配置说明

### 视频下载配置
- **代理设置**：在设置中开启“强制代理检查”，确保能访问国际互联网。
- **Cookies**：如下载受限（如高画质限制），可在设置中开启 Cookie 并放置 `cookies.txt`。

### LLM 配置
支持 OpenAI 兼容接口，推荐使用 DeepSeek 或 SiliconFlow 等高性价比服务。

## 目录结构

```
down-video-load/
├── resource/                   # 资源文件
├── AppData/                    # 应用数据（日志、缓存、模型）
│   ├── models/                 # Faster-Whisper 模型路径
│   ├── downloads/              # 视频下载目录
│   └── settings.json           # 配置文件
└── main.py                     # 主程序
```

## 贡献

欢迎提交 Issue 和 Pull Request 帮助改进项目。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tkwa12358/video-translate&type=Date)](https://star-history.com/#tkwa12358/video-translate&Date)
