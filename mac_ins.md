# Mac 终端环境配置备忘

> 记录时间：2026-05-29  
> 系统：macOS 15.x (Darwin 25.5.0, Apple Silicon)  
> 用途：重装或换机时快速恢复终端开发环境

---

## 环境信息

| 项目 | 版本 / 值 |
|------|----------|
| macOS | 15.x (Sequoia) |
| Shell | zsh 5.9 |
| 终端 | Ghostty |
| 代理 | `http://localhost:7890`（下载 GitHub 资源时使用） |

---

## 1. 安装 Homebrew（如未安装）

```bash
export ALL_PROXY=http://localhost:7890
/bin/bash -c "$(curl -fsSL -x http://localhost:7890 https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> **注意**：安装完成后，Homebrew 会提示将初始化命令写入 `~/.zprofile`。但 macOS 上很多终端默认不会加载 `.zprofile`，因此**必须在 `~/.zshrc` 开头也加上 Homebrew 的 PATH 初始化**，否则后续安装的命令（如 `zoxide`、`fzf`）会找不到。

## 2. 安装 Oh My Zsh

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

安装完成后备份原配置：

```bash
# 安装脚本会自动备份 ~/.zshrc 到 ~/.zshrc.pre-oh-my-zsh
```

---

## 2. 安装插件

```bash
# 命令自动建议（灰色提示文字）
git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# 语法高亮（绿色 = 合法命令，红色 = 非法）
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

内置插件无需安装，直接在 `~/.zshrc` 的 `plugins` 中启用：
- `git` — Git 别名和补全
- `sudo` — 按 ESC 两次自动加 sudo
- `extract` — `x <file>` 解压任意格式
- `history` — 历史命令快捷操作

---

## 3. 安装 Starship

```bash
curl -sS https://starship.rs/install.sh | sh -s -- -y -b ~/.local/bin
```

确保 `~/.local/bin` 在 PATH 中（见 `~/.zshrc` 配置）。

---

## 4. 安装 Nerd Font

下载并安装 JetBrainsMono Nerd Font（终端图标支持）：

```bash
mkdir -p ~/Library/Fonts
cd /tmp
curl -x http://localhost:7890 -sL \
  "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/JetBrainsMono.tar.xz" \
  -o JetBrainsMono.tar.xz
tar -xJf JetBrainsMono.tar.xz -C ~/Library/Fonts/
```

> **注意**：终端必须使用 Nerd Font 的 **Mono** 变体（等宽），否则图标错位。

---

## 5. 写入配置文件

### 5.1 `~/.zshrc`

```zsh
# 必须先初始化 Homebrew，否则后续安装的命令找不到
#（macOS 终端默认不加载 ~/.zprofile，所以这里必须加）
eval "$(/opt/homebrew/bin/brew shellenv zsh)"

# PATH
export PATH="$HOME/.local/bin:$PATH"

# Oh My Zsh
export ZSH="$HOME/.oh-my-zsh"

# 禁用内置主题，由 Starship 接管提示符
ZSH_THEME=""

# 插件
plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
  sudo
  extract
  history
)

source $ZSH/oh-my-zsh.sh

# 别名
alias zshconfig="code ~/.zshrc"
alias ohmyzsh="code ~/.oh-my-zsh"
alias ll="ls -la"
alias ..="cd .."
alias ...="cd ../.."

# NVM（如已安装）
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# SDKMAN!（Java 版本管理）
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

# Starship
eval "$(starship init zsh)"

# zoxide：智能目录跳转
# ⚠️ 不要加 --cmd cd！默认会创建 z 和 zi 命令
# 如果加了 --cmd cd，zoxide 只会接管 cd，不会创建 z
eval "$(zoxide init zsh)"

# fzf：模糊查找
source <(fzf --zsh)
```

### 5.2 `~/.config/starship.toml`

