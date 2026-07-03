# CSswitch 自定义第三方API支持与多平台打包计划

## 项目概述
基于 SuperJJ007/CSswitch 仓库，添加自定义第三方 ANTHROPIC API / OPENAI API 支持，
参考 9router 的格式转换逻辑，最终打包 macOS 和 Linux 版本，提交到 Tippye/CSswitch 仓库。

## 阶段划分

### Stage 1: 代码克隆与分析
- 克隆 CSswitch 和 9router 仓库
- 深入分析 proxy/csswitch_proxy.py 的 provider 注册表架构
- 分析 9router 的 providerNormalization.js 和 API转换逻辑
- 分析 desktop GUI 代码，了解 provider 配置UI

### Stage 2: 核心开发 - 添加自定义Provider支持
- 在 csswitch_proxy.py 中添加 `custom_anthropic` 和 `custom_openai` provider
- 实现 Anthropic ↔ OpenAI API 格式转换（参考9router）
- 添加自定义API endpoint、模型名、API key 配置支持
- 更新 qwen_proxy.py 中的翻译逻辑复用

### Stage 3: GUI 更新
- 更新 desktop/src 前端代码，支持自定义 provider URL 输入
- 更新 src-tauri/src/config.rs 配置结构
- 更新 src-tauri/src/lib.rs 后端命令

### Stage 4: 打包构建
- 构建 macOS app（Tauri 原生支持）
- 构建 Linux 版本（Tauri AppImage/deb）
- 验证打包产物

### Stage 5: 文档更新与提交
- 更新 README.md（使用说明、自定义API配置说明）
- 提交到 git@github.com:Tippye/CSswitch.git

## 技能加载
- Stage 2-3: vibecoding-general-swarm
- Stage 4: vibecoding-general-swarm (打包脚本)
