#!/bin/bash
# CSSwitch macOS 打包脚本
set -e

echo "=== CSSwitch macOS Build ==="

# 检查依赖
command -v cargo >/dev/null 2>&1 || { echo "错误：需要 Rust（安装: https://rustup.rs）"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "错误：需要 Node.js"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "错误：需要 npm"; exit 1; }

# 安装 Tauri CLI
echo "安装 Tauri CLI..."
cargo install tauri-cli 2>/dev/null || true

# 安装 npm 依赖
echo "安装 npm 依赖..."
cd "$(dirname "$0")/../desktop"
npm install

# 构建 macOS 通用版本
echo "构建 macOS Universal 版本..."
cargo tauri build --target universal-apple-darwin

echo ""
echo "=== 构建完成 ==="
echo "产物目录: src-tauri/target/universal-apple-darwin/release/bundle/"
echo "  - DMG: bundle/dmg/"
echo "  - app: bundle/macos/"
