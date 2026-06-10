#!/usr/bin/env python3
"""
基于功能和出发点，为 GitHub Star 项目智能分类。
分类逻辑基于：描述、名称、语言等多维度判断。
"""

import json
import sys
import re

# 分类定义：名称、匹配关键词、排除关键词
CATEGORIES = [
    {
        "name": "🤖 AI Agents",
        "keywords": [
            "agent", "autonomous", "crewai", "autogpt", "metagpt", "multion",
            "browser-use", "computer use", "operator", "agentic", "swarm",
            "orchestrat", "workflow automation", "auto-gpt", "babyagi",
            "langgraph", "autogen", "superpowers", "claw code", "hermes-agent",
            "openhands", "ai-driven development", "taskmatrix", "open interpreter",
            "devin", "swe-agent", "ai software engineer"
        ],
        "exclude": ["management agent", "user agent"]
    },
    {
        "name": "🧠 LLM & Inference",
        "keywords": [
            "llm", "gpt", "claude", "ollama", "vllm", "transformers",
            "huggingface", "hugging face", "model server", "inference engine",
            "quantization", "gguf", "exllama", "text generation", "lm studio",
            "openai", "anthropic", "gemini", "mistral", "llama.cpp",
            "kobold", "tabby", "continue.dev", "copilot", "code completion",
            "codeium", "twinny", "aider", "codex", "cursor",
            "llama models", "chatglm", "deepseek", "janus", "verl",
            "sglang", "vllm", "tensorrt", "onnx runtime",
            "lm evaluation", "eval harness", "context-hub",
            "lm-evaluation", "evaluation harness", "model evaluation"
        ],
        "exclude": []
    },
    {
        "name": "📊 RAG & Knowledge",
        "keywords": [
            "rag", "retrieval augmented", "embedding", "vector database",
            "vector store", "knowledge base", "knowledge graph",
            "semantic search", "similarity search", "document qa",
            "chunking", "indexing", "pinecone", "weaviate", "chroma",
            "milvus", "qdrant", "mem0", "open-webui",
            "supermemory", "second brain"
        ],
        "exclude": []
    },
    {
        "name": "🎨 AI Apps & Creativity",
        "keywords": [
            "chatbot", "chat ui", "chat interface", "ai assistant",
            "personal assistant", "ai image", "ai video", "ai audio",
            "stable diffusion", "midjourney", "comfyui", "fooocus",
            "invokeai", "automatic1111", "suno", "udio", "musicgen",
            "voice clone", "tts", "text to speech", "speech to text",
            "whisper", "ai writing", "ai coding", "code generation"
        ],
        "exclude": []
    },
    {
        "name": "🛠️ DevTools - Editors & IDE",
        "keywords": [
            "vim", "neovim", "nvim", "emacs", "vscode", "intellij",
            "editor", "ide ", "plugin", "extension", "theme",
            "dotfiles", "configuration", "setup", "brewfile",
            "lazyvim", "spacevim", "doom emacs", "spacemacs",
            "helix", "zed", "fleet", "cursor ide"
        ],
        "exclude": ["video editor", "audio editor", "image editor"]
    },
    {
        "name": "🛠️ DevTools - Terminal & CLI",
        "keywords": [
            "terminal", "tui", "text user interface", "command line",
            "cli ", "cli tool", "shell", "bash", "zsh", "fish",
            "prompt", "starship", "powerline", "oh-my-zsh",
            "tmux", "zellij", "screen", "repl", "console",
            "file manager", "finder alternative", "system monitor",
            "ripgrep", "grep", "recursively searches", "search directories",
            "fast grep", "ag ", "the_silver_searcher", "ack",
            "http server", "file server", "static file server", "dufs"
        ],
        "exclude": ["payment terminal", "bank terminal", "llm prompt"]
    },
    {
        "name": "🛠️ DevTools - Build & Deploy",
        "keywords": [
            "build tool", "build system", "makefile", "cmake", "bazel",
            "ninja", "meson", "gradle", "maven", "ant",
            "ci/cd", "continuous integration", "github action",
            "gitlab ci", "jenkins", "drone", "argo", "tekton",
            "deploy", "deployment", "release", "packaging",
            "distro", "appimage", "flatpak", "snap", "homebrew",
            "commitlint", "conventional changelog", "semantic release",
            "lint", "code style", "formatter", "prettier", "eslint",
            "diagnostic tool", "profiler", "arthas", "java diagnostic",
            "spec-driven", "spec kit", "sourcetrail", "code explorer",
            "logging framework", "logger", "pino", "winston", "log4j",
            "structured logging"
        ],
        "exclude": []
    },
    {
        "name": "🗄️ Data & Storage",
        "keywords": [
            "database", "db ", "sql", "nosql", "redis", "postgres",
            "sqlite", "mysql", "mongodb", "cassandra", "dynamodb",
            "clickhouse", "elasticsearch", "opensearch", "meilisearch",
            "neo4j", "dgraph", "cockroachdb", "tidb", "citus",
            "cache", "caching", "kv store", "object storage",
            "data warehouse", "olap", "etl", "data pipeline",
            "apache spark", "apache flink", "databricks", "dbt",
            "etcd", "distributed reliable key-value", "consul", "zookeeper",
            "druid", "pinot", "kylin", "presto", "trino"
        ],
        "exclude": []
    },
    {
        "name": "☁️ Cloud Native & Infra",
        "keywords": [
            "docker", "kubernetes", "k8s", "container", "helm",
            "istio", "linkerd", "service mesh", "cloud native",
            "serverless", "lambda", "fargate", "knative",
            "terraform", "pulumi", "ansible", "puppet", "chef",
            "vagrant", "packer", "nomad", "consul", "vault",
            "prometheus", "grafana", "observability", "monitoring",
            "logging", "tracing", "opentelemetry", "jaeger",
            "nginx", "traefik", "envoy", "haproxy", "cdn",
            "proxy", "vpn", "tunnel", "reverse proxy",
            "spring cloud alibaba", "microservice", "resilience4j",
            "fault tolerance", "circuit breaker"
        ],
        "exclude": []
    },
    {
        "name": "📚 Learning & Reference",
        "keywords": [
            "awesome", "curated list", "resources", "collection",
            "cheatsheet", "cheat sheet", "handbook", "cookbook",
            "roadmap", "path", "guide to", "primer",
            "tutorial", "course", "learn ", "learning",
            "interview", "leetcode", "system design",
            "coding interview", "behavioral interview",
            "algorithm", "data structure", "competitive programming",
            "book", "reading list", "papers", "research",
            "分享 github", "分享github", "github 上有趣", "hello",
            "flight rules", "examples", "那些事", "hiring without",
            "companies that don't have", "entry-level", "beginner",
            "getting started", "入门", "examples",
            "ddia", "data-intensive", "the art of programming",
            "apachecn", "algorithm-zh"
        ],
        "exclude": ["style guide", "guide to contribute"]
    },
    {
        "name": "📝 Docs & Note-taking",
        "keywords": [
            "note", "note-taking", "notebook", "wiki", "knowledge base",
            "documentation", "docs", "obsidian", "notion", "logseq",
            "trilium", "joplin", "standard notes", "bear",
            "markdown", "static site generator", "documentation site",
            "docusaurus", "vitepress", "mkdocs", "gitbook",
            "blog", "cms", "content management",
            "rime", "input method", "ime ", "keyboard", "typing",
            "supermemory", "second brain", "personal knowledge"
        ],
        "exclude": []
    },
    {
        "name": "🎨 Visualization",
        "keywords": [
            "visualization", "chart", "graph", "plot", "diagram",
            "draw", "canvas", "svg", "d3", "matplotlib",
            "plotly", "bokeh", "altair", "vega", "observable",
            "three.js", "webgl", "opengl", "vulkan",
            "rendering", "shader", "graphics"
        ],
        "exclude": ["data visualization"]
    },
    {
        "name": "🧠 ML Frameworks",
        "keywords": [
            "pytorch", "tensorflow", "jax", "mxnet", "paddle", "paddlepaddle",
            "deep learning framework", "neural network framework",
            "machine learning framework", "ml framework",
            "tensor", "autograd", "backpropagation",
            "ray is", "ray project", "colossalai", "flash attention",
            "deepspeed", "fairseq", "allennlp", "caffe", "cntk",
            "recommender system", "recommendation system", "recommenders",
            "kohya", "animatediff", "open_clip",
            "flash-attention", "starcoder", "bigcode"
        ],
        "exclude": []
    },
    {
        "name": "👁️ Computer Vision",
        "keywords": [
            "computer vision", "opencv", "image processing",
            "face detection", "face recognition", "object detection",
            "ocr", "optical character recognition", "tesseract",
            "yolo", "ssd", "rcnn", "detr", "segmentation",
            "diffusion model", "stable diffusion", "controlnet",
            "image generation", "text to image", "midjourney",
            "insightface", "facefusion", "deepfake"
        ],
        "exclude": []
    },
    {
        "name": "🔧 System & Kernel",
        "keywords": [
            "operating system", "os kernel", "linux kernel", "kernel",
            "system call", "syscall", "memory management", "process scheduler",
            "bootloader", "firmware", "bios", "uefi",
            "virtual machine", "hypervisor", "kvm", "qemu", "xen",
            "wine", "compatibility layer", "emulator"
        ],
        "exclude": ["game emulator"]
    },
    {
        "name": "🌐 Networking",
        "keywords": [
            "network", "networking", "tcp/ip", "socket", "async io",
            "event-driven", "nio", "netty", "async runtime",
            "tokio", "async-std", "mio", "libuv",
            "api gateway", "kong", "zuul", "spring cloud gateway",
            "load balancer", "service discovery", "rpc framework",
            "grpc", "thrift", "dubbo", "brpc",
            "webrtc", "quic", "quiche", "http/3", "http3",
            "pion", "webtransport", "real-time communication"
        ],
        "exclude": []
    },
    {
        "name": "📡 VPN & Proxy",
        "keywords": [
            "vpn", "proxy", "shadowsocks", "v2ray", "trojan", "wireguard",
            "openvpn", "softether", "lantern", "brook",
            "tunnel", "port forwarding", "reverse proxy",
            "clash", "surge", "quantumult", "sing-box",
            "科学上网", "翻墙", "梯子", "节点",
            "subconverter", "subscription", "gfwlist", "gfw"
        ],
        "exclude": []
    },
    {
        "name": "⏱️ Task Queue & Scheduler",
        "keywords": [
            "task queue", "job scheduler", "cron", "scheduled job",
            "celery", "rq", "huey", "bull", "agenda",
            "xxl-job", "elastic-job", "powerjob", "quartz",
            "airflow", "prefect", "dagster", "luigi",
            "workflow engine", "orchestration", "pipeline",
            "temporal", "cadence", "camunda", "zeebe"
        ],
        "exclude": ["data pipeline"]
    },
    {
        "name": "💾 Backup & Storage",
        "keywords": [
            "backup", "restore", "snapshot", "incremental backup",
            "restic", "borg", "duplicati", "rsync", "rclone",
            "file sync", "cloud sync", "dropbox alternative",
            "nas", "network attached storage", "synology",
            "s3", "minio", "object storage", "ceph"
        ],
        "exclude": []
    },
    {
        "name": "📊 Data Processing",
        "keywords": [
            "dataframe", "pandas", "polars", "datafusion", "duckdb",
            "spark", "flink", "beam", "dataflow",
            "etl", "elt", "data pipeline", "data engineering",
            "stream processing", "batch processing",
            "big data", "mapreduce", "hive", "presto", "trino",
            "datax", "easyexcel", "excel", "spreadsheet",
            "json parser", "json library", "json serializer", "sonic",
            "data sync", "data transfer", "data migration"
        ],
        "exclude": []
    },
    {
        "name": "📈 Benchmarking & Testing",
        "keywords": [
            "benchmark", "performance test", "load test", "stress test",
            "wrk", "ab ", "locust", "k6", "jmeter", "artillery",
            "profiling", "profiler", "memory profiler", "cpu profiler",
            "tracing", "flamegraph", "perf"
        ],
        "exclude": []
    },
    {
        "name": "🎵 Media & Audio",
        "keywords": [
            "music", "audio", "video", "media player", "mpv", "vlc",
            "ffmpeg", "youtube-dl", "yt-dlp", "spotify",
            "netease cloud music", "qq music", "bilibili",
            "subtitle", "transcode", "codec", "h264", "h265", "av1"
        ],
        "exclude": []
    },
    {
        "name": "💻 Remote Desktop",
        "keywords": [
            "remote desktop", "vnc", "rdp", "teamviewer alternative",
            "rustdesk", "anydesk", "nomachine", "x2go",
            "ssh client", "terminal emulator", "putty alternative"
        ],
        "exclude": []
    },
    {
        "name": "🏢 Enterprise & Admin",
        "keywords": [
            "erp", "crm", "cms", "admin panel", "dashboard",
            "hr system", "oa system", "ecommerce", "shop",
            "forum", "community", "wiki system", "knowledge management",
            "project management", "issue tracker", "ticketing"
        ],
        "exclude": []
    },
    {
        "name": "🔒 Security",
        "keywords": [
            "security", "pentest", "penetration test", "vulnerability",
            "exploit", "ctf", "capture the flag", "reverse engineering",
            "forensic", "malware", "ransomware", "phishing",
            "osint", "reconnaissance", "bug bounty", "hacker",
            "cryptography", "encryption", "cipher", "hash",
            "owasp", "burp suite", "metasploit", "nmap", "nessus",
            "teleport", "access plane", "privileged access",
            "openssl", "tls", "ssl", "certificate"
        ],
        "exclude": ["job security"]
    },
    {
        "name": "🌐 Web & API",
        "keywords": [
            "web framework", "web server", "http server", "rest api",
            "graphql", "grpc", "websocket", "socket.io",
            "fastapi", "flask", "django", "express", "nestjs",
            "spring boot", "rails", "laravel", "phoenix",
            "next.js", "nuxt", "sveltekit", "remix", "astro",
            "react", "vue", "svelte", "angular", "solid",
            "tailwind", "bootstrap", "mui", "shadcn",
            "authentication", "oauth", "jwt", "sso", "auth",
            "css framework", "ui component", "pdf.js", "pdf reader",
            "frontend", "front-end", "html", "css", "bulma",
            "sanic", "web application", "webapp",
            "vercel", "netlify", "deploy platform", "hosting platform",
            "responsive", "responsive design", "responsive testing",
            "phone number", "libphonenumber", "validation library",
            "katex", "math rendering", "latex", "mathjax",
            "starlette", "asgi", "wsgi", "effect-ts", "effect ts"
        ],
        "exclude": []
    },
    {
        "name": "💻 Programming Languages",
        "keywords": [
            "programming language", "language implementation",
            "compiler", "interpreter", "jit", "bytecode", "vm ",
            "julia programming", "kotlin programming", "rust programming",
            "go programming", "python programming", "ruby programming",
            "programming language.", "the .* programming language",
            "openjdk", "jdk", "jvm", "llvm", "gcc", "clang",
            "typescript compiler", "babel", "swc", "esbuild",
            "language specification", "language design",
            "syntax", "parser", "lexer", "grammar"
        ],
        "exclude": ["natural language", "query language"]
    },
    {
        "name": "📱 Mobile & Desktop",
        "keywords": [
            "react native", "flutter", "ios", "android", "swift",
            "kotlin multiplatform", "capacitor", "ionic",
            "electron", "tauri", "flutter desktop", "qt",
            "gtk", "wxwidgets", " Avalonia", "maui",
            "cross platform", "multi platform", "pwa",
            "dokit", "mobile development", "mobile debug",
            "open im", "instant messaging", "im sdk", "chat sdk"
        ],
        "exclude": []
    },
    {
        "name": "🔌 Embedded & IoT",
        "keywords": [
            "embedded", "iot", "internet of things", "hardware",
            "raspberry pi", "arduino", "esp32", "esp8266",
            "stm32", "microcontroller", "mcu", "firmware",
            "bare metal", "rtos", "zephyr", "freertos",
            "platformio", "home assistant", "home automation",
            "smart home", "wearable", "sensor"
        ],
        "exclude": []
    },
    {
        "name": "🎮 Games",
        "keywords": [
            "game engine", "game framework", "game development",
            "emulator", "retro", "arcade", "console emulator",
            "chess", "go game", "puzzle", "roguelike",
            "minecraft", " factorio", "terraria",
            "godot", "unity", "unreal", "bevy", "raylib",
            "sdl", "sfml", "love2d"
        ],
        "exclude": ["game theory"]
    },
    {
        "name": "🤖 Robotics",
        "keywords": [
            "robotics", "robot", "drone", "uav", "autonomous vehicle",
            "self-driving", "ros", "ros2", "gazebo",
            "slam", "computer vision", "opencv", "yolo",
            "nvidia jetson", "raspberry pi robot"
        ],
        "exclude": []
    },
]

