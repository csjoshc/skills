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

See Step 4 in [workflow.md](~/.skills/pr-fix/workflow.md). Create a new test file following project conventions. Do not modify the source file unless the comment explicitly asks for a source change to improve testability.

## "Fix type error / add type"

Add the type annotation or interface. Run `tsc --noEmit` to verify. If the type change cascades to other files, make all necessary changes before verification but keep them as small as possible.

## "Rename X to Y"

Rename across all usages in the changed files. Use the editor's rename functionality or search-replace. Verify no references were missed with `tsc --noEmit` or `grep`.

## "This could crash / null check"

Add the null/undefined guard. Do not refactor the surrounding logic. Match the existing defensive coding style in the file.
