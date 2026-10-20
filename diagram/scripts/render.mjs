#!/usr/bin/env node
// Render a Mermaid .mmd file to SVG or PNG with Pele, using a named palette.
//
// Usage:
//   render.mjs <input.mmd> [--for iterm|obsidian] [--theme NAME] [--format svg|png]
//                          [--out PATH] [--zoom N] [--transparent] [--show]
//
// No flags: writes <base>.light.svg and <base>.dark.svg.
// --for iterm:    catppuccin (Mocha), PNG (iTerm2 shows PNG inline, not SVG).
// --for obsidian: paper, SVG (Obsidian embeds SVG as an image).
// --theme NAME:   one file, <base>.<NAME>.<format>, format defaults to svg.
// --transparent:  SVG without its theme background, for a host of matching lightness.
// --show:         also show a catppuccin PNG in a reusable iTerm2 pane (Preview elsewhere).

import { render, PeleError } from 'pele';
import { readFileSync, readdirSync, writeFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { basename, join } from 'node:path';
import { showPreview } from './preview.mjs';

const PALETTES = new URL('../palettes/', import.meta.url);
const PRESETS = {
  iterm: { theme: 'catppuccin', format: 'png' },
  obsidian: { theme: 'paper', format: 'svg' },
};
const DEFAULT_PAIR = ['light', 'dark'];
// The preview matches the iTerm2 terminal theme, whatever the deliverable's theme is.
const PREVIEW = PRESETS.iterm.theme;
const FORMATS = ['svg', 'png'];

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

function usage(code) {
  console.error('usage: render.mjs <input.mmd> [--for iterm|obsidian] [--theme NAME] [--format svg|png] [--out PATH] [--zoom N] [--transparent] [--show]');
  process.exit(code);
}

function parseArgs(argv) {
  const opts = { zoom: 2 };
  let input;
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const value = () => {
      const v = argv[++i];
      if (v === undefined) fail(`${arg} needs a value`);
      return v;
    };
    if (arg === '--for') opts.for = value();
    else if (arg === '--theme') opts.theme = value();
    else if (arg === '--format') opts.format = value();
    else if (arg === '--out') opts.out = value();
    else if (arg === '--zoom') opts.zoom = Number(value());
    else if (arg === '--show') opts.show = true;
    else if (arg === '--transparent') opts.transparent = true;
    else if (arg === '-h' || arg === '--help') usage(0);
    else if (arg.startsWith('-')) fail(`unknown flag ${arg}`);
    else if (input) fail('only one input file is allowed');
    else input = arg;
  }
  if (!input) usage(2);
  return { ...opts, input };
}

function loadPalette(name) {
  try {
    return JSON.parse(readFileSync(new URL(`${name}.json`, PALETTES), 'utf8'));
  } catch {
    const available = readdirSync(PALETTES).map((f) => f.replace(/\.json$/, '')).join(', ');
    fail(`unknown theme "${name}". Available: ${available}`);
  }
}

// Pele reads colors from CSS variables with fallbacks. A file opened outside the
// page can't see the page's variables, and librsvg ignores var() in attributes,
// so every var() is replaced with its literal value.
function bake(svg, palette) {
  const withPalette = svg.replace(/var\(--pele-([a-z0-9-]+),[^)]*\)/g, (match, name) => palette[name] ?? match);
  const internal = {};
  for (const [, name, value] of withPalette.matchAll(/--(_[a-z0-9-]+):([^;"]+)/g)) internal[name] = value.trim();
  return withPalette.replace(/var\(--(_[a-z0-9-]+)\)/g, (match, name) => internal[name] ?? match);
}

// Theme ink (text, lines) assumes the theme's own background. Pele leaves the SVG
// transparent, so on a host of the opposite lightness the ink disappears; paint the bg.
function withBackground(svg, palette) {
  return svg.replace(/(<svg\b[^>]*>)/, `$1<rect width="100%" height="100%" fill="${palette.bg}"/>`);
}

function toPng(svg, out, zoom, background) {
  const dir = mkdtempSync(join(tmpdir(), 'diagram-'));
  try {
    const svgPath = join(dir, 'diagram.svg');
    writeFileSync(svgPath, svg);
    const result = spawnSync('rsvg-convert', ['-z', String(zoom), '-b', background, '-o', out, svgPath], {
      encoding: 'utf8',
    });
    if (result.error?.code === 'ENOENT') throw new Error('rsvg-convert not found. Install with: brew install librsvg');
    if (result.status !== 0) throw new Error(`rsvg-convert failed: ${result.stderr.trim()}`);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (!Number.isFinite(opts.zoom) || opts.zoom <= 0) fail('--zoom must be a positive number');

  let { theme, format } = opts;
  if (opts.for) {
    const preset = PRESETS[opts.for];
    if (!preset) fail(`unknown --for "${opts.for}". Use iterm or obsidian`);
    theme ??= preset.theme;
    format ??= preset.format;
  }
  if (format && !FORMATS.includes(format)) fail(`unknown format "${format}". Use svg or png`);

  const targets = theme
    ? [{ theme, format: format ?? 'svg' }]
    : DEFAULT_PAIR.map((name) => ({ theme: name, format: format ?? 'svg' }));
  if (opts.out && targets.length > 1) fail('--out needs one target; pass --theme or --for');

  let source;
  try {
    source = readFileSync(opts.input, 'utf8');
  } catch {
    fail(`cannot read ${opts.input}`);
  }

  const base = opts.input.replace(/\.mmd$/, '');
  const idPrefix = base.split('/').pop().replace(/[^a-zA-Z0-9]+/g, '-');

  const renderTheme = (name) => {
    try {
      const palette = loadPalette(name);
      const svg = bake(render(source, { padding: 16, fontSize: 14, idPrefix }).svg, palette);
      return opts.transparent ? svg : withBackground(svg, palette);
    } catch (error) {
      if (error instanceof PeleError) fail(`${opts.input}: ${error.message}`);
      throw error;
    }
  };

  let previewPng;
  for (const target of targets) {
    const svg = renderTheme(target.theme);
    const out = opts.out ?? `${base}.${target.theme}.${target.format}`;
    if (target.format === 'png') {
      try {
        toPng(svg, out, opts.zoom, loadPalette(target.theme).bg);
      } catch (error) {
        fail(error.message);
      }
    } else writeFileSync(out, svg);
    console.log(`✓ ${out}`);
    if (target.theme === PREVIEW && target.format === 'png') previewPng = out;
  }

  if (opts.show) {
    // The preview is a convenience: a failure here warns and leaves the exit code alone.
    try {
      if (!previewPng) {
        const dir = join(tmpdir(), 'diagram-preview');
        mkdirSync(dir, { recursive: true });
        previewPng = join(dir, `${basename(base)}.png`);
        toPng(renderTheme(PREVIEW), previewPng, opts.zoom, loadPalette(PREVIEW).bg);
      }
      showPreview(previewPng);
    } catch (error) {
      console.error(`warning: preview skipped (${error.message})`);
    }
  }
}

main();