```toml
# Starship 配置 - Catppuccin Mocha 配色

format = """
$directory$git_branch$git_status$nodejs$rust$golang$python
$character"""

[character]
success_symbol = "[➜](#a6e3a1)"
error_symbol = "[✗](#f38ba8)"
vicmd_symbol = "[❮](#a6e3a1)"

[directory]
truncation_length = 3
truncation_symbol = "…/"
style = "bold #89b4fa"

[git_branch]
symbol = " "
style = "bold #cba6f7"
format = '[$symbol$branch]($style) '

[git_status]
style = "bold #fab387"
format = '([$all_status$ahead_behind]($style) )'

[nodejs]
symbol = " "
style = "#a6e3a1"
format = '[$symbol($version)]($style) '

[rust]
symbol = " "
style = "bold #f38ba8"
format = '[$symbol($version)]($style) '

[python]
symbol = " "
style = "#f9e2af"
format = '[$symbol($version)]($style) '

[golang]
symbol = " "
style = "#94e2d5"
format = '[$symbol($version)]($style) '

[cmd_duration]
min_time = 2000
format = '[$duration](bold #f9e2af) '

[username]
style_user = "bold #89b4fa"
style_root = "bold #f38ba8"
format = "[$user]($style) "
disabled = true
show_always = false

[hostname]
ssh_only = true
format = "[@$hostname](bold #f9e2af) "
disabled = false
```

### 5.3 `~/.config/ghostty/config`

```ini
# Ghostty 配置

# 主题
theme = catppuccin-mocha

# 字体（Mono 变体）
font-family = "JetBrainsMono Nerd Font Mono"
font-size = 14

# 窗口
window-padding-x = 8
window-padding-y = 8
background-opacity = 0.95

# 光标
cursor-style = block
cursor-color = #f5e0dc
cursor-text = #1e1e2e

# 其他
mouse-hide-while-typing = true
confirm-close-surface = false
```

---

## 6. 安装 zoxide 和 fzf（可选但强烈推荐）

```bash
brew install zoxide fzf
```

在 `~/.zshrc` 中添加初始化（放在 Starship 之后）：

```zsh
# zoxide：智能目录跳转
# ⚠️ 默认参数会创建 z / zi 命令
# 如果加 --cmd cd，zoxide 只会接管 cd，不会创建 z
eval "$(zoxide init zsh)"

# fzf：模糊查找 + 快捷键
source <(fzf --zsh)
```

### zoxide 用法

| 命令 | 作用 |
|------|------|
| `z proj` | 跳转到历史中最匹配的 `*proj*` 目录 |
| `zi proj` | 交互式选择（多个匹配时弹出 fzf 列表） |
| `zq proj` | 只查询会跳到哪，不实际跳转 |
| `z -` | 返回上一个目录 |
| `zoxide query -l` | 列出所有已记录的目录 |

### fzf 快捷键

| 快捷键 | 作用 |
|--------|------|
| `Ctrl + R` | 模糊搜索历史命令 |
| `Ctrl + T` | 模糊搜索文件 |
| `Alt + C` | 模糊搜索目录并进入 |

---

## 7. 安装 SDKMAN!（Java 版本管理）

macOS 自带 Bash 3.2，但 SDKMAN! 安装脚本要求 Bash 4+。使用 zsh 执行可跳过该检查：

```bash
export https_proxy=http://localhost:7890
curl -s "https://get.sdkman.io" | zsh
```

安装完成后，SDKMAN! 会自动将初始化代码追加到 `~/.zshrc`（见 5.1 节配置）。

### 安装 Java（最新 LTS）

```bash
# 安装默认推荐版本（当前为 Java 25 LTS）
sdk install java

# 或指定版本
sdk install java 25.0.3-tem
```

> **注意**：`sdk install java` 不带版本号时，SDKMAN! 会自动选择当前默认的 LTS 版本。由于 SDKMAN! 管理 `JAVA_HOME`，**不要在 `~/.zshrc` 中手动设置 `JAVA_HOME`**，否则版本切换会失效。

### 常用命令

