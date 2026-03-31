# Interactive HITL Question Presentation

When the pipeline pauses for human feedback, present questions in a structured format:

```
+----------------------------------------------------+
|  Human-in-the-Loop                                |
+----------------------------------------------------+
|  Round 1 - 3 question(s) pending                  |
|                                                    |
|  q_auth_01:                                        |
|    What authentication mechanism should be used?   |
|    Type: independent                               |
|    Impact: high                                    |
|                                                    |
|  q_storage_01:                                     |
|    What storage backend for uploaded files?        |
|    Type: independent                               |
|    Impact: high                                    |
|                                                    |
|  q_progress_01:                                    |
|    Should uploads show real-time progress?         |
|    Type: dependent                                 |
|    Depends: q_storage_01                           |
|                                                    |
|  Answer with: --answers '{"q_auth_01": "OAuth2"}' |
|  Or re-run with --approve to skip                  |
+----------------------------------------------------+
```

### Categorize Questions by Architectural Impact

Group and prioritize questions by category:

```
+----------------------------------------------------+
|  Human-in-the-Loop                                |
+----------------------------------------------------+
|  Round 1 - 4 question(s) pending                  |
|                                                    |
|  === Storage / Infrastructure (HIGH IMPACT) ===    |
|  q_storage_01: What storage backend?               |
|    Options: [S3, GCS, local filesystem, other]     |
|    Type: independent                               |
|                                                    |
|  === Authentication / Security (HIGH IMPACT) ===   |
|  q_auth_01: What auth mechanism?                   |
|    Options: [OAuth2, API keys, SSO, none]          |
|    Type: independent                               |
|                                                    |
|  === UX / Interaction (MEDIUM IMPACT) ===          |
|  q_progress_01: Show real-time progress?           |
|    Type: dependent (requires q_storage_01)         |
|                                                    |
|  === Performance / Scale (LOW IMPACT) ===          |
|  q_scale_01: Expected concurrent users?            |
|    Type: independent                               |
|                                                    |
|  Answer with: --answers '{"q_storage_01": "S3"...}'
|  Or re-run with --approve to skip                  |
+----------------------------------------------------+
```

### Collect Answers

Users can answer:
1. **Inline key-value pairs:** `q_storage_01: S3, q_auth_01: OAuth2`
2. **Direct JSON:** `--answers '{"q_storage_01": "S3", "q_auth_01": "OAuth2'}'`
3. **Skip all:** `--approve`

### Round 2

Pipeline prunes the Question DAG based on Round 1 answers. Present any follow-up questions in the same structured format.
