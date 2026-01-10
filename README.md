# cc_hooks



---
手动图文教程：[/ClaudeCode-400-2e3cf3ac3f988079b79ccceaed4fe8da?source=copy_link](https://dolomite-scorpion-4cb.notion.site/ClaudeCode-400-2e3cf3ac3f988079b79ccceaed4fe8da?source=copy_link)

Claude Code Hook 脚本，用于处理400 错误（Invalid signature in thinking block）。

## 原理

每次发送消息时自动检测对话历史文件（JSONL）中的空 `signature` 字段，发现则截断文件。

## 安装

将以下配置添加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python C:\\Users\\Administrator\\.claude\\truncate_signature.py"
          }
        ]
      }
    ]
  }
}
```

## 文件说明

- `truncate_signature.py` - 主脚本，检测并截断空 signature
- 日志位置：`~/.claude/projects/truncate_log.txt`
- 备份位置：原 JSONL 文件同目录，后缀 `.bak`

## Hook 可获取的信息

| 字段 | 说明 |
|------|------|
| `session_id` | 会话 ID |
| `cwd` | 工作目录 |
| `prompt` | 用户消息内容 |
| `permission_mode` | 权限模式 |
| `transcript_path` | 对话历史文件路径 |
