# TDD Commit Discipline

Commit when a **working call stack** is proven — typically after a producer → subject → consumer integration check can run — not after every intermediate support-file edit. Prefer one commit per completed vertical slice / workplan node set. Never commit a broken build, failing tests, or half-wired feature unless the user explicitly directs a WIP commit.

After each feature (or small set of tasks):

1. **Run the relevant tests** from your test suite
2. **Update progress documentation** with status and notes
3. **Stage all related files**, including new files (`git add ...`)
4. **Verify `git status` is clean** before commit
5. **Create a small, descriptive git commit** so rollback is clean
6. **Only when the user asks** — agents do not commit unprompted (see user git rules)

```bash
# Example commit workflow
pytest tests/path/to/test.py -v           # Run tests
git add src/path/file.py tests/path/test.py
git status                                 # Verify clean
git commit -m "feat: add specific feature"
```

## Deprecation Cleanup

When a file/module is confirmed unused or explicitly deprecated:
1. Remove the file in the same feature branch
2. Verify no references remain (`rg -n "OldSymbol|old/path"`)
3. Include the deletion in the same commit as the replacement work
