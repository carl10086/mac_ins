#!/usr/bin/env python3
"""
高效批量添加 GitHub Star 项目到 Lists。
使用 requests 直接调用 GraphQL API，支持批量 mutation。
"""

import json
import subprocess
import sys
import time
from collections import defaultdict

import requests

# 细分分类 → List 名称映射
CATEGORY_TO_LIST = {
    "🤖 AI Agents": "ai agents",
    "🧠 LLM & Inference": "llm",
    "🎨 AI Apps & Creativity": "generative ai",
    "👁️ Computer Vision": "generative ai",
    "🧠 ML Frameworks": "generative ai",
    "📊 RAG & Knowledge": "generative ai",
    "🤖 Robotics": "generative ai",
    "🛠️ DevTools - Editors & IDE": "dev tools",
    "🛠️ DevTools - Terminal & CLI": "dev tools",
    "🛠️ DevTools - Build & Deploy": "dev tools",
    "🎨 Visualization": "dev tools",
    "📈 Benchmarking & Testing": "dev tools",
    "☁️ Cloud Native & Infra": "cloud native",
    "🗄️ Data & Storage": "infra",
    "📊 Data Processing": "infra",
    "💾 Backup & Storage": "infra",
    "⏱️ Task Queue & Scheduler": "infra",
    "🔧 System & Kernel": "system & network",
    "🌐 Networking": "system & network",
    "📡 VPN & Proxy": "system & network",
    "🔒 Security": "system & network",
    "📚 Learning & Reference": "learning",
    "📝 Docs & Note-taking": "learning",
    "💻 Programming Languages": "languages & libs",
    "🎵 Media & Audio": "medias & others",
    "💻 Remote Desktop": "medias & others",
    "🏢 Enterprise & Admin": "medias & others",
    "🎮 Games": "medias & others",
    "🔌 Embedded & IoT": "medias & others",
    "📱 Mobile & Desktop": "medias & others",
    "🌐 Web & API": "medias & others",
    "🔬 Experiments": "medias & others",
}

# 导入分类逻辑
import importlib.util
spec = importlib.util.spec_from_file_location("classify", "scripts/classify-stars.py")
classify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_module)
classify_project = classify_module.classify_project

GRAPHQL_URL = "https://api.github.com/graphql"
BATCH_SIZE = 5  # 每批 mutation 数量


def get_token():
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return result.stdout.strip()


def get_list_mapping(token):
    query = """
    query {
      viewer {
        lists(first: 20) {
          nodes {
            id
            name
          }
        }
      }
    }
    """
    resp = requests.post(
        GRAPHQL_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query}
    )
    data = resp.json()
    mapping = {}
    for node in data["data"]["viewer"]["lists"]["nodes"]:
        mapping[node["name"]] = node["id"]
    return mapping


def batch_mutate(token, items, max_retries=3):
    """
    items: [(alias, repo_node_id, list_id), ...]
    返回: {alias: (success, error), ...}
    """
    mutations = []
    for alias, repo_id, list_id in items:
        mutations.append(f"""
      {alias}: updateUserListsForItem(input: {{
        itemId: "{repo_id}"
        listIds: ["{list_id}"]
      }}) {{
        user {{ login }}
      }}
    """)

    query = "mutation {\n" + "\n".join(mutations) + "\n}"

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                GRAPHQL_URL,
                headers={"Authorization": f"Bearer {token}"},
                json={"query": query},
                timeout=30
            )

            if resp.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {alias: (False, f"HTTP {resp.status_code}") for alias, _, _ in items}

            data = resp.json()
            results = {}

            if "errors" in data:
                error_aliases = set()
                for err in data["errors"]:
                    if "path" in err and len(err["path"]) >= 2:
                        error_aliases.add(err["path"][1])

                for alias, _, _ in items:
                    if alias in error_aliases:
                        err_msg = next((e["message"] for e in data["errors"]
                                       if "path" in e and len(e["path"]) >= 2 and e["path"][1] == alias), "Unknown")
                        results[alias] = (False, err_msg)
                    else:
                        results[alias] = (True, None)
            else:
                for alias, _, _ in items:
                    results[alias] = (True, None)

            return results

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"    请求失败 (attempt {attempt + 1}): {str(e)[:60]}, 重试中...")
                time.sleep(2 ** attempt)
            else:
                return {alias: (False, str(e)[:100]) for alias, _, _ in items}

    return {alias: (False, "Max retries exceeded") for alias, _, _ in items}


def main():
    input_file = "my-stars.jsonl"
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            input_file = arg

    print("获取 GitHub token...")
    token = get_token()

    print("获取 Lists 信息...")
    list_mapping = get_list_mapping(token)
    print(f"找到 {len(list_mapping)} 个 Lists")

    # 读取项目
    projects = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                projects.append(json.loads(line))
    print(f"读取了 {len(projects)} 个项目")

    # 分类
    print("正在分类...")
    assignments = []  # [(repo_name, repo_id, list_id), ...]
    for proj in projects:
        categories = classify_project(proj)
        target_list = None
        for cat in categories:
            if cat in CATEGORY_TO_LIST:
                target_list = CATEGORY_TO_LIST[cat]
                break

        if target_list and target_list in list_mapping:
            assignments.append((proj["name"], proj["node_id"], list_mapping[target_list]))

    print(f"可归类: {len(assignments)}")

    # 统计
    list_counts = defaultdict(int)
    for _, _, list_id in assignments:
        name = [k for k, v in list_mapping.items() if v == list_id][0]
        list_counts[name] += 1
    print("\n各 List 预计项目数:")
    for name, count in sorted(list_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {count}")

    if "--yes" not in sys.argv:
        confirm = input("\n确认执行? [y/N]: ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    print(f"\n开始批量添加，每批 {BATCH_SIZE} 个...")
    success = 0
    failed = 0
    errors = []

    total = len(assignments)
    for i in range(0, total, BATCH_SIZE):
        batch = assignments[i:i + BATCH_SIZE]
        batch_items = []
        for j, (name, repo_id, list_id) in enumerate(batch):
            alias = f"m{j}"
            batch_items.append((alias, repo_id, list_id))

        results = batch_mutate(token, batch_items)

        for j, (name, repo_id, list_id) in enumerate(batch):
            alias = f"m{j}"
            ok, err = results.get(alias, (False, "No result"))
            if ok:
                success += 1
            else:
                failed += 1
                errors.append((name, err))
                print(f"  ✗ {name}: {err[:80]}")

        # 进度显示
        processed = min(i + BATCH_SIZE, total)
        if processed % 50 == 0 or processed == total:
            print(f"  进度: {processed}/{total} ({processed * 100 // total}%) 成功: {success} 失败: {failed}")

        # 限速
        time.sleep(0.3)

    print(f"\n完成！成功: {success}, 失败: {failed}")
    if errors:
        print(f"\n错误示例 (前 5 个):")
        for name, err in errors[:5]:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
