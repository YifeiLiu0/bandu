import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const SOURCE_COMMIT = 'effb52f1730913be650a04e5ffb251c093096894';
const SOURCE_FILE = path.join(process.cwd(), 'content', 'bilingual', 'Chapter 1_ Prompt Chaining.md');
const OUTPUT_JSON = path.join(process.cwd(), 'data', 'chapter1-reading-pack.json');
const OUTPUT_PREVIEW = path.join(process.cwd(), 'data', 'chapter1-reading-pack.preview.md');
const DEFAULT_MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-6';
const ANTHROPIC_BASE_URL = (process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com').replace(/\/$/, '');
const STRUCTURE_ONLY = process.argv.includes('--structure-only');
const LIMIT_EPISODES = getNumberArg('--limit-episodes');

const COMMENTARY_TYPES = [
  '一句话先讲明白型',
  '阅读钩子型',
  '吐槽理解型',
  '产品经理视角型',
  '工程师视角型',
  '场景/冲突型',
  '降挫败型',
  '关键句人话型',
];

function getNumberArg(name) {
  const direct = process.argv.find((arg) => arg.startsWith(`${name}=`));
  if (direct) return Number(direct.slice(name.length + 1));
  const index = process.argv.indexOf(name);
  if (index !== -1 && process.argv[index + 1]) return Number(process.argv[index + 1]);
  return undefined;
}

function slugCounter(prefix, index) {
  return `${prefix}_${String(index).padStart(3, '0')}`;
}

function stripMarkdownLabel(value) {
  return value
    .replace(/^#+\s*/, '')
    .replace(/^[-*+]\s+/, '')
    .replace(/^\d+\\?[.)、]\s*/, '')
    .replace(/^\*\*/, '')
    .replace(/\*\*.*$/s, '')
    .replace(/[：:].*$/s, '')
    .replace(/\\_/g, '_')
    .trim();
}

function countCjk(value) {
  return (value.match(/[㐀-鿿]/g) || []).length;
}

function visibleLength(value) {
  return value.replace(/```[\s\S]*?```/g, (match) => ' '.repeat(Math.min(match.length, 500))).length;
}

function isLikelyChinese(value) {
  return countCjk(value) >= 2;
}

function splitIntoBlocks(markdown) {
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  const blocks = [];
  let buffer = [];
  let codeFence = null;

  const flush = () => {
    if (!buffer.length) return;
    const markdownText = buffer.join('\n').trim();
    if (markdownText) blocks.push(classifyBlock(markdownText));
    buffer = [];
  };

  for (const line of lines) {
    const fenceMatch = line.match(/^\s*(```|~~~)/);
    if (fenceMatch) {
      if (!codeFence) {
        flush();
        codeFence = fenceMatch[1];
        buffer.push(line);
        continue;
      }

      buffer.push(line);
      if (fenceMatch[1] === codeFence) {
        blocks.push({ type: 'code', markdown: buffer.join('\n').trim() });
        buffer = [];
        codeFence = null;
      }
      continue;
    }

    if (codeFence) {
      buffer.push(line);
      continue;
    }

    if (!line.trim()) {
      flush();
      continue;
    }

    const isHeading = /^#{1,6}\s+/.test(line);
    const isList = /^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(line);
    const isQuote = /^\s*>\s?/.test(line);
    const isReference = /^\[[^\]]+\]:\s+/.test(line);
    const startsNewBlock = isHeading || isList || isQuote || isReference;

    if (startsNewBlock && buffer.length && !sameContinuationType(buffer[0], line)) {
      flush();
    }

    buffer.push(line);
  }

  flush();
  return blocks;
}

function sameContinuationType(firstLine, nextLine) {
  if (/^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(firstLine) && /^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(nextLine)) return true;
  if (/^\s*>\s?/.test(firstLine) && /^\s*>\s?/.test(nextLine)) return true;
  if (/^\[[^\]]+\]:\s+/.test(firstLine) && /^\[[^\]]+\]:\s+/.test(nextLine)) return true;
  return false;
}

function classifyBlock(markdown) {
  const firstLine = markdown.split('\n')[0];
  const heading = firstLine.match(/^(#{1,6})\s+(.+)$/);
  if (heading) {
    return {
      type: 'heading',
      level: heading[1].length,
      title: heading[2].trim(),
      markdown,
    };
  }
  if (/^\s*(```|~~~)/.test(firstLine)) return { type: 'code', markdown };
  if (/^\s*(?:[-*+]\s+|\d+[.)]\s+)/.test(firstLine)) return { type: 'list', markdown };
  if (/^\s*>\s?/.test(firstLine)) return { type: 'quote', markdown };
  if (/^!\[[^\]]*\]\[[^\]]*\]/.test(firstLine) || /^!\[[^\]]*\]\([^)]*\)/.test(firstLine)) return { type: 'image', markdown };
  if (/^\[[^\]]+\]:\s+/.test(firstLine)) return { type: 'reference', markdown };
  return { type: 'paragraph', markdown };
}

