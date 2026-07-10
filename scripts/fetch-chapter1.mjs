import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const REPO = 'xindoo/agentic-design-patterns';
const COMMIT = 'effb52f1730913be650a04e5ffb251c093096894';
const SOURCE_PATH = 'bilingual/Chapter 1_ Prompt Chaining.md';
const OUTPUT_DIR = path.join(process.cwd(), 'content', 'bilingual');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'Chapter 1_ Prompt Chaining.md');
const RAW_URL = `https://raw.githubusercontent.com/${REPO}/${COMMIT}/${SOURCE_PATH
  .split('/')
  .map(encodeURIComponent)
  .join('/')}`;

async function main() {
  console.log(`Downloading Chapter 1 from ${REPO}@${COMMIT}...`);
  const response = await fetch(RAW_URL, {
    headers: {
      'user-agent': 'bandu-reading-agent-mvp0',
      accept: 'text/markdown,text/plain,*/*',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to download ${RAW_URL}: ${response.status} ${response.statusText}`);
  }

  const markdown = await response.text();
  if (!markdown.trim().startsWith('#')) {
    throw new Error('Downloaded file does not look like the expected Chapter 1 Markdown.');
  }

  await mkdir(OUTPUT_DIR, { recursive: true });
  await writeFile(OUTPUT_FILE, markdown, 'utf8');
  console.log(`Saved ${markdown.length.toLocaleString()} characters to ${path.relative(process.cwd(), OUTPUT_FILE)}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
