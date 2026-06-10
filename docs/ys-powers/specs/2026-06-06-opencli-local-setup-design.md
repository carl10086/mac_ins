# Spec: OpenCLI 本地安装与 Claude Code 集成备忘

## Objective

编写一份独立的 `opencli-setup.md` 备忘文档，记录从源码手动安装 OpenCLI、配置 Chrome 扩展、集成 Claude Code Skill 的完整步骤。目标读者是自己（重装/换机时快速恢复），语气为个人备忘，包含关键路径和命令，不解释基础原理。

## Tech Stack

- **Runtime**: Node.js >= 20
- **Package**: `@jackwener/opencli` (npm global 或源码运行)
- **Browser**: Chrome/Chromium + OpenCLI Browser Bridge Extension
- **AI Agent**: Claude Code (Claude Code CLI / claude.ai/code)
- **Shell**: zsh (macOS 15.x)

## Commands

### 1. CLI 工具安装（从源码）
```bash
# 验证 Node.js 版本
node --version

# 方式 A: npm 全局安装（推荐，稳定版）
npm install -g @jackwener/opencli

# 方式 B: 源码运行（开发/调试）
git clone git@github.com:jackwener/opencli.git ~/soft/projects/opencli
cd ~/soft/projects/opencli && npm install
npx tsx src/main.ts <command>
```

### 2. Chrome 扩展安装（手动）
```bash
# 扩展源码路径
~/soft/projects/opencli/extension/dist/

# 安装步骤
# 1. 打开 Chrome → chrome://extensions
# 2. 开启右上角「开发者模式」
# 3. 点击「加载已解压的扩展程序」
# 4. 选择 ~/soft/projects/opencli/extension/dist/
```

### 3. 环境验证
```bash
opencli doctor
opencli --version
opencli list | head -20
```

### 4. Claude Code Skill 安装
```bash
mkdir -p ~/.claude/skills

# 核心 skill（必须）
cp -r ~/soft/projects/opencli/skills/opencli-usage ~/.claude/skills/
cp -r ~/soft/projects/opencli/skills/opencli-browser ~/.claude/skills/

# 可选 skill（按需）
cp -r ~/soft/projects/opencli/skills/opencli-adapter-author ~/.claude/skills/
cp -r ~/soft/projects/opencli/skills/opencli-autofix ~/.claude/skills/
cp -r ~/soft/projects/opencli/skills/opencli-browser-sitemap ~/.claude/skills/
cp -r ~/soft/projects/opencli/skills/opencli-sitemap-author ~/.claude/skills/
cp -r ~/soft/projects/opencli/skills/smart-search ~/.claude/skills/
```

### 5. 项目符号链接维护（mac_ins）
```bash
# refer/ 目录下建立符号链接（已存在，换机时需重新创建）
cd ~/soft/projects/mac_ins
ln -s ~/soft/projects/opencli refer/opencli

# .gitignore 确保 refer/ 不上传
# refer/ 已加入 .gitignore
```

## Project Structure

```
mac_ins/
├── mac_ins.md              # 主备忘（不修改，独立文档）
├── opencli-setup.md        # ← 本文档产物（独立文件）
├── refer/
│   └── opencli -> ~/soft/projects/opencli    # 符号链接，指向源码
└── docs/ys-powers/specs/
    └── 2026-06-06-opencli-local-setup-design.md   # 本 spec
```

Claude Code Skill 安装位置（全局）：
```
~/.claude/skills/
├── opencli-usage/
│   └── SKILL.md
├── opencli-browser/
│   └── SKILL.md
├── opencli-adapter-author/
│   ├── SKILL.md
│   └── references/
├── opencli-autofix/
│   └── SKILL.md
├── opencli-browser-sitemap/
│   └── SKILL.md
├── opencli-sitemap-author/
│   ├── SKILL.md
│   └── references/
└── smart-search/
    ├── SKILL.md
    └── references/
```

## Code Style

文档风格遵循 mac_ins.md 现有约定：

```markdown
## N. 安装 xxx

> 项目：[owner/repo](url)  
> 用途：一句话说明  
> 前提：Node.js >= 20

```bash
# 命令带注释
npm install -g @jackwener/opencli
```

### 验证

```bash
opencli doctor
```

### 常用别名

在 `~/.zshrc` 中添加：

```zsh
alias ocli='opencli'
alias ocli-doc='opencli doctor'
```
```

- 标题使用「安装 xxx」格式
- 代码块标注 shell/zsh
- 表格用于对比（strategy、skill 用途等）
- 不展开「为什么」，只记「怎么做」和「路径在哪」

## Testing Strategy

无自动化测试（本文档是安装备忘，不是代码项目）。验证方式：

| 检查项 | 命令 | 期望结果 |
|--------|------|----------|
| CLI 可用 | `which opencli && opencli --version` | 输出版本号 |
| Daemon 运行 | `opencli doctor` | Extension: connected |
| Skill 加载 | Claude Code 对话中问「opencli 能做什么」 | 引用 opencli-usage skill |
| 符号链接 | `ls -la refer/opencli` | 指向正确路径 |

## Boundaries

- **Always**: 
  - 安装后先运行 `opencli doctor` 验证
  - 拷贝 skill 时保持目录结构（`skill-name/SKILL.md`）
  - 更新 opencli 源码后同步验证 skill 是否仍有效
- **Ask first**: 
  - 是否将 opencli-setup.md 整合进 mac_ins.md
  - 是否提交 skill 文件到版本控制（默认不提交，skill 在 ~/.claude/skills/）
- **Never**: 
  - 不要把 refer/opencli 的符号链接目标提交到 git
  - 不要手动修改 `cli-manifest.json`
  - 不要在未验证的 Chrome profile 上执行 `browser bind`

## Success Criteria

- [ ] `opencli-setup.md` 文件存在于 mac_ins 项目根目录
- [ ] 文档包含 CLI 安装、扩展安装、Skill 安装、项目链接四个部分
- [ ] 所有路径使用绝对路径或 `~` 简写，避免相对路径歧义
- [ ] 文档可被直接拷贝到其他项目使用（无 mac_ins 专属依赖）

## Open Questions

1. opencli 源码更新后，Chrome 扩展是否需要重新加载？（待验证：通常 dist/ 内容变化后扩展自动刷新，但 manifest 变更需重新加载）
2. `opencli-usage` 与 `opencli-browser` 两个 skill 是否足够覆盖日常需求，其余 skill 是否建议默认安装？（当前方案：核心 2 个必装，其余按需）