function splitChapterIntoSections(blocks) {
  const h1Titles = blocks.filter((block) => block.type === 'heading' && block.level === 1).map((block) => block.title);
  const chapterTitle = h1Titles.length >= 2 ? `${h1Titles[0]} / ${h1Titles[1]}` : h1Titles[0] || 'Chapter 1: Prompt Chaining';
  const contentBlocks = blocks.filter((block) => !(block.type === 'heading' && block.level === 1));
  const sections = [];
  let index = 0;
  let sectionCounter = 1;

  while (index < contentBlocks.length) {
    while (index < contentBlocks.length && !(contentBlocks[index].type === 'heading' && contentBlocks[index].level === 2)) index += 1;
    if (index >= contentBlocks.length) break;

    const titleParts = [contentBlocks[index].title];
    index += 1;
    if (contentBlocks[index]?.type === 'heading' && contentBlocks[index].level === 2) {
      titleParts.push(contentBlocks[index].title);
      index += 1;
    }

    const body = [];
    while (index < contentBlocks.length && !(contentBlocks[index].type === 'heading' && contentBlocks[index].level === 2)) {
      body.push(contentBlocks[index]);
      index += 1;
    }

    const title = titleParts.join(' / ');
    sections.push({
      id: slugCounter('section', sectionCounter++),
      title,
      blocks: body,
    });
  }

  return { chapterTitle, sections };
}

function isStrongLead(block) {
  if (!['paragraph', 'list'].includes(block.type)) return false;
  const firstLine = block.markdown.split('\n')[0].trim();
  if (/^\*\*\d+\\?[.)、]/.test(firstLine)) return true;
  if (/^\*\*[^*\n]{3,100}[：:]/.test(firstLine)) return true;
  return false;
}

function extractStrongLeadTitle(block) {
  const firstLine = block.markdown.split('\n')[0].trim();
  const bold = firstLine.match(/^\*\*(.+?)\*\*/);
  if (!bold) return '';
  return stripMarkdownLabel(bold[1]);
}

function findChineseLead(blocks) {
  for (const block of blocks.slice(0, 4)) {
    if (!isStrongLead(block)) continue;
    const title = extractStrongLeadTitle(block);
    if (isLikelyChinese(title)) return title;
  }
  return '';
}

