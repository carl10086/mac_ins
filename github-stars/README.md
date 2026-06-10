# github-stars

GitHub stars 整理工作：从"无序收藏"到"按 Lists 分组"。

**来源**：从 `ys-learn/` 迁移过来（2026-06-10）。

## 目录结构

```
github-stars/
├── README.md                # 本文件
├── scripts/                 # 6 个工具脚本
├── notes/                   # 2 个学习笔记
├── docs/                    # 1 个 spec + 1 个 plan
└── data/                    # 4 个数据/日志/测试（含 gitignored 的 star 数据）
```

## scripts/

| 文件 | 作用 |
|------|------|
| `classify-stars.py` | 主分类器：读 `my-stars.jsonl`，按预定义分类模板分类 |
| `export-github-stars.sh` | 调用 `gh api user/starred` 导出原始 JSON |
| `export-stars-jsonl.sh` | 把原始 JSON 转成 JSONL（每行一个项目）|
| `bulk-add-fast.py` | 高效批量添加：用 requests 直接调 GraphQL API |
| `bulk-add-gh.py` | 批量添加：用 `gh api graphql` 避开 SSL 问题 |
| `bulk-add-to-lists.py` | 批量添加：基于 classify-stars.py 的分类结果 |

## notes/

| 文件 | 内容 |
|------|------|
| `2026-06-10-github-stars-organization.md` | 整理方案与操作指南 |
| `2026-06-10-github-stars-classified.md` | 1234 个项目的分类结果快照 |

## docs/

| 文件 | 内容 |
|------|------|
| `2026-06-10-github-stars-organization-design.md` | spec：目标、技术栈、命令、目录结构、验收清单 |
| `2026-06-10-github-stars-organization-plan.md` | plan：5 个 task 的实施步骤 |

## data/

| 文件 | 类型 | 是否入 mac_ins 库 |
|------|------|------------------|
| `my-stars.jsonl` | star 导出数据 | 建议忽略（个人收藏，含敏感信息）|
| `stars-classified.md` | 分类结果 | 可入 |
| `bulk-add.log` | 批量添加日志 | 可入（历史记录）|
| `test_batch.py` | 批量 mutation 测试脚本 | 可入 |

## 工作流

```bash
# 1. 导出 stars
./scripts/export-github-stars.sh > my-stars.json
./scripts/export-stars-jsonl.sh  # 生成 my-stars.jsonl

# 2. 分类
python3 scripts/classify-stars.py

# 3. 批量添加到 GitHub Lists
python3 scripts/bulk-add-gh.py  # 或 bulk-add-fast.py / bulk-add-to-lists.py
```

## 相关项目

- 原始学习笔记：原 `ys-learn/notes/2026-06-10-github-stars-*.md`（已迁移到 `notes/`）
- spec / plan：原 `ys-learn/docs/ys-powers/{specs,plans}/2026-06-10-github-stars-organization-*`（已迁移到 `docs/`）
