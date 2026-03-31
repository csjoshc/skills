# Example Sessions

## Interactive Mode (HITL)

```
user: write-prd "add file upload to dashboard"

skill: Running PRD pipeline...
[Pipeline status: needs_human_feedback, Ambiguity: 0.45]

+----------------------------------------------------+
|  Human-in-the-Loop                                 |
+----------------------------------------------------+
|  Round 1 - 3 question(s) pending                  |
|                                                    |
|  === Storage / Infrastructure (HIGH IMPACT) ===    |
|  q_storage_01: What storage backend?               |
|    Type: independent                               |
|                                                    |
|  === UX / Interaction (MEDIUM IMPACT) ===          |
|  q_progress_01: Show real-time progress?           |
|    Type: dependent                                 |
|    Depends: q_storage_01                           |
|                                                    |
|  q_maxsize_01: Maximum file size?                  |
|    Type: independent                               |
+----------------------------------------------------+

skill: Please provide answers.

user: q_storage_01: S3, q_progress_01: yes, q_maxsize_01: 100MB

skill: Re-running with answers...
[Pipeline status: completed]

Artifacts:
- PRD: .prd/drafts/add-file-upload-to-dashboard.md
- Tickets: .tickets/ (3 tickets, Stage: NEW)

[OK] Pipeline completed.
```

## Non-Interactive Mode (--approve)

```
user: write-prd --approve "add a /health endpoint"

skill: Running PRD pipeline...
[Pipeline status: completed, Ambiguity: 0.12 (low)]

[OK] Pipeline completed successfully.
```

## CLI Invocations

```bash
# Interactive (prompts for description)
write-prd

# Inline text
write-prd "add SSO authentication"

# From intake file
write-prd --input .prd/intake/my-issue.md

# Dry run (preview without writing)
write-prd --dry-run "feature description"

# Target specific project directory
write-prd --output-dir /path/to/project "feature"

# Skip HITL (CI/scripted)
write-prd --approve "feature"

# Provide answers for HITL resume
write-prd --answers '{"q_storage_01": "S3", "q_auth_01": "OAuth2"}'
```