| 命令 | 作用 |
|------|------|
| `sdk current java` | 查看当前 Java 版本 |
| `sdk list java` | 查看所有可用 Java 版本 |
| `sdk use java 21.0.11-tem` | 当前终端临时切换版本 |
| `sdk default java 21.0.11-tem` | 设置默认版本 |
| `sdk install maven` | 安装 Maven |
| `sdk install gradle` | 安装 Gradle |
| `sdk selfupdate` | 更新 SDKMAN! 本身 |

---

## 8. 安装 PM2（进程管理器）

PM2 用于管理长期运行的后台进程（Node.js、Python、Shell 脚本等），并支持开机自动恢复。

### 安装

```bash
npm install -g pm2
```

验证安装：

```bash
pm2 --version
```

### 配置开机自启

PM2 通过 macOS `launchd` 实现登录后自动恢复已保存的进程。

```bash
# 生成并注册 launchd 服务
pm2 startup launchd

# 按提示执行输出的 sudo 命令，例如：
# sudo env PATH=$PATH:/Users/yusizhen/.nvm/versions/node/v24.16.0/bin pm2 startup launchd -u yusizhen --hp /Users/yusizhen
```

> **注意**：`pm2 startup` 需要 sudo 权限，因为它要在 `/Library/LaunchDaemons` 或 `~/Library/LaunchAgents` 下创建 plist 文件。

### 配置进程

创建 `ecosystem.config.js`：

```js
module.exports = {
  apps: [
    {
      name: 'api-server',
      script: './services/api/server.js',
      instances: 1,
      autorestart: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      env: { NODE_ENV: 'production' }
    },
    {
      name: 'data-processor',
      script: './services/data/main.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true
    },
    {
      name: 'backup-job',
      script: './scripts/backup.sh',
      interpreter: 'bash',
      instances: 1,
      cron_restart: '0 2 * * *',
      autorestart: false
    }
  ]
};
```

### 启动与保存

```bash
# 启动所有进程
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs

# 保存当前进程列表（关键！开机自启依赖此步骤）
pm2 save
```

> **⚠️ 重要**：每次增删进程后，必须执行 `pm2 save`，否则重启后不会自动恢复新进程。

### 常用命令

| 命令 | 作用 |
|------|------|
| `pm2 start <name>` | 启动进程 |
| `pm2 stop all` | 停止全部进程 |
| `pm2 restart <name>` | 重启指定进程 |
| `pm2 delete <name>` | 删除进程 |
| `pm2 logs <name>` | 查看指定进程日志 |
| `pm2 monit` | 打开实时监控面板 |
| `pm2 save` | 保存进程列表（供开机恢复） |

---

## 9. 安装 GitHub CLI (gh)

用于在终端操作 GitHub（查看 issue、PR、star 列表等）。

### 安装

```bash
brew install gh
```

### 登录

```bash
gh auth login
```

按提示选择：
- **GitHub.com** → **HTTPS** → **Login with a web browser**
- 终端会显示一个 one-time code，打开浏览器访问 `https://github.com/login/device` 粘贴即可

### 常用命令

| 命令 | 作用 |
|------|------|
| `gh repo view owner/repo` | 查看仓库信息 |
| `gh api user/starred --paginate` | 查看自己的 star 列表 |
| `gh release list --repo owner/repo` | 查看 release |

---

## 10. 安装 markdown-reader

TUI Markdown 文件浏览器和阅读器，支持 Mermaid 图表、LaTeX 数学公式、实时编辑等。

