#!/usr/bin/env python3
"""
Claude Code Hook: 自动截断空 signature，预防 400 错误
用于 UserPromptSubmit 事件
"""
import json
import sys
import os
import io
import shutil
from datetime import datetime
from pathlib import Path

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
input_data = json.load(sys.stdin)

session_id = input_data.get("session_id")
cwd = input_data.get("cwd")


def convert_path(original_path):
    """转换路径格式，匹配 Claude Code 的行为"""
    if sys.platform == "win32":
        path = original_path.replace(":\\", "--").replace("\\", "-").replace("/", "-")
    else:
        path = original_path.replace("/", "-")
    # 下划线替换为 -
    path = path.replace("_", "-")
    # 非 ASCII 字符替换为 -
    return ''.join(c if ord(c) < 128 else '-' for c in path)


def has_empty_signature(obj):
    """递归检测空 signature"""
    if isinstance(obj, dict):
        if obj.get("signature") == "":
            return True
        for value in obj.values():
            if has_empty_signature(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if has_empty_signature(item):
                return True
    return False


def find_empty_signature_line(filepath):
    """找到第一个空 signature 的行号"""
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                if has_empty_signature(json.loads(line)):
                    return line_num
            except json.JSONDecodeError:
                continue
    return None


def truncate_file(filepath, line_num):
    """截断文件并备份"""
    backup_path = str(filepath) + ".bak"
    shutil.copy2(filepath, backup_path)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines[:line_num - 1])
    return backup_path


if session_id and cwd:
    claude_base = Path.home() / ".claude" / "projects"
    project_dir = convert_path(cwd)
    jsonl_file = claude_base / project_dir / f"{session_id}.jsonl"

    if jsonl_file.exists():
        empty_line = find_empty_signature_line(jsonl_file)
        if empty_line:
            backup = truncate_file(jsonl_file, empty_line)
            log_file = claude_base / "truncate_log.txt"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {session_id} | line {empty_line} | {backup}\n")

sys.exit(0)
