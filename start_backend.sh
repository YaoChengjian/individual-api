#!/bin/zsh

set -e

cd "$(dirname "$0")"

# 强制使用 arm64 解释器启动，避免 Rosetta/x86_64 终端下加载 arm64 二进制扩展时报错。
exec arch -arm64 ./venv/bin/python run.py
