// ai-excited-01 entry: "One small leap becomes a universe".
// The image is drawn at build time by draw_excited.py (PIL, deterministic
// seed 20261116) and shipped here as entry.png; this program copies it to
// the grader's output directory, checking the gate limits on the way:
// a whole PNG, at most 1 MiB, at most 1024 by 1024 pixels.
//
// Local check: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const SOURCE = new URL('./entry.png', import.meta.url);
const DEST_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const DEST = join(DEST_DIR, 'entry.png');

const bytes = readFileSync(SOURCE);
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG file');
}
if (bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB gate`);
}
// IHDR chunk: width and height are the first 8 bytes of its data,
// at file offsets 16-19 and 20-23 (big-endian uint32).
if (!bytes.subarray(12, 16).equals(Buffer.from('IHDR'))) {
  throw new Error('entry.png has no IHDR chunk where a PNG must');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 gate`);
}
const size = statSync(SOURCE).size;
if (size !== bytes.length) {
  throw new Error('entry.png changed while being read');
}

copyFileSync(SOURCE, DEST);
// The grader runs this program twice and demands identical bytes, so
// confirm the copy landed byte for byte before reporting success.
if (!readFileSync(DEST).equals(bytes)) {
  throw new Error('copied entry.png does not match the repository file');
}
