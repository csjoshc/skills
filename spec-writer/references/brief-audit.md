# Author-side Brief Audit

Mandatory check before delegating a ticket to a subagent. Extracted from `SKILL.md` for the 500-line budget.

## Author-side brief audit (mandatory before subagent delegation)

When spec-writer is invoked to produce a BUILD subagent's brief (the
prompt passed to the agent that will write the ticket's code), the
brief itself is a piece of code that runs in the subagent's context.
Brief bugs compound: a buggy shell command in the brief becomes a
buggy ticket AC becomes a buggy verification path becomes an
operator-facing bug.

**Before sending any subagent brief, the author (parent agent or
human) must self-audit the brief for these failure modes:**

1. **Shell command runnability** (Pattern 16 in ticket-critic):
   - Every `curl` / `wget` / `jq` / `nc` invocation is verified
     present in the target environment (base image, CI runner, dev
     host) OR replaced with a stdlib alternative.
   - Path math (`../../`, `$SCRIPT_DIR/../...`) is verified by
     counting directory depth, not guessed.
   - `localhost` is replaced with `127.0.0.1` for healthchecks
     inside containers (alpine base images resolve `localhost` to
     `::1` first).
2. **Wrapper-target verification** (Pattern 17 in ticket-critic):
   - If the ticket creates or modifies a Makefile target, the
     brief must instruct the subagent to verify the target by
     invoking it *literally* (not by an explicit-service sidestep).
   - For profile-scoped compose wrappers, the brief must require
     both a positive AC ("intended services up") and a negative AC
     ("unintended services NOT up").
3. **Runtime contracts referenced are accurate** (Pattern 27 in
   antiplan rubric):
   - Every schema, enum, path, or model the brief names must be
     verified against the brownfield-context.md row (or, if that's
     thin, grep'd against the actual repo before authoring the
     brief).
   - Field counts, enum values, and base-image binaries quoted in
     the brief must come from observation, not memory.
4. **Subagent verification surface** (Pattern 18 in ticket-critic):
   - The brief names what the build subagent must report in its
     final message: files created, per-AC result, artifact paths,
     deviations.
   - The brief instructs the subagent NOT to flip Stage: COMPLETE
     if any AC was skipped without justification; if env
     prerequisites are absent, the skip path is loud (named in the
     final report).
5. **Scope guardrails:**
   - The brief explicitly enumerates files the subagent may NOT
     touch (other tickets' files, .plan/, etc.).
   - The brief instructs DO NOT run git commands.

If running the audit by hand is too heavy at scale, spawn a
brief-audit subagent:

```
Agent(subagent_type="general-purpose", prompt="Audit this BUILD
subagent brief for Patterns 16, 17, 18 (ticket-critic) and AP-26,
AP-27 (antiplan rubric). For each shell command in the brief,
verify the binary is available in the target env. For path math,
verify the depth. For wrapper-target ACs, verify positive + negative
shape. Return either VERIFIED or a list of issues to fix before
the brief is sent.")
```

Always run the brief audit. Half the bugs that survive the pipeline
to operator-contact are brief bugs.
