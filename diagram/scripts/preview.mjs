// Show a PNG in one reusable iTerm2 split pane. Claude Code and similar TUIs capture tool
// output and repaint the screen, so imgcat only renders in a session they don't own.
// Falls back to macOS Preview. Never throws: the preview is a convenience, not the output.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';

const STATE = join(homedir(), '.cache', 'diagram', 'preview-session');
const ITERM_IMGCAT = '/Applications/iTerm.app/Contents/Resources/utilities/imgcat';

// argv: saved pane id, agent session id, command. Reuses the saved pane only if it sits in
// the agent's tab, else splits the agent session. Gives focus back to the agent; prints the pane id.
const SCRIPT = `
on findTab(wanted)
  tell application "iTerm2"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if id of s is wanted then return t
        end repeat
      end repeat
    end repeat
  end tell
  return missing value
end findTab

on run argv
  tell application "iTerm2"
    set agentTab to missing value
    if item 2 of argv is not "" then set agentTab to my findTab(item 2 of argv)
    if agentTab is missing value then
      set agentTab to current tab of current window
      set agentSession to current session of current window
    else
      set agentSession to first session of agentTab whose id is (item 2 of argv)
    end if
    set previewSession to missing value
    if (item 1 of argv) is not "" then
      set matches to (sessions of agentTab whose id is (item 1 of argv))
      if matches is not {} then set previewSession to item 1 of matches
    end if
    if previewSession is missing value then
      tell agentSession to set previewSession to (split vertically with default profile)
    end if
    tell previewSession to write text (item 3 of argv)
    tell agentSession to select
    return id of previewSession
  end tell
end run`;

const quote = (s) => `'${s.replaceAll("'", `'\\''`)}'`;

function imgcatPath() {
  const found = spawnSync('sh', ['-c', 'command -v imgcat'], { encoding: 'utf8' }).stdout.trim();
  return found || (existsSync(ITERM_IMGCAT) ? ITERM_IMGCAT : null);
}

function showInPane(png) {
  const imgcat = imgcatPath();
  if (!imgcat) return { error: 'imgcat not found' };
  const saved = existsSync(STATE) ? readFileSync(STATE, 'utf8').trim() : '';
  // ITERM_SESSION_ID is "w0t0p0:<uuid>"; the uuid is the AppleScript session id.
  const origin = (process.env.ITERM_SESSION_ID ?? '').split(':').pop();
  const result = spawnSync('osascript', ['-', saved, origin, `clear; ${quote(imgcat)} ${quote(png)}`], {
    input: SCRIPT,
    encoding: 'utf8',
  });
  if (result.status !== 0) return { error: (result.stderr || 'osascript failed').trim() };
  const pane = result.stdout.trim();
  mkdirSync(dirname(STATE), { recursive: true });
  writeFileSync(STATE, `${pane}\n`);
  return { pane };
}

export function showPreview(file) {
  // The preview pane starts in its own cwd, so a relative path would not resolve there.
  const png = resolve(file);
  const inIterm = process.env.TERM_PROGRAM === 'iTerm.app' || Boolean(process.env.ITERM_SESSION_ID);
  if (inIterm) {
    const { pane, error } = showInPane(png);
    if (pane) return console.log(`preview: ${png} (iTerm2 pane ${pane})`);
    console.error(`warning: iTerm2 preview failed (${error}); opening Preview`);
  }
  const opened = spawnSync('open', [png]);
  if (opened.status === 0) console.log(`preview: ${png} (opened in Preview)`);
  else console.error(`warning: could not open ${png}`);
}
