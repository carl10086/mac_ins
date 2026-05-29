# Project: mac_ins

> macOS 终端环境配置备忘 — 重装或换机时快速恢复开发环境

## 用途

个人 macOS 环境恢复指南，记录从零配置终端开发环境的步骤。

## 关键文件

| 文件 | 说明 |
|------|------|
| `mac_ins.md` | 主文档，包含完整配置步骤（Homebrew → Oh My Zsh → 插件 → 工具） |
| `mac_ins.html` | `mac_ins.md` 的 HTML 导出版本 |
| `refer/` | 参考资料目录（已加入 .gitignore，不同步） |
| `z-f-cheatsheet.md` | 可能是 z/fzf 相关快捷键速查 |

## 项目约定

- **不需要 README.md** — 主文档直接用 `mac_ins.md`
- `refer/` 目录不上传 — 已加入 `.gitignore`
- 分支策略：直接提交到 `main`，不需要额外分支
- 提交信息使用中文描述

## 技术栈记录

- macOS 15.x (Darwin 25.5.0, Apple Silicon)
- Shell: zsh 5.9
- 终端: Ghostty
- 代理: `http://localhost:7890`
- Homebrew, Oh My Zsh, zsh-autosuggestions, zsh-syntax-highlighting

## Boundaries

- 不要删除 `refer/` 目录
- 不要创建 README.md
- 文档更新时，同步导出 HTML 版本到 `mac_ins.html`
