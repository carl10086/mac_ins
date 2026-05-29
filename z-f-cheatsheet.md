# zoxide + fzf 速查手册

> 安装：`brew install zoxide fzf`
>
> 配置（加到 `~/.zshrc`）：
> ```bash
> eval "$(zoxide init zsh --cmd cd)"
> source <(fzf --zsh)
> ```

---

## zoxide —— 智能目录跳转 (`z`)

### 核心用法

| 命令 | 作用 |
|------|------|
| `z foo` | 跳到最常访问的、匹配 "foo" 的目录 |
| `zi foo` | 交互式选择（多个匹配时弹出 fzf 列表） |
| `zq foo` | 只查询、显示会跳到哪，不实际跳转 |
| `z -` | 返回上一个目录 |
| `z ..` | 上级目录（接管 cd 后） |

### 实际示例

```bash
# 假设你常访问 ~/soft/projects/work/frontend
z front              # 直接跳过去
z work front         # 多个关键词匹配
zi pro               # 如果有多个项目匹配，弹出列表让你选
```

### 数据库管理

| 命令 | 作用 |
|------|------|
| `zoxide query -l` | 列出所有已记录的目录 |
| `zoxide remove ~/old/path` | 从数据库删除某目录 |
| `zoxide import --from autojump ~/.local/share/autojump/autojump.txt` | 从 autojump 导入历史 |

> zoxide 使用 **frecency** 算法（频率 + 最近访问）排序，越常用的目录排名越高。

---

## fzf —— 模糊查找 (`Ctrl+R` / `Ctrl+T`)

### 快捷键

| 快捷键 | 作用 |
|--------|------|
| `Ctrl+R` | 搜索历史命令 |
| `Ctrl+T` | 搜索当前目录下的文件 |
| `Alt+C` | 搜索并切换到子目录 |

### fzf 界面操作

| 按键 | 作用 |
|------|------|
| `↑/↓` | 上下选择 |
| `Enter` | 确认选择 |
| `Ctrl+J/K` | 上下选择（同 ↑/↓） |
| `Ctrl+C` / `Esc` | 取消 |
| `Tab` | 多选模式（标记多个） |

### 搜索语法

| 输入 | 匹配规则 |
|------|----------|
| `foo` | 模糊匹配 "foo" |
| `'foo` | 精确匹配 "foo"（前缀加单引号） |
| `^foo` | 以 "foo" 开头 |
| `foo$` | 以 "foo" 结尾 |
| `!bar` | 排除包含 "bar" 的结果 |
| `foo !bar` | 包含 "foo" 但不包含 "bar" |

---

## 组合使用

### zoxide + fzf = `zi`

```bash
zi front    # 弹出 fzf 列表，从所有匹配 "front" 的目录中选择
```

### fzf 管道用法

```bash
# 配合 git：选择分支切换
git checkout $(git branch -a | fzf)

# 配合 kill：选择进程终止
kill $(ps aux | fzf | awk '{print $2}')

# 配合 vim：选择文件打开
vim $(fzf)
```

---

## 一句话记忆

- **`z` = "记住我去哪，帮我跳过去"**
- **`fzf` = "列表太长，打字就能过滤"**
- **`zi` = 两者合体：记住的目录太多？fzf 帮你挑**