> 项目：[leboiko/markdown-reader](https://github.com/leboiko/markdown-reader)  
> 二进制名：`markdown-reader`  
> crates.io 包名：`markdown-tui-explorer`

### 安装（Homebrew）

```bash
# 添加 tap 后安装（国内网络建议开代理）
ALL_PROXY=http://localhost:7890 brew tap leboiko/tap
ALL_PROXY=http://localhost:7890 brew install markdown-reader
```

### 使用

```bash
# 浏览当前目录的 markdown 文件
markdown-reader .

# 打开单个文件
markdown-reader README.md
```

### 快捷键

| 按键 | 作用 |
|------|------|
| `o` | 大纲导航 |
| `i` | 混合编辑模式（光标所在块显示 raw markdown） |
| `c` | 设置面板（主题、字体等） |
| `/` | 全局搜索 |

### 设置别名

在 `~/.zshrc` 中添加：

```zsh
alias mdr="markdown-reader"
```

之后可用 `mdr .` 或 `mdr README.md`。

---

## 11. 安装 Glow

终端 Markdown 渲染器，基于 Charmbracelet 的 TUI 框架。相比 `markdown-reader` 更轻量，适合日常快速阅读 Markdown 文件。

> 项目：[charmbracelet/glow](https://github.com/charmbracelet/glow)

### 安装（Homebrew）

```bash
brew install glow
```

### 用法

```bash
# TUI 浏览当前目录所有 markdown（推荐）
glow -t .

# 直接打开单个文件
glow -t README.md

# 限制宽度
glow -t -w 80 README.md

# 带行号
glow -t -l README.md
```

> **注意**：`-t`（TUI 模式）是推荐用法。它使用内置渲染引擎，自动分页且无乱码。不使用 `-t` 时 glow 会调用系统 `$PAGER`（如 `less`），在 Ghostty 下可能出现样式乱码。

### 配置别名

在 `~/.zshrc` 中添加：

```zsh
# glow: Markdown TUI 阅读器
unalias md 2>/dev/null || true
md() {
  if [[ -f "$1" ]]; then
    glow -t "$1"
  elif [[ -d "$1" ]]; then
    glow -t "$1"
  else
    glow -t .
  fi
}
```

> `unalias md` 是为了覆盖 Oh My Zsh 某些插件预定义的 `md='mkdir -p'` alias。

之后可用：
- `md` — 浏览当前目录所有 markdown
- `md README.md` — 直接打开文件
- `md ~/docs` — 浏览指定目录

### TUI 快捷键

| 按键 | 作用 |
|------|------|
| `↑`/`↓` 或 `j`/`k` | 滚动 |
| `PgUp`/`PgDn` 或 `b`/`f` | 翻页 |
| `g` / `G` | 跳到开头 / 结尾 |
| `/` | 搜索文档内容 |
| `←`/`→` | 文件列表 ↔ 预览切换 |
| `q` / `Esc` | 退出 |

---

## 12. 安装 bat

`cat` 的替代品，支持语法高亮、Git 集成、自动分页。

> 项目：[sharkdp/bat](https://github.com/sharkdp/bat)

### 安装

```bash
brew install bat
```

### 基础用法

```bash
# 替代 cat，带语法高亮
bat file.py

# 查看多个文件（带文件名标题）
bat file1.js file2.js

# 只查看指定行范围
bat --line-range 10:20 file.log

# 显示不可见字符
bat -A file.txt
```

### 关于分页

bat 本身不内嵌分页器，但会自动调用系统的 `less`（macOS 自带 `/usr/bin/less`）。输出能 fit 在一屏内时自动退出，超出时进入分页模式。

```bash
# 禁用分页直接输出（适合管道）
bat --paging=never file.txt | grep "error"
```

### 配置别名

在 `~/.zshrc` 中添加：

```zsh
# 替代 cat（保留原 cat 可用）
alias cat='bat --paging=never'
```

---

## 13. 安装 codegraph

本地代码智能索引工具，为 AI Agent 提供代码库的符号搜索、调用关系、影响分析等能力。

> 项目：[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)

### 安装

```bash
npm install -g @colbymchenry/codegraph
```

验证安装：

```bash
codegraph --version
```

### 初始化项目

进入项目目录后执行：

```bash
# 初始化并建立索引
codegraph init -i

# 或先初始化，再手动索引
codegraph init
codegraph index
```

索引完成后，codegraph 会在后台监听文件变更并自动同步。

### 常用 Alias

在 `~/.zshrc` 中添加：

```zsh
source ~/.config/zsh/codegraph-aliases.zsh
```

`~/.config/zsh/codegraph-aliases.zsh` 内容参考：

```zsh
alias cg='codegraph'
alias cg-idx='codegraph index'
alias cg-s='codegraph sync'
alias cg-st='codegraph status'
alias cg-c='codegraph context'
alias cg-tr='codegraph trace'
alias cg-ca='codegraph callers'
alias cg-ce='codegraph callees'
alias cg-im='codegraph impact'
alias cg-serve='codegraph serve --mcp'
alias cg-h='glow ~/.config/zsh/codegraph-help.md 2>/dev/null || cat ~/.config/zsh/codegraph-help.md'
```

### MCP 服务

codegraph 支持以 MCP 服务器模式运行，供 Claude 等 AI 工具调用：

```bash
# 启动 MCP 服务
codegraph serve --mcp

# 或使用 alias
cg-serve
```

---

## 14. 生效

1. **完全退出 Ghostty**（Cmd + Q）
2. **重新打开 Ghostty**
3. 检查提示符是否正常显示

```bash
# 验证 Starship
starship --version

# 验证字体（应显示图标而非方块）
echo "    "

# 验证 bat
bat --version

# 验证 codegraph
codegraph --version
```

---

## 常见问题

### Q: 提示符显示方块或问号？

A: Nerd Font 未正确安装。检查 Ghostty 配置的 `font-family` 是否匹配实际字体族名。

```bash
# 查看已安装字体
ls ~/Library/Fonts/ | grep -i jetbrains
```

### Q: Starship 配置报错 TOML parse error？

A: 格式字符串中使用了双引号 `"` 但包含 `\[` 转义。改用单引号 `'` 包裹含转义的字符串。

### Q: zoxide / fzf 命令找不到？

A: 检查两点：

1. **`~/.zshrc` 开头必须有 Homebrew 初始化**，因为 macOS 终端默认不加载 `~/.zprofile`：
   ```zsh
   eval "$(/opt/homebrew/bin/brew shellenv zsh)"
   ```

2. **zoxide 不要加 `--cmd cd`**，否则不会创建 `z` 命令：
   ```zsh
   # ✅ 正确
   eval "$(zoxide init zsh)"

   # ❌ 错误（只有 cd / cdi，没有 z / zi）
   eval "$(zoxide init zsh --cmd cd)"
   ```

### Q: 之前装过 Powerlevel10k，如何彻底清理？

```bash
rm -rf ~/.oh-my-zsh/custom/themes/powerlevel10k
rm -f ~/.p10k.zsh
rm -rf ~/.cache/p10k*
rm -f ~/.zcompdump*
```

然后在 `~/.zshrc` 中删除所有含 `p10k` 或 `powerlevel10k` 的行。

---

## 组件说明

| 组件 | 作用 |
|------|------|
| **Ghostty** | 终端模拟器，GPU 加速，原生 macOS 应用 |
| **Oh My Zsh** | zsh 插件框架，管理插件和补全 |
| **Starship** | 命令提示符主题，Rust 编写，跨 Shell |
| **JetBrainsMono Nerd Font** | 等宽编程字体，含图标字形 |
| **Homebrew** | macOS 包管理器 |
| **zoxide** | 智能目录跳转，替代 `cd` |
| **fzf** | 模糊查找工具 |
| **Catppuccin Mocha** | 暗色配色方案，低饱和度护眼 |
| **SDKMAN!** | Java/JVM 工具链版本管理器（Java、Maven、Gradle 等） |
| **PM2** | Node.js 进程管理器，支持开机自启、日志管理、进程监控 |
| **GitHub CLI** | 终端操作 GitHub（issue、PR、star、release 等） |
| **Glow** | 轻量终端 Markdown 渲染器，TUI 浏览，自动分页 |
| **bat** | `cat` 替代品，语法高亮、Git 集成、自动分页 |
| **codegraph** | 本地代码智能索引，为 AI Agent 提供符号搜索和调用分析 |
| **markdown-reader** | TUI Markdown 文件浏览器，支持 Mermaid/LaTeX/实时编辑 |
