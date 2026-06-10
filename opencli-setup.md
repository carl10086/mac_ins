# OpenCLI 本地安装备忘

> 项目：[jackwener/opencli](https://github.com/jackwener/opencli)  
> 用途：把任意网站变成 CLI，并在登录态浏览器上跑 Browser Use  
> 前提：Node.js >= 20，Chrome/Chromium
>
> **路径说明**：以下 `~/soft/projects/opencli` 为个人源码存放路径，换机/拷贝时请替换为实际路径。

---

## 1. 安装 CLI 工具

### 方式 A：npm 全局安装（推荐）

```bash
# 验证 Node.js 版本（要求 >= v20.0.0，不满足时用 brew install node 升级）
node --version

# 全局安装
npm install -g @jackwener/opencli

# 验证
opencli --version
```

### 方式 B：源码运行（开发/调试）

```bash
# 已克隆到 ~/soft/projects/opencli
cd ~/soft/projects/opencli
npm install

# 临时运行（不安装全局命令）
npx tsx src/main.ts <command>
```

---

## 2. 安装 Chrome 扩展（手动）

扩展源码位于 `~/soft/projects/opencli/extension/dist/`（构建后目录）。

```bash
# 若 dist/ 不存在，先构建（extension 是独立 npm 项目，需单独装依赖）
cd ~/soft/projects/opencli/extension
npm install      # 安装 vite 等构建依赖
npm run build    # 输出到 dist/
```

**加载步骤：**

1. 打开 Chrome → 地址栏输入 `chrome://extensions`
2. 开启右上角「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `~/soft/projects/opencli/extension/dist/`（含 `manifest.json` 的文件夹）

> **注意**：扩展更新后（源码拉取新 commit），若 `manifest.json` 无变更，Chrome 自动刷新；若 manifest 有变更，需点击扩展卡片的「重新加载」按钮。

---

## 3. 验证环境

```bash
# 诊断daemon、扩展、浏览器连接
opencli doctor

# 期望输出：
# Daemon: running (PID xxx)
# Extension: connected (v1.x.x)
# Profiles: xxxxxxxx
#
# 如果 doctor 输出红色，参见第 7 节「Extension disconnected」排查。

# 查看可用命令（165+ 站点适配器）
opencli list | head -20
```

---

## 4. Claude Code Skill 安装

OpenCLI 提供 8 个 Skill 指导 Claude Code 何时/如何调用命令。**核心 2 个必装，其余按需。**

```bash
mkdir -p .claude/skills

# ========== 核心（必须）==========
rm -rf .claude/skills/opencli-usage \
  && cp -r ~/soft/projects/opencli/skills/opencli-usage .claude/skills/
rm -rf .claude/skills/opencli-browser \
  && cp -r ~/soft/projects/opencli/skills/opencli-browser .claude/skills/

# ========== 可选（按需）==========
rm -rf .claude/skills/opencli-adapter-author \
  && cp -r ~/soft/projects/opencli/skills/opencli-adapter-author .claude/skills/   # 写新 adapter
rm -rf .claude/skills/opencli-autofix \
  && cp -r ~/soft/projects/opencli/skills/opencli-autofix .claude/skills/          # 修复坏 adapter
rm -rf .claude/skills/opencli-browser-sitemap \
  && cp -r ~/soft/projects/opencli/skills/opencli-browser-sitemap .claude/skills/  # 站点地图导航
rm -rf .claude/skills/opencli-sitemap-author \
  && cp -r ~/soft/projects/opencli/skills/opencli-sitemap-author .claude/skills/   # 维护站点地图
rm -rf .claude/skills/smart-search \
  && cp -r ~/soft/projects/opencli/skills/smart-search .claude/skills/             # 搜索路由
```

### Skill 路由速查

| 场景 | 加载的 Skill | 说明 |
|------|-------------|------|
| "opencli 能做什么？" | `opencli-usage` | 顶层导航。告诉 Claude Code 有三类能力：Adapter / Browser / External CLI，并建议用 `opencli list -f json` 动态发现命令 |
| "帮我点击网页上的按钮" | `opencli-browser` | 浏览器自动化。指导 Claude Code 使用 `state` / `click` / `type` / `find` / `network` 等原语操作登录态浏览器 |
| "写个 xxx 网站的 adapter" | `opencli-adapter-author` | Adapter 开发。从站点侦察、API 发现、字段解码到 `verify` 验证的完整工作流 |
| "xxx 命令坏了怎么修" | `opencli-autofix` | 自动修复。通过 `--trace retain-on-failure` 收集证据 → 诊断 → 打补丁 → 验证 → 提交 GitHub issue |
| "这个网站有 sitemap 吗？" | `opencli-browser-sitemap` | 站点地图消费。指导 Agent 优先用 adapter best path，失败后走 browser fallback path |
| "我要为这个网站写 sitemap" | `opencli-sitemap-author` | 站点地图编写。为 Agent 编写任务执行图（page / workflow / pitfall），非 SEO 地图 |
| "帮我搜索 xxx" | `smart-search` | 智能搜索路由。先 `opencli list` 预检，再选 1 个 AI 源 + 1-2 个专用源，控制调用频率 |

### Skill 核心约束速查

每个 skill 都有 `allowed-tools` 限制和硬边界，Claude Code 加载后会自动遵守：

| Skill | allowed-tools | 硬边界 |
|-------|---------------|--------|
| `opencli-usage` | `Bash(opencli:*), Read` | 不 hard-code adapter 列表；以 `opencli list -f json` 为准 |
| `opencli-browser` | `Bash(opencli:*), Read, Edit, Write` | 10 条 Critical rules；优先 numeric ref；`state` → action → `state` |
| `opencli-adapter-author` | `Bash(opencli:*), Read, Edit, Write` | 只改 `adapterSourcePath`；不改 `src/` / `extension/` / `tests/` |
| `opencli-autofix` | `Bash(opencli:*), Bash(gh:*), Read, Edit, Write` | Max 3 轮修复；`AUTH_REQUIRED` / `BROWSER_CONNECT` / CAPTCHA 不修改代码 |
| `opencli-browser-sitemap` | `Bash(opencli:*), Read, Edit, Write, Grep` | Sitemap 是 prior knowledge，browser state 是 truth |
| `opencli-sitemap-author` | `Bash(opencli:*), Read, Edit, Write, Grep` | 不写 secrets；不写 brittle snapshot indices；draft 放 `sitemap/draft-*.md` |
| `smart-search` | — | 预检 `opencli list`；1 AI 源 + 1-2 专用源；限频控制 |

> **注意**：以上 7 个 skill 位于 `opencli/skills/` 目录下。此外 `clis/antigravity/SKILL.md` 是第 8 个 skill，专用于控制 Antigravity 桌面应用（Electron CDP）。


> **重要**：Skill 只教 Claude Code **"如何思考"**，真正的能力来自 CLI 工具 + Chrome 扩展 + 165+ adapter。只拷贝 Skill 不装 CLI，命令会报 `command not found`。

---

## 5. 附录：mac_ins 项目配置（可选）

> 本节仅适用于 mac_ins 项目，其他项目可跳过。

### refer/ 符号链接

```bash
cd ~/soft/projects/mac_ins
ln -s ~/soft/projects/opencli refer/opencli
```

- `refer/opencli` 已加入 `.gitignore`，不上传
- 换机/重装时，先克隆 opencli 源码到相同路径，再重建符号链接

### 别名（~/.zshrc）

```zsh
# opencli 快捷入口
alias ocli='opencli'
alias ocli-doc='opencli doctor'
# 需预先安装 jq：brew install jq
alias ocli-list='opencli list -f json | jq ".[] | {site, name, strategy}"'
```

---

## 6. 更新与维护

### CLI 更新

```bash
# 全局安装方式
npm update -g @jackwener/opencli

# 源码方式
cd ~/soft/projects/opencli && git pull && npm install
```

### 扩展更新

```bash
cd ~/soft/projects/opencli/extension
npm run build
# Chrome 扩展页面点击「重新加载」
```

### Skill 同步

```bash
# opencli 源码更新后，skill 文件可能有变更，重新拷贝
rm -rf .claude/skills/opencli-usage \
  && cp -r ~/soft/projects/opencli/skills/opencli-usage .claude/skills/
rm -rf .claude/skills/opencli-browser \
  && cp -r ~/soft/projects/opencli/skills/opencli-browser .claude/skills/
# ... 按需同步其他 skill
```

---

## 7. 常见问题

### Q: `opencli: command not found`

A: npm 全局安装路径不在 PATH 中（尤其是用 Homebrew 安装的 Node）。检查：

```bash
which opencli
npm config get prefix   # 确认 prefix/bin 在 PATH 中
```

### Q: `opencli doctor` 提示 Extension disconnected

A: Chrome 未启动，或扩展未加载。检查：

1. Chrome 是否运行
2. `chrome://extensions` 中 OpenCLI 扩展是否显示且启用
3. 其他扩展（如 1Password）可能占用 CDP，临时禁用后重试

### Q: 安装了 Skill 但 Claude Code 不生成 opencli 命令

A: 检查 Skill 目录结构是否正确：

```bash
ls .claude/skills/opencli-browser/SKILL.md   # 必须存在
# 错误结构：.claude/skills/SKILL.md（缺少子目录）
```

Claude Code 按 `.claude/skills/<skill-name>/SKILL.md`（项目级）或 `~/.claude/skills/<skill-name>/SKILL.md`（全局）识别，不是按单个文件。

### Q: `opencli list` 能看到命令，但 `opencli xiaohongshu hot` 报错

A: 检查 adapter 的 strategy：

- `PUBLIC`：无需浏览器，直接调用
- `COOKIE` / `INTERCEPT` / `UI`：需要 Chrome 扩展已连接且已登录目标站点

```bash
opencli list -f json | jq '.[] | select(.site=="xiaohongshu") | {name, strategy}'
```

---

## 组件说明

| 组件 | 作用 |
|------|------|
| **OpenCLI CLI** | 命令入口，管理 adapter 注册和分发 |
| **Chrome 扩展（Browser Bridge）** | 通过 `chrome.debugger` 连接浏览器，接收 CLI 指令 |
| **Daemon** | 本地 HTTP + WebSocket 桥（localhost:19825），CLI ↔ 扩展的转发层 |
| **Adapter** | 站点命令封装（`clis/<site>/<command>.js`），165+ 个 |
| **Skill** | Claude Code 的行为说明书（`skills/*/SKILL.md`），8 个 |
