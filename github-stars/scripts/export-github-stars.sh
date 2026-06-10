#!/bin/bash
# 导出 GitHub Star 列表为可读格式
# 用法: ./scripts/export-github-stars.sh [输出文件名]

OUTPUT_FILE="${1:-my-stars.tsv}"

echo "正在导出 star 列表到 ${OUTPUT_FILE} ..."

gh api user/starred --paginate | jq -r '
  .[] |
  [
    .full_name,
    (.language // "N/A"),
    (.description // "" | gsub("[\t\n]"; " ")),
    .html_url
  ] | @tsv
' > "$OUTPUT_FILE"

COUNT=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
echo "完成！共导出 ${COUNT} 个项目。"
echo "文件位置: $(pwd)/${OUTPUT_FILE}"
