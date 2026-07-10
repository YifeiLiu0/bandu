# bandu

MVP0 for an AI Reading Agent.

This version intentionally does **not** build a full app. It only tests the core reading experience on one chapter:

- Book: Agentic Design Patterns
- Chapter: `Chapter 1: Prompt Chaining / 第 1 章：提示词链`
- Source: https://github.com/xindoo/agentic-design-patterns/tree/effb52f1730913be650a04e5ffb251c093096894/bilingual

The goal is to generate a local reading pack:

```text
Chapter 1
└── Section
    └── Episode
        └── Beat
            ├── original Markdown
            └── light, hook-driven, slightly funny reading commentary
```

The commentary is not a summary. It should feel more like a relaxed reading companion:

- 抛一个阅读钩子
- 用轻微吐槽降低理解压力
- 用产品/工程视角把概念落地
- 最后给一句“你要抓住的一句话”

## Scripts

### 1. Fetch Chapter 1

```bash
npm run chapter1:fetch
```

This downloads the fixed Chapter 1 Markdown into:

```text
content/bilingual/Chapter 1_ Prompt Chaining.md
```

### 2. Inspect structure only

```bash
npm run chapter1:structure
```

This generates section / episode / beat cutting without calling an AI model.

Outputs:

```text
data/chapter1-reading-pack.json
data/chapter1-reading-pack.preview.md
```

### 3. Build the AI reading pack

Set an Anthropic-compatible API key first:

```bash
export ANTHROPIC_API_KEY="..."
```

Optional:

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export ANTHROPIC_MODEL="claude-sonnet-4-6"
```

Then run:

```bash
npm run chapter1:build
```

The script writes:

```text
data/chapter1-reading-pack.json
data/chapter1-reading-pack.preview.md
```

The Markdown preview is the fastest way to judge the MVP0 experience.

## Cost controls

You can generate only the first few episodes while tuning prompts:

```bash
node scripts/build-chapter1-pack.mjs --limit-episodes=3
```

## What to inspect

Open:

```text
data/chapter1-reading-pack.preview.md
```

Randomly inspect several beats. The key question is:

> Does the commentary make the original text feel more interesting, easier to enter, and worth continuing?

Good commentary should sound closer to:

```text
单 prompt 像什么？
像你对一个实习生说：今天顺便把公司战略、产品设计、技术架构、用户访谈和融资 BP 都搞了。
实习生表面：好的老板。
内心：我先编个像样的。

你要抓住的一句话：
Prompt Chaining 解决的不是“让模型更聪明”，而是“让模型工作更可控”。
```

Bad commentary sounds like:

```text
本段主要讲的是 Prompt Chaining 的定义和作用。
```
