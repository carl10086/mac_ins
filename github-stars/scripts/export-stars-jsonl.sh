#!/bin/bash
# 导出 GitHub Star 列表为 JSONL 格式（每行一个项目）
# 用法: ./scripts/export-stars-jsonl.sh [输出文件名]

OUTPUT_FILE="${1:-my-stars.jsonl}"

echo "正在导出 star 列表到 ${OUTPUT_FILE} ..."

gh api user/starred --paginate | jq -c '
  .[] | {
    name: .full_name,
    node_id: .node_id,
    language: (.language // "N/A"),
    description: (.description // ""),
    url: .html_url,
    stars: .stargazers_count,
    updated_at: .updated_at
  }
' > "$OUTPUT_FILE"

COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
echo "完成！共导出 ${COUNT} 个项目。"
echo "文件位置: $(pwd)/${OUTPUT_FILE}"
