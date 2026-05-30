# Bat 安装与配置

> `bat` — `cat` 的替代品，支持语法高亮、Git 集成、自动分页

## 安装

```bash
brew install bat
```

## 为什么感觉"自带分页"

bat 本身**不内嵌分页器**，但它会自动调用系统的 `less`（macOS 自带 `/usr/bin/less`）。所以安装后直接使用，超出屏幕的内容会自动分页，体验上就是"开箱即用"。

如果输出能 fit 在一屏内，bat 会自动退出不分页；超出时才会进入分页模式。

## 基础用法

```bash
# 替代 cat，带语法高亮
bat file.py

# 查看多个文件（带文件名标题）
bat file1.js file2.js

# 只查看指定行范围
bat --line-range 10:20 file.log

# 显示不可见字符
bat -A file.txt

# 禁用分页直接输出（适合管道）
bat --paging=never file.txt | grep "error"
```

## 常用配置

### 1. 添加到 ~/.zshrc

```bash
# 替代 cat（保留原 cat 可用）
alias cat='bat --paging=never'

# 或者保留分页，只看 bat
alias b='bat'

# 自定义分页器参数（可选，bat 默认已经很好）
export BAT_PAGER="less -RF"

# 禁用分页（管道场景有用）
# export BAT_PAGER=""
```

### 2. 配置文件

```bash
# 创建配置目录
mkdir -p ~/.config/bat

# bat 配置文件位置：~/.config/bat/config
# 示例内容：
--style="numbers,changes,header"
--theme="TwoDark"
```

### 3. 与 fzf 集成（预览文件内容）

```bash
# 在 fzf 中用 bat 预览文件
fzf --preview 'bat --color=always --style=numbers --line-range=:500 {}'
```

### 4. 替代 man 的分页器

```bash
# 让 man 页面也有语法高亮
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
```

## 主题与语言

```bash
# 查看所有主题
bat --list-themes

# 指定主题
bat --theme=GitHub file.py

# 查看支持的语言
bat --list-languages

# 强制指定语言（无后缀或识别错误时）
bat -l yaml config.txt
```

## 注意事项

- bat 的默认行为是**分页**（通过系统 less），管道传输时会自动禁用
- 用 `--paging=never` 或 `BAT_PAGER=""` 可永久禁用分页
- 主题需要终端支持真彩色（Ghostty、iTerm2、Alacritty 都支持）