function splitSectionsIntoEpisodes(sections) {
  let episodeCounter = 1;
  return sections.map((section) => {
    const groups = [];
    let current = [];

    for (const block of section.blocks) {
      const strongLead = isStrongLead(block);
      const strongLeadIsChinese = strongLead && isLikelyChinese(extractStrongLeadTitle(block));
      const startsEpisode = strongLead && current.length > 0 && !strongLeadIsChinese;
      if (startsEpisode) {
        groups.push(current);
        current = [];
      }
      current.push(block);
    }
    if (current.length) groups.push(current);

    const episodes = groups.flatMap((group) => splitLongGroup(group, section.title)).map((blocksForEpisode) => {
      const firstLead = blocksForEpisode.find(isStrongLead);
      const englishTitle = firstLead ? extractStrongLeadTitle(firstLead) : '';
      const chineseTitle = findChineseLead(blocksForEpisode.filter((block) => block !== firstLead));
      const deterministicTitle = buildEpisodeTitle(section.title, englishTitle, chineseTitle, episodeCounter);
      const episode = {
        id: slugCounter('ep', episodeCounter++),
        title: deterministicTitle,
        sourceTitle: [englishTitle, chineseTitle].filter(Boolean).join(' / ') || section.title,
        beats: buildBeats(blocksForEpisode),
      };
      return episode;
    });

    return { ...section, episodes, blocks: undefined };
  });
}

function splitLongGroup(blocks, sectionTitle) {
  const chunks = [];
  let current = [];
  let size = 0;
  const isCodeSection = sectionTitle.includes('Hands-On') || sectionTitle.includes('代码');
  const target = isCodeSection ? 3200 : 4200;
  const hardMax = isCodeSection ? 5200 : 6500;

  for (const block of blocks) {
    const blockSize = visibleLength(block.markdown);
    const shouldSplit = current.length > 0 && size + blockSize > hardMax;
    if (shouldSplit) {
      chunks.push(current);
      current = [];
      size = 0;
    }
    current.push(block);
    size += blockSize;

    if (size >= target && current.length >= 4 && block.type !== 'code') {
      chunks.push(current);
      current = [];
      size = 0;
    }
  }

  if (current.length) chunks.push(current);
  return chunks;
}

function buildEpisodeTitle(sectionTitle, englishTitle, chineseTitle, episodeNumber) {
  const combined = [englishTitle, chineseTitle].filter(Boolean).join(' / ');
  if (combined) return combined;
  const base = sectionTitle.split('/').map((part) => part.trim()).filter(Boolean).slice(0, 2).join(' / ');
  return `${base} · Part ${episodeNumber}`;
}

function buildBeats(blocks) {
  const beats = [];
  let current = [];
  let size = 0;
  const target = 900;
  const hardMax = 1450;

  const push = () => {
    if (!current.length) return;
    beats.push({
      id: slugCounter('beat', beats.length + 1),
      sourceMarkdown: current.map((block) => block.markdown).join('\n\n'),
    });
    current = [];
    size = 0;
  };

  for (const block of blocks) {
    const blockSize = visibleLength(block.markdown);
    const standalone = block.type === 'code' || blockSize > hardMax;

    if (standalone) {
      push();
      current.push(block);
      size = blockSize;
      push();
      continue;
    }

    if (current.length && size + blockSize > hardMax) push();
    current.push(block);
    size += blockSize;

    const hasBilingualPair = current.length >= 2 && isLikelyChinese(current[current.length - 1].markdown);
    if (size >= target && hasBilingualPair) push();
  }

  push();

  return beats.map((beat, index) => ({
    ...beat,
    id: slugCounter('beat', index + 1),
  }));
}

function flattenEpisodes(sections) {
  return sections.flatMap((section) => section.episodes.map((episode) => ({ section, episode })));
}

