# PR Fix — Common Comment Types

## Extracting suggestion blocks

Review comments may contain GitHub suggestion blocks:

````
```suggestion
fixed code here
```
````

When a suggestion block is present:
1. Extract the suggested replacement text
2. Identify the lines it replaces (from the comment's `line` and optional `start_line` fields)
3. Apply the replacement exactly as written
4. Run verification — if it fails, report to the user rather than modifying the suggestion

## "Add logging"

Add the log statement in the catch/error block. Do not restructure the try-catch. Match the project's logging pattern (console.error, project logger, etc.).

## "Add tests"

See Step 4 in [workflow.md](workflow.md). Create a new test file following project conventions. Do not modify the source file unless the comment explicitly asks for a source change to improve testability.

## "Fix type error / add type"

Add the type annotation or interface. Run `tsc --noEmit` to verify. If the type change cascades to other files, make all necessary changes before verification but keep them as small as possible.

## "Rename X to Y"

Rename across all usages in the changed files. Use the editor's rename functionality or search-replace. Verify no references were missed with `tsc --noEmit` or `grep`.

## "This could crash / null check"

Add the null/undefined guard. Do not refactor the surrounding logic. Match the existing defensive coding style in the file.

## "Add a docstring" / "Comment this"
Write prose that explains *why*. The reader can see *what* from the
signature. If the original code is load-bearing because of a design
decision recorded in `docs/ADR-*.md`, include the rationale inline
and add `Background: docs/ADR-XXX.md` as a trailing reference.
Never ship `"""ADR-XXX: ..."""` alone — the bare label is the
canonical failure mode `pr-review`'s DC-004 fires on.

## "Rename / strip cycle slug" / "Path coupled to gate"
The reviewer is asking you to remove a planning-system token (gate
slug, ticket ID, cycle name) from a long-lived path or identifier.
Rename to a feature- or scope-based name. For test-artifact roots,
make the path env-overridable (`PROOF_DIR` env with a stable default).
Update every referrer in the same commit; `git grep -nE` is your
friend.
