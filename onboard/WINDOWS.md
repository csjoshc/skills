# WINDOWS.md — File Operations & Shell Reference for Git Bash on Windows

## Contents

- 1. Path Syntax Rules (Critical)
- 2. Reading Files
- 3. Creating & Writing Files
- 4. Editing Files In-Place with `sed`
- 5. Multi-location Edits with `awk`
- 6. Searching Files
- 7. Finding Files
- 8. Copy, Move, Delete
- 9. Directory Operations
- 10. Running Node / npm / npx


> **Environment:** Git Bash (MINGW64 / MSYS2), running on Windows.
> This is NOT PowerShell and NOT WSL. Unix commands (`ls`, `grep`, `sed`, `find`) work,
> but Windows-native path syntax and PowerShell cmdlets do NOT work natively.

---

## 1. Path Syntax Rules (Critical)

Git Bash uses **POSIX-style paths** internally but runs on Windows. Understanding the
path model prevents the most common class of errors.

### Canonical Path Format in Git Bash

| Windows Path            | Git Bash Equivalent      |
| :---------------------- | :----------------------- |
| `C:\Users\josh\dev`     | `/c/Users/josh/dev`      |
| `D:\Projects\app`       | `/d/Projects/app`        |
| `%USERPROFILE%`         | `$HOME` or `~`           |
| `.\relative\path`       | `./relative/path`        |

**Rules:**
- Always use **forward slashes** `/` — backslashes `\` are escape characters in bash.
- Drive letters become lowercase, prefixed with `/`: `C:` → `/c/`.
- Trailing slashes are optional but consistent with Unix convention.
- Use `$HOME` or `~` for the user home directory.

### Converting Paths Explicitly

```bash
# Windows → POSIX
cygpath -u "C:\\Users\\josh\\dev\\app.ts"
# Output: /c/Users/josh/dev/app.ts

# POSIX → Windows
cygpath -w "/c/Users/josh/dev/app.ts"
# Output: C:\Users\josh\dev\app.ts

# Resolve a relative path to absolute POSIX
realpath ./src/index.ts
```

### Disabling Automatic Path Conversion

Git Bash silently converts POSIX paths when calling native Windows binaries,
which can mangle arguments like `--flag /value` into `--flag C:/Program Files/Git/value`.

```bash
# Disable for a single command
MSYS_NO_PATHCONV=1 some-native-windows-tool.exe --flag "/registry/key"

# Disable for the entire session
export MSYS_NO_PATHCONV=1

# Alternative: double the leading slash to suppress conversion
some-tool.exe //registry/key
```

---

## 2. Reading Files

```bash
# Print entire file
cat /c/Users/josh/dev/app.ts

# Print with line numbers
cat -n /c/Users/josh/dev/app.ts

# First 20 lines
head -n 20 /c/Users/josh/dev/app.ts

# Last 20 lines
tail -n 20 /c/Users/josh/dev/app.ts

# Follow a log file in real time
tail -f /c/Users/josh/dev/logs/app.log

# Print specific lines (e.g. lines 10–25)
sed -n '10,25p' /c/Users/josh/dev/app.ts

# Print a single line (e.g. line 42)
sed -n '42p' /c/Users/josh/dev/app.ts
```

---

## 3. Creating & Writing Files

```bash
# Create a new file (overwrites if exists)
cat > /c/Users/josh/dev/hello.txt << 'EOF'
Hello, World!
This is line two.
EOF

# Append to an existing file
cat >> /c/Users/josh/dev/hello.txt << 'EOF'
This line is appended.
EOF

# One-liner write
echo "console.log('hello');" > /c/Users/josh/dev/index.js

# One-liner append
echo "console.log('world');" >> /c/Users/josh/dev/index.js

# Touch (create empty or update timestamp)
touch /c/Users/josh/dev/newfile.ts
```

> ⚠️ **Line endings:** Git Bash writes **LF** (`\n`) by default. If Windows tools
> require CRLF, use: `unix2dos /c/Users/josh/dev/file.txt`

---

## 4. Editing Files In-Place with `sed`

> ⚠️ **Windows `sed -i` quirk:** MINGW64's `sed -i` does not require a backup
> extension (unlike macOS `sed`), but some builds create a backup file `file.txt~`.
> Use `-i` (no argument) — it works correctly in Git Bash's bundled GNU `sed`.

### Replace exact text on a known line range

```bash
# Replace first occurrence of "Old text" on line 3
sed -i '3s/Old text/New text/' /c/Users/josh/dev/file.txt

