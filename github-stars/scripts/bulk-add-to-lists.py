#!/usr/bin/env python3
"""
批量将 GitHub Star 项目添加到 Lists。
基于 classify-stars.py 的分类逻辑，通过 GraphQL API 自动归类。
"""

import json
import subprocess
import sys
import time
from collections import defaultdict

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

# 从 classify-stars.py 导入分类逻辑
import importlib.util
spec = importlib.util.spec_from_file_location("classify", "scripts/classify-stars.py")
classify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_module)
classify_project = classify_module.classify_project


def get_list_mapping():
    """获取 List 名称 → ID 的映射"""
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
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    mapping = {}
    for node in data["data"]["viewer"]["lists"]["nodes"]:
        mapping[node["name"]] = node["id"]
    return mapping


def add_to_list(repo_id, list_id):
    """调用 GraphQL mutation 将项目添加到 List"""
    query = f"""
    mutation {{
      updateUserListsForItem(input: {{
        itemId: "{repo_id}"
        listIds: ["{list_id}"]
      }}) {{
        user {{ login }}
      }}
    }}
    """
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, result.stderr
    try:
        data = json.loads(result.stdout)
        if "errors" in data:
            return False, json.dumps(data["errors"])
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    input_file = "my-stars.jsonl"
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            input_file = arg
            break

    # 1. 获取 List ID 映射
    print("获取 Lists 信息...")
    list_mapping = get_list_mapping()
    print(f"找到 {len(list_mapping)} 个 Lists: {list(list_mapping.keys())}")

    # 2. 读取项目
    projects = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                projects.append(json.loads(line))
    print(f"读取了 {len(projects)} 个项目")

    # 3. 分类并建立 项目 -> List 映射
    print("正在分类...")
    project_to_list = {}
    skipped = []

    for proj in projects:
        categories = classify_project(proj)
        # 取第一个分类，映射到 List
        target_list = None
        for cat in categories:
            if cat in CATEGORY_TO_LIST:
                target_list = CATEGORY_TO_LIST[cat]
                break

        if target_list and target_list in list_mapping:
            project_to_list[proj["name"]] = {
                "node_id": proj["node_id"],
                "list_name": target_list,
                "list_id": list_mapping[target_list]
            }
        else:
            skipped.append(proj["name"])

    print(f"可归类: {len(project_to_list)}, 跳过: {len(skipped)}")
    if skipped:
        print(f"跳过的项目: {skipped[:10]}")

    # 4. 统计每个 List 的数量
    list_counts = defaultdict(int)
    for info in project_to_list.values():
        list_counts[info["list_name"]] += 1
    print("\n各 List 预计项目数:")
    for name, count in sorted(list_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {count}")

    # 5. 批量添加（带确认）
    print(f"\n即将把 {len(project_to_list)} 个项目添加到 Lists。")
    if "--yes" not in sys.argv:
        confirm = input("确认执行? [y/N]: ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    print("\n开始批量添加...")
    success = 0
    failed = 0
    errors = []

    for i, (name, info) in enumerate(project_to_list.items(), 1):
        ok, err = add_to_list(info["node_id"], info["list_id"])
        if ok:
            success += 1
            print(f"  [{i}/{len(project_to_list)}] ✓ {name} → {info['list_name']}")
        else:
            failed += 1
            errors.append((name, err))
            print(f"  [{i}/{len(project_to_list)}] ✗ {name} → ERROR: {err[:100]}")

        # 简单限速：每 100 个暂停 1 秒
        if i % 100 == 0:
            time.sleep(1)

    print(f"\n完成！成功: {success}, 失败: {failed}")
    if errors:
        print(f"\n错误示例:")
        for name, err in errors[:5]:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
