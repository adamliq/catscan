#!/usr/bin/env node
/**
 * Parses every inline <script> block in index.html with `new Function()`
 * to catch syntax errors before they ship - the same check this repo's
 * own PRs have been running by hand (as an ad hoc `node -e` one-liner)
 * before every merge. Doesn't execute the scripts, just parses them.
 *
 * Usage: node tools/check_syntax.js
 */
const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '..', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scriptRe = /<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/g;

let match, count = 0;
const errors = [];
while ((match = scriptRe.exec(html)) !== null) {
  const src = match[1];
  if (!src.trim()) continue;
  const openTag = match[0].slice(0, match[0].indexOf('>'));
  if (/\bsrc=/.test(openTag)) continue; // external script, nothing to parse
  count++;
  try {
    new Function(src);
  } catch (e) {
    errors.push(`Script #${count}: ${e.message}`);
  }
}

console.log(`Checked ${count} inline script blocks in index.html`);
if (errors.length) {
  console.error('SYNTAX ERRORS:');
  errors.forEach(e => console.error('  ' + e));
  process.exit(1);
}
console.log('ALL SCRIPTS OK');