# 项目名称到分类的硬编码映射（处理特殊项目）
PROJECT_NAME_MAPPING = {
    "Dao-AILab/flash-attention": "🧠 ML Frameworks",
    "julycoding/The-Art-Of-Programming-By-July-2nd": "📚 Learning & Reference",
    "dianping/cat": "☁️ Cloud Native & Infra",
    "openimsdk/open-im-server": "📱 Mobile & Desktop",
    "thumbor/thumbor": "🌐 Web & API",
    "flowable/flowable-engine": "⏱️ Task Queue & Scheduler",
    "spring-projects/spring-ai": "🤖 AI Agents",
    "apple/ml-ferret": "👁️ Computer Vision",
    "aeron-io/aeron": "🌐 Networking",
    "alibaba/otter": "📊 Data Processing",
    "deep-floyd/IF": "👁️ Computer Vision",
    "zai-org/GLM-130B": "🧠 LLM & Inference",
    "agronholm/apscheduler": "⏱️ Task Queue & Scheduler",
    "jepsen-io/jepsen": "🗄️ Data & Storage",
    "civitai/civitai": "👁️ Computer Vision",
    "detekt/detekt": "🛠️ DevTools - Build & Deploy",
    "vespa-engine/vespa": "🗄️ Data & Storage",
    "Meituan-Dianping/Leaf": "🗄️ Data & Storage",
    "axboe/fio": "📈 Benchmarking & Testing",
    "google/google-java-format": "🛠️ DevTools - Build & Deploy",
    "vavr-io/vavr": "💻 Programming Languages",
    "996icu/996.ICU": "🔬 Experiments",
    "The-Run-Philosophy-Organization/run": "🔬 Experiments",
    "programthink/zhao": "🔬 Experiments",
    "evil-huawei/evil-huawei": "🔬 Experiments",
    "qarmin/czkawka": "🛠️ DevTools - Terminal & CLI",
    "Javen205/IJPay": "📱 Mobile & Desktop",
    "maemual/raft-zh_cn": "📚 Learning & Reference",
    "apache/incubator-kie-drools": "🏢 Enterprise & Admin",
    "apache/nifi": "📊 Data Processing",
    "image-rs/image": "👁️ Computer Vision",
    "changmingxie/tcc-transaction": "🗄️ Data & Storage",
    "google/seesaw": "🌐 Networking",
    "baidu/uid-generator": "🗄️ Data & Storage",
    "goto456/stopwords": "📊 Data Processing",
    "diffplug/spotless": "🛠️ DevTools - Build & Deploy",
    "j-easy/easy-rules": "🏢 Enterprise & Admin",
    "harvester/harvester": "☁️ Cloud Native & Infra",
    "Bing-su/adetailer": "👁️ Computer Vision",
    "chewiebug/GCViewer": "🛠️ DevTools - Build & Deploy",
    "luosiallen/latent-consistency-model": "👁️ Computer Vision",
    "dromara/hmily": "🗄️ Data & Storage",
    "IDEA-CCNL/Fengshenbang-LM": "🧠 LLM & Inference",
    "qunarcorp/bistoury": "🛠️ DevTools - Build & Deploy",
    "baidu/lac": "📊 Data Processing",
    "JCTools/JCTools": "💻 Programming Languages",
    "TencentARC/T2I-Adapter": "👁️ Computer Vision",
    "OpenHFT/Chronicle-Queue": "🗄️ Data & Storage",
    "TNG/ArchUnit": "🛠️ DevTools - Build & Deploy",
    "hnes/libaco": "🔧 System & Kernel",
    "google/ksp": "🛠️ DevTools - Build & Deploy",
    "Miksus/rocketry": "⏱️ Task Queue & Scheduler",
    "PixArt-alpha/PixArt-alpha": "👁️ Computer Vision",
    "koderover/zadig": "🛠️ DevTools - Build & Deploy",
    "yitter/IdGenerator": "🗄️ Data & Storage",
    "git-chglog/git-chglog": "🛠️ DevTools - Build & Deploy",
    "yanyiwu/cppjieba": "📊 Data Processing",
    "bytedeco/javacpp-presets": "💻 Programming Languages",
    "adefossez/demucs": "🎵 Media & Audio",
    "http4k/http4k": "🌐 Web & API",
    "oblac/jodd": "🌐 Web & API",
    "JetBrains/skija": "👁️ Computer Vision",
    "mattn/goreman": "🛠️ DevTools - Terminal & CLI",
    "confluentinc/schema-registry": "🗄️ Data & Storage",
    "shenweichen/DeepMatch": "🧠 ML Frameworks",
    "didi/sharingan": "🛠️ DevTools - Build & Deploy",
    "QNJR-GROUP/EasyTransaction": "🗄️ Data & Storage",
    "apache/rocketmq-spring": "☁️ Cloud Native & Infra",
    "sohutv/mqcloud": "☁️ Cloud Native & Infra",
    "material-foundation/material-color-utilities": "🌐 Web & API",
    "DozerMapper/dozer": "📊 Data Processing",
    "Tencent/TubeMQ": "☁️ Cloud Native & Infra",
    "IBM/fp-go": "💻 Programming Languages",
    "cjolowicz/cookiecutter-hypermodern-python": "🛠️ DevTools - Build & Deploy",
    "dromara/Jpom": "🛠️ DevTools - Build & Deploy",
    "apache/kudu": "🗄️ Data & Storage",
    "wellsjo/JSON-Splora": "🛠️ DevTools - Terminal & CLI",
    "jbangdev/jbang": "🛠️ DevTools - Build & Deploy",
    "strob/gentle": "🎵 Media & Audio",
    "apache/inlong": "📊 Data Processing",
    "apache/ratis": "🗄️ Data & Storage",
    "googleapis/google-http-java-client": "🌐 Web & API",
    "aio-libs/aiokafka": "📊 Data Processing",
    "shekhargulati/strman-java": "💻 Programming Languages",
    "SeanLee97/xmnlp": "📊 Data Processing",
    "didi/turbo": "🛠️ DevTools - Build & Deploy",
    "c4urself/bump2version": "🛠️ DevTools - Build & Deploy",
    "hoisie/mustache": "🌐 Web & API",
    "jspecify/jspecify": "💻 Programming Languages",
    "ai-dynamo/nixl": "🧠 ML Frameworks",
    "RupertAvery/DiffusionToolkit": "👁️ Computer Vision",
    "zalando/nakadi": "🗄️ Data & Storage",
    "froghui/yolanda": "📱 Mobile & Desktop",
    "zeroturnaround/zt-exec": "🛠️ DevTools - Terminal & CLI",
    "IrisRainbowNeko/HCP-Diffusion": "👁️ Computer Vision",
    "chatty/chatty": "🎵 Media & Audio",
    "line/kotlin-jdsl": "🗄️ Data & Storage",
    "zai-org/GLM-ASR": "🧠 LLM & Inference",
    "bytedance/ImageDream": "👁️ Computer Vision",
    "smfrpc/smf": "🌐 Networking",
    "TencentCloud/tencentcloud-sdk-python": "🌐 Web & API",
    "TencentCloud/tencentcloud-sdk-java": "🌐 Web & API",
    "kubewharf/godel-scheduler": "☁️ Cloud Native & Infra",
    "Meituan-Dianping/octo-rpc": "🌐 Networking",
    "nivance/image-similarity": "👁️ Computer Vision",
    "segmind/distill-sd": "👁️ Computer Vision",
    "shabbywu/Battle-Brothers-CN": "🎮 Games",
    "jshachm/pi-rs": "🔧 System & Kernel",
    "TEN-framework/ten-turn-detection": "🤖 AI Agents",
    "openlookeng/hetu-core": "🗄️ Data & Storage",
    "arkcontrol/arkcontrol": "🗄️ Data & Storage",
    "zhaozhiyong19890102/Recommender-System": "🧠 ML Frameworks",
    "icoz69/StyleAvatar3D": "👁️ Computer Vision",
    "confluentinc/confluent-kafka-python": "📊 Data Processing",
    "LatencyUtils/LatencyUtils": "📈 Benchmarking & Testing",
    "Beh01der/EasyFlow": "🛠️ DevTools - Build & Deploy",
    "airbnb/SpinalTap": "🗄️ Data & Storage",
    "alibaba/proxima": "📊 RAG & Knowledge",
    "Aryagm/dflash-mlx": "👁️ Computer Vision",
    "mybatis-mapper/mapper": "🗄️ Data & Storage",
    "langchain4j/langchain4j-spring": "🤖 AI Agents",
    "hexops/fastfilter": "🗄️ Data & Storage",
    "alturkovic/distributed-lock": "🗄️ Data & Storage",
    "tobran/GALIP": "👁️ Computer Vision",
    "CVPR2023": "👁️ Computer Vision",
    "myui/btree4j": "🗄️ Data & Storage",
    "querycatai/jaison": "🤖 AI Agents",
    "taoofagi/easegen-admin": "🤖 AI Agents",
    "360digitech/chronus": "⏱️ Task Queue & Scheduler",
    "seruva19/kubin": "👁️ Computer Vision",
    "xpbob/CrashAnalysis": "🛠️ DevTools - Build & Deploy",
    "apioo/typeschema": "🌐 Web & API",
    "mixedbread-ai/batched": "📊 Data Processing",
    "YongyuG/rnnoise_16k": "🎵 Media & Audio",
    "toomanyopenfiles/jmxmon": "🛠️ DevTools - Build & Deploy",
    "xmolecules/jmolecules-integrations": "💻 Programming Languages",
    "aliyun/alibabacloud-java-sdk": "🌐 Web & API",
    "scylladb/scylla-cdc-source-connector": "🗄️ Data & Storage",
    "LableOrg/java-uniqueid": "🗄️ Data & Storage",
    "kcpeppe/regions": "🔧 System & Kernel",
    "jlmelville/rcpphnsw": "📊 RAG & Knowledge",
    "bkdevops-projects/devops-framework": "🛠️ DevTools - Build & Deploy",
    "scylladb/scylla-cdc-java": "🗄️ Data & Storage",
    "ExponentiAI/StyleMe": "👁️ Computer Vision",
    "LJWLgl/life-helper": "🔬 Experiments",
    "eduosi/district": "🌐 Web & API",
}

