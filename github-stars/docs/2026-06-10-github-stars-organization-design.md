# Spec: GitHub Stars 整理方案

## Objective

帮助用户系统地整理 GitHub 上已 star 的项目，从"无序收藏"变成"分组清晰的知识库"。

**用户故事**：
- 作为开发者，我 star 了很多项目，但难以快速找到特定领域的工具
- 我希望用 GitHub Lists 功能给 star 项目分组，方便后续检索
- 我需要先导出所有 star 项目的详情，离线浏览后再决定分类策略

**成功标准**：
1. 能通过 `gh` CLI 导出所有 star 项目的完整信息（名称、描述、语言、URL）
2. 理解 GitHub Lists 的功能和限制
3. 制定一套适合自己的分类维度和整理流程
4. 产出一份可复用的操作指南笔记

## Tech Stack

- **工具**：GitHub CLI (`gh`)
- **API**：GitHub REST API (`/user/starred`)
- **辅助**：`jq`（JSON 处理，可选）
- **产出**：Markdown 文档

## Commands

```bash
# 1. 验证 gh 登录状态
gh auth status

# 2. 导出 star 列表（基础 JSON）
gh api user/starred --paginate > my-stars.json

# 3. 导出为可读格式（需安装 jq）
gh api user/starred --paginate | jq -r '.[] | "\(.full_name)\t\(.language)\t\(.description)"' > my-stars.tsv

# 4. 查看单个项目的详细信息
gh api repos/<owner>/<repo>

# 5. 查看 GitHub Lists（通过 API 预览， Lists 主要在网页端管理）
gh api user/lists
```

## Project Structure

产出文档存放位置：

```
notes/
└── 2026-06-10-github-stars-organization.md    # 主文档：整理方案与操作指南
    ├── gh-star-导出命令与脚本说明
    ├── github-lists-功能解析
    ├── 推荐分类模板
    └── 实际整理记录（用户后续填写）
```

## Code Style

本文档非代码项目，无代码风格要求。文档编写约定：

- 所有说明使用中文
- 命令、API 端点、字段名保持英文原文
- 代码块标注语言类型（bash、json）

示例：

```bash
# 获取 star 列表并提取关键字段
gh api user/starred --paginate | jq -r '
  .[] |
  {
    name: .full_name,
    lang: .language,
    desc: .description,
    url: .html_url
  }
'
```

## Testing Strategy

无自动化测试，采用**手动验证**：

1. **命令验证**：运行 `gh api user/starred`，确认返回 JSON 数据且包含预期字段
2. **数据完整性验证**：对比 GitHub 网页上 [github.com/stars](https://github.com/stars) 显示的数量与导出数据的条目数
3. **Lists 功能验证**：在网页端创建一个测试 List，确认项目可正常添加/移除

## Boundaries

- **Always**：
  - 导出数据前确认 `gh auth status` 已登录
  - 将导出的 star 数据文件加入 `.gitignore`（避免个人信息泄露）
  - 在 `notes/` 中记录整理过程中的分类决策

- **Ask first**：
  - 使用第三方工具处理 star 数据（如需要脚本辅助）
  - 修改已有的 GitHub Lists 结构（删除/重命名）

- **Never**：
  - 将包含敏感信息的 API 响应提交到仓库
  - 使用未经验证的第三方服务处理 GitHub 数据
  - 批量操作（如取消 star）没有备份和确认

## Success Criteria

1. `gh api user/starred` 成功返回数据，包含 `full_name`、`description`、`language`、`html_url` 字段
2. 文档中包含 GitHub Lists 的创建步骤截图说明或文字指引
3. 提供至少一套推荐分类模板（如：AI 工具、CLI 工具、前端框架、学习资源等）
4. 用户阅读文档后能够独立完成：导出 → 浏览 → 创建 Lists → 归类的完整流程

## Open Questions

1. 用户当前 star 的项目数量级是多少？（影响是否需要分页处理建议）
2. 分类维度偏好：按技术领域、按用途场景、还是混合？
3. 是否需要定期重新导出和更新 Lists？