async function generateCommentaryForEpisode({ section, episode }, episodeIndex, totalEpisodes) {
  if (STRUCTURE_ONLY) {
    return {
      ...episode,
      beats: episode.beats.map((beat) => ({
        ...beat,
        commentaryType: ['结构预览'],
        commentaryMarkdown: '#### 结构预览\n这里会生成轻松、有钩子、有吐槽感的陪读评论。当前运行使用了 `--structure-only`，所以没有调用模型。',
      })),
    };
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('Missing ANTHROPIC_API_KEY. Set it before running `npm run chapter1:build`, or run `npm run chapter1:structure` to inspect only the cutting result.');
  }

  const prompt = buildCommentaryPrompt({ section, episode, episodeIndex, totalEpisodes });
  const response = await fetch(`${ANTHROPIC_BASE_URL}/v1/messages`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: DEFAULT_MODEL,
      max_tokens: 7000,
      temperature: 0.75,
      system: buildSystemPrompt(),
      messages: [{ role: 'user', content: prompt }],
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Anthropic API error for ${episode.id}: ${response.status} ${response.statusText}\n${body}`);
  }

  const payload = await response.json();
  const text = payload.content?.filter((item) => item.type === 'text').map((item) => item.text).join('\n') || '';
  const parsed = parseJsonFromModel(text);
  const comments = Array.isArray(parsed.comments) ? parsed.comments : parsed;
  if (!Array.isArray(comments)) {
    throw new Error(`Model response for ${episode.id} did not contain a comments array.`);
  }

  const byBeat = new Map(comments.map((comment) => [comment.beatId, comment]));
  return {
    ...episode,
    beats: episode.beats.map((beat) => {
      const comment = byBeat.get(beat.id);
      if (!comment?.commentaryMarkdown) {
        throw new Error(`Model response for ${episode.id} is missing commentary for ${beat.id}.`);
      }
      return {
        ...beat,
        commentaryType: normalizeCommentaryType(comment.commentaryType),
        commentaryMarkdown: String(comment.commentaryMarkdown).trim(),
      };
    }),
  };
}

function buildSystemPrompt() {
  return `你是一本专业书的“陪读导演”，但请记住：你不是老师站在讲台上讲课，你是坐在读者旁边，帮他把一本看起来很硬的书读得有意思。

你的任务不是总结，也不是把内容降智成爽文，而是把原文改造成一种：有钩子、有吐槽、有推进感、能让人继续读下去的陪读体验。

核心风格：
- 像一个聪明、松弛、有产品感的读书搭子。
- 口语化，短句，多换行。
- 少写大段解释，多写“这事像什么”。
- 多用具体场景、小剧场、类比、反差。
- 可以轻微吐槽，但吐槽是为了帮助理解，不是为了讲段子。
- 读起来要像用户给的示例，而不是像咨询报告、教科书、技术白皮书。

必须接近这种语气：

一句话先讲明白
提示词链就是：不要指望一个 prompt 一口气干完复杂任务，而是把任务拆成多步，每一步让模型只做好一件事。

阅读钩子
你先想一个问题：
为什么我们不能直接写一个超级 prompt，让模型一步到位？

这看起来很爽。
但模型很容易变成“全能实习生上头版”：
* 用户需求讲一点；
* 竞品分析编一点；
* 技术架构糊一点；
* 最后输出一篇看似完整但很虚的报告。

吐槽视角
单 prompt 像什么？
像你对一个实习生说：
你今天顺便把公司战略、产品设计、融资 BP、代码架构、用户访谈、竞品研究都搞了。

实习生表面镇定：
好的老板。

内心：
我先编个像样的。

你要抓住的一句话
Prompt chaining 解决的不是“让模型更聪明”，而是“让模型工作更可控”。

强约束：
- 只评论当前 beat，不改写原文。
- 不总结全章，不提前讲后文结论。
- 不写百科式解释。
- 不要用“本段主要讲了”“这里体现了”“从技术层面来看”“综上所述”这种正式腔。
- 少用“复杂任务”“模块化”“结构化”这种抽象词；用了就立刻配一个生活化例子。
- 中文为主，保留必要英文术语。
- 吐槽只吐槽问题、机制或错误用法，不吐槽作者、译者或读者。
- 遇到代码段，先说“先别慌”，解释这段代码在演示什么动作，不要逐行教学。
- 尽量把内容连回用户正在做的 AI Reading Agent：不要写一个万能陪读 prompt，而是设计一条让用户读进去的链。

可选评论类型：${COMMENTARY_TYPES.join('、')}。`;
}

function buildCommentaryPrompt({ section, episode, episodeIndex, totalEpisodes }) {
  const beats = episode.beats.map((beat) => ({
    beatId: beat.id,
    sourceMarkdown: beat.sourceMarkdown,
  }));

  return `请为 Chapter 1 的一个 episode 生成每个 beat 的陪读评论。

全章主题：Chapter 1: Prompt Chaining / 第 1 章：提示词链
当前进度：Episode ${episodeIndex + 1} / ${totalEpisodes}
Section：${section.title}
Episode：${episode.title}

这次最重要的要求：
不要写成“专业导读”。
要写成“轻松陪读稿”。
像一个懂 AI 产品的人坐在旁边，帮读者把这段读得有意思。

每个 beat 输出：
- beatId：必须和输入一致
- commentaryType：从这些类型中选 2-4 个：${COMMENTARY_TYPES.join('、')}
- commentaryMarkdown：Markdown 文本。优先使用这些小标题，但不要死板：
  #### 一句话先讲明白
  #### 阅读钩子
  #### 吐槽视角
  #### 技术理解 / 产品经理视角 / 这事放到你的 Reading Agent 里
  #### 你要抓住的一句话

写法要求：
- 多短句，多换行。
- 可以用列表。
- 可以写小剧场，比如：
  “实习生表面：好的老板。内心：我先编个像样的。”
- 可以使用“先别慌”“你先想一个问题”“这看起来很爽，但……”“单 prompt 像什么？”
- 评论要有轻微节奏感，不要一整块密密麻麻。
- 每个 beat 300-900 中文字。宁可松弛一点，也不要像论文。

特别避免：
- 不要用“本段主要讲了”。
- 不要用“本文/本节/该机制/从技术层面来看/综上所述”这种正式腔。
- 不要把每段都写成四平八稳的解释。
- 不要只替换几个标题，正文仍然很正式。
- 不要机械说明“英文和中文重复”。
- 不要复制原文长句。

你要尽量做到：
读者看完评论后，会觉得：
“哦，原来这段是在讲这个，有点意思，我愿意回去读原文。”

输入 beats：
${JSON.stringify(beats, null, 2)}

只返回 JSON，不要 Markdown 代码围栏。格式如下：
{
  "comments": [
    {
      "beatId": "beat_001",
      "commentaryType": ["阅读钩子型", "吐槽理解型", "关键句人话型"],
      "commentaryMarkdown": "#### 一句话先讲明白\n...\n\n#### 阅读钩子\n...\n\n#### 吐槽视角\n...\n\n#### 你要抓住的一句话\n..."
    }
  ]
}`;
}

function parseJsonFromModel(text) {
  const cleaned = text.trim().replace(/^```(?:json)?\s*/i, '').replace(/```$/i, '').trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    const startObject = cleaned.indexOf('{');
    const startArray = cleaned.indexOf('[');
    const starts = [startObject, startArray].filter((index) => index >= 0);
    const start = Math.min(...starts);
    const endObject = cleaned.lastIndexOf('}');
    const endArray = cleaned.lastIndexOf(']');
    const end = Math.max(endObject, endArray);
    if (start >= 0 && end > start) return JSON.parse(cleaned.slice(start, end + 1));
    throw new Error(`Could not parse model JSON response:\n${text}`);
  }
}

function normalizeCommentaryType(value) {
  if (Array.isArray(value)) return value.map(String).filter(Boolean);
  if (typeof value === 'string') return value.split(/[、,，/]/).map((part) => part.trim()).filter(Boolean);
  return ['未标注'];
}

function buildPreview(pack) {
  const lines = [];
  lines.push(`# ${pack.book.chapter}`);
  lines.push('');
  lines.push(`- Source commit: \`${pack.book.sourceCommit}\``);
  lines.push(`- Sections: ${pack.stats.sections}`);
  lines.push(`- Episodes: ${pack.stats.episodes}`);
  lines.push(`- Beats: ${pack.stats.beats}`);
  lines.push('');

  for (const section of pack.sections) {
    lines.push(`## ${section.title}`);
    lines.push('');
    for (const episode of section.episodes) {
      lines.push(`### ${episode.id.toUpperCase()}：${episode.title}`);
      lines.push('');
      for (const beat of episode.beats) {
        lines.push(`#### ${beat.id.toUpperCase()}`);
        lines.push('');
        lines.push('##### 原文');
        lines.push('');
        lines.push(beat.sourceMarkdown.trim());
        lines.push('');
        lines.push(`##### 陪读评论（${(beat.commentaryType || []).join(' / ')}）`);
        lines.push('');
        lines.push((beat.commentaryMarkdown || '').trim());
        lines.push('');
        lines.push('---');
        lines.push('');
      }
    }
  }

  return `${lines.join('\n').trim()}\n`;
}

async function main() {
  const markdown = await readFile(SOURCE_FILE, 'utf8').catch(() => {
    throw new Error('Chapter 1 markdown not found. Run `npm run chapter1:fetch` first.');
  });

  const blocks = splitIntoBlocks(markdown);
  const { chapterTitle, sections: rawSections } = splitChapterIntoSections(blocks);
  let sections = splitSectionsIntoEpisodes(rawSections)
    .filter((section) => !/^References\s*\/\s*参考文献/i.test(section.title));

  const allEpisodes = flattenEpisodes(sections);
  const selectedEpisodes = Number.isFinite(LIMIT_EPISODES) ? allEpisodes.slice(0, LIMIT_EPISODES) : allEpisodes;
  const selectedIds = new Set(selectedEpisodes.map(({ episode }) => episode.id));
  sections = sections
    .map((section) => ({
      ...section,
      episodes: section.episodes.filter((episode) => selectedIds.has(episode.id)),
    }))
    .filter((section) => section.episodes.length);

  const totalEpisodes = flattenEpisodes(sections).length;
  let processed = 0;
  const processedSections = [];

  for (const section of sections) {
    const episodes = [];
    for (const episode of section.episodes) {
      console.log(`${STRUCTURE_ONLY ? 'Structuring' : 'Generating'} ${episode.id}/${totalEpisodes}: ${episode.title}`);
      const generated = await generateCommentaryForEpisode({ section, episode }, processed, totalEpisodes);
      episodes.push(generated);
      processed += 1;
    }
    processedSections.push({ ...section, episodes });
  }

  const stats = {
    sections: processedSections.length,
    episodes: processedSections.reduce((sum, section) => sum + section.episodes.length, 0),
    beats: processedSections.reduce((sum, section) => sum + section.episodes.reduce((inner, episode) => inner + episode.beats.length, 0), 0),
    structureOnly: STRUCTURE_ONLY,
    model: STRUCTURE_ONLY ? null : DEFAULT_MODEL,
  };

  const pack = {
    book: {
      title: 'Agentic Design Patterns',
      chapter: chapterTitle,
      sourceCommit: SOURCE_COMMIT,
      sourcePath: 'bilingual/Chapter 1_ Prompt Chaining.md',
    },
    stats,
    sections: processedSections,
  };

  await mkdir(path.dirname(OUTPUT_JSON), { recursive: true });
  await writeFile(OUTPUT_JSON, `${JSON.stringify(pack, null, 2)}\n`, 'utf8');
  await writeFile(OUTPUT_PREVIEW, buildPreview(pack), 'utf8');

  console.log(`Wrote ${path.relative(process.cwd(), OUTPUT_JSON)}`);
  console.log(`Wrote ${path.relative(process.cwd(), OUTPUT_PREVIEW)}`);
  console.log(`Stats: ${stats.sections} sections, ${stats.episodes} episodes, ${stats.beats} beats`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
