#!/bin/bash

# 1. 安装 PyInstaller (如果未安装)
pip install pyinstaller

# 2. 清理旧构建
rm -rf build dist *.spec

# 3. 执行打包
# --windowed: 无控制台窗口
# --add-data: 打包资源文件
# --icon: 应用图标
# --name: 应用名称
# --clean: 清理缓存
pyinstaller --noconfirm --onedir --windowed --clean \
    --name "down-video-load" \
    --add-data "resource:resource" \
    --icon "resource/assets/logo.png" \
    --hidden-import "faster_whisper" \
    main.py

echo "打包完成！应用位于 dist/down-video-load.app"

# 4. 可选：创建 DMG (如果安装了 create-dmg)
if command -v create-dmg &> /dev/null; then
    echo "正在创建 DMG..."
    create-dmg \
      --volname "down-video-load Installer" \
      --volicon "resource/assets/logo.png" \
      --window-pos 200 120 \
      --window-size 800 400 \
      --icon-size 100 \
      --icon "down-video-load.app" 200 190 \
      --hide-extension "down-video-load.app" \
      --app-drop-link 600 185 \
      "dist/down-video-load.dmg" \
      "dist/down-video-load.app"
    echo "DMG 创建完成！位于 dist/down-video-load.dmg"
else
    echo "提示: 未检测到 create-dmg 工具，仅生成了 .app 应用包。"
    echo "你可以通过 'brew install create-dmg' 安装它，然后再次运行此脚本生成 DMG。"
fi