# Replace all occurrences in the file
sed -i 's/oldVariable/newVariable/g' /c/Users/josh/dev/app.ts

# Replace only between line 10 and line 50
sed -i '10,50s/foo/bar/g' /c/Users/josh/dev/app.ts

# Case-insensitive replace (GNU sed)
sed -i 's/oldtext/newtext/gI' /c/Users/josh/dev/app.ts
```

### Delete lines

```bash
# Delete line 7
sed -i '7d' /c/Users/josh/dev/file.txt

# Delete lines 10 through 15
sed -i '10,15d' /c/Users/josh/dev/file.txt

# Delete all lines matching a pattern
sed -i '/TODO: remove this/d' /c/Users/josh/dev/app.ts
```

### Insert or append a line

```bash
# Insert a line BEFORE line 5
sed -i '5i\const newVar = true;' /c/Users/josh/dev/app.ts

# Append a line AFTER line 5
sed -i '5a\const newVar = true;' /c/Users/josh/dev/app.ts
```

### Safe pattern: edit to temp file first

If the in-place operation is risky, use a temp file:
```bash
sed 's/oldValue/newValue/g' /c/Users/josh/dev/app.ts > /tmp/app_patched.ts \
  && mv /tmp/app_patched.ts /c/Users/josh/dev/app.ts
```

---

## 5. Multi-location Edits with `awk`

For replacing content at multiple specific line numbers in one pass:

```bash
# Replace line 10 with new content AND line 25 with other content
awk 'NR==10 { print "const y = 2;" } NR==25 { print "return y;" } NR!=10 && NR!=25' \
  /c/Users/josh/dev/code.ts > /tmp/code_patched.ts \
  && mv /tmp/code_patched.ts /c/Users/josh/dev/code.ts
```

---

## 6. Searching Files

```bash
# Search for pattern in a file
grep -n "myFunction" /c/Users/josh/dev/app.ts

# Recursive search from a directory
grep -rn "myFunction" /c/Users/josh/dev/src/

# Case-insensitive
grep -rni "todo" /c/Users/josh/dev/src/

# Show 3 lines of context around each match
grep -rn -C 3 "myFunction" /c/Users/josh/dev/src/

# Search only .ts files
grep -rn "myFunction" /c/Users/josh/dev/src/ --include="*.ts"

# Search for multiple patterns
grep -rn -E "foo|bar" /c/Users/josh/dev/src/
```

---

## 7. Finding Files

```bash
# Find all TypeScript files under a directory
find /c/Users/josh/dev -name "*.ts"

# Find files modified in the last 24 hours
find /c/Users/josh/dev -name "*.ts" -mtime -1

# Find and exclude node_modules
find /c/Users/josh/dev -name "*.ts" -not -path "*/node_modules/*"

# Find by size (files larger than 1MB)
find /c/Users/josh/dev -size +1M

# Find a file by exact name
find /c/Users/josh/dev -name "package.json" -not -path "*/node_modules/*"
```

---

## 8. Copy, Move, Delete

```bash
# Copy a file
cp /c/Users/josh/dev/app.ts /c/Users/josh/dev/app.backup.ts

# Copy a directory recursively
cp -r /c/Users/josh/dev/src /c/Users/josh/dev/src_backup

# Move / rename
mv /c/Users/josh/dev/old_name.ts /c/Users/josh/dev/new_name.ts

# Delete a file
rm /c/Users/josh/dev/temp.txt

# Delete a directory recursively (no recycle bin — permanent)
rm -rf /c/Users/josh/dev/dist/

# Safe delete: confirm before each file
rm -i /c/Users/josh/dev/temp.txt
```

---

## 9. Directory Operations

```bash
# List files (long format, including hidden)
ls -la /c/Users/josh/dev/

# List only directories
ls -d /c/Users/josh/dev/*/

# Create a directory (including parents)
mkdir -p /c/Users/josh/dev/src/components/ui

# Print current working directory (POSIX format)
pwd

# Change directory
cd /c/Users/josh/dev/src
```

---

## 10. Running Node / npm / npx

> ⚠️ **Interactive programs need `winpty`** in Git Bash (e.g., Python REPL, Node REPL).
> For non-interactive scripts, `winpty` is NOT needed.

```bash
# Non-interactive — no winpty needed
node /c/Users/josh/dev/script.js
npm install
npm run build
npx tsc --noEmit

# Capture last 30