def classify_project(project):
    """为单个项目分类，返回最匹配的类别列表"""
    # 先检查硬编码映射
    if project['name'] in PROJECT_NAME_MAPPING:
        return [PROJECT_NAME_MAPPING[project['name']]]

    text = f"{project['name']} {project.get('description', '')} {project.get('language', '')}".lower()
    matches = []

    for cat in CATEGORIES:
        score = 0
        # 关键词匹配
        for kw in cat["keywords"]:
            if kw.lower() in text:
                # 名称匹配权重更高
                if kw.lower() in project['name'].lower():
                    score += 3
                else:
                    score += 1

        # 排除关键词检查
        for ex in cat.get("exclude", []):
            if ex.lower() in text:
                score -= 2

        if score > 0:
            matches.append((cat["name"], score))

    # 按分数排序
    matches.sort(key=lambda x: x[1], reverse=True)

    # 返回前 2 个最佳匹配
    if matches:
        return [m[0] for m in matches[:2]]
    else:
        return ["🔬 Experiments"]

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "my-stars.jsonl"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "stars-classified.md"

    projects = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                projects.append(json.loads(line))

    print(f"读取了 {len(projects)} 个项目")

    # 分类
    classified = []
    for proj in projects:
        categories = classify_project(proj)
        classified.append({
            "name": proj["name"],
            "description": proj.get("description", "")[:80] + "..." if len(proj.get("description", "")) > 80 else proj.get("description", ""),
            "language": proj.get("language", "N/A"),
            "stars": proj.get("stars", 0),
            "categories": categories,
            "url": proj.get("url", "")
        })

    # 按分类统计
    cat_stats = {}
    for c in classified:
        for cat in c["categories"]:
            cat_stats[cat] = cat_stats.get(cat, 0) + 1

    # 生成 Markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GitHub Stars 项目分类清单\n\n")
        f.write(f"共分析 {len(projects)} 个 star 项目\n\n")

        # 分类统计
        f.write("## 分类统计\n\n")
        f.write("| 分类 | 项目数 |\n")
        f.write("|------|--------|\n")
        for cat_name, count in sorted(cat_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {cat_name} | {count} |\n")
        f.write("\n")

        # 详细列表
        f.write("## 详细分类列表\n\n")

        # 按分类分组输出
        sorted_cats = sorted(cat_stats.keys(), key=lambda x: cat_stats[x], reverse=True)

        for cat_name in sorted_cats:
            f.write(f"### {cat_name}\n\n")
            f.write("| 仓库 | 语言 | Stars | 描述 |\n")
            f.write("|------|------|-------|------|\n")

            cat_projects = [c for c in classified if cat_name in c["categories"]]
            # 按 star 数排序
            cat_projects.sort(key=lambda x: x["stars"], reverse=True)

            for p in cat_projects:  # 显示全部项目
                desc = p["description"].replace("|", "\\|").replace("\n", " ")
                f.write(f"| [{p['name']}]({p['url']}) | {p['language']} | {p['stars']:,} | {desc} |\n")
            f.write("\n")

    print(f"分类完成！结果保存到 {output_file}")
    print(f"\n分类统计：")
    for cat_name, count in sorted(cat_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat_name}: {count}")

if __name__ == "__main__":
    main()
