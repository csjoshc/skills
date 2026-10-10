# Planning chat, 2030-02-03

**User:** The bike shop loses repair jobs when the paper ticket goes missing. I want a screen where staff log a repair and see what is waiting.

**Agent:** Should customers see their repair status too?

**User:** Not yet. Staff only for now. And no billing; the till handles that.

**Agent:** Decision D1: staff-only repair log, no customer view this cycle. Decision D2: billing stays on the till. I split it into T-001 (repair record) and T-002 (waiting list). For T-002, is the waiting list sorted by drop-off date?

**User:** Yes, oldest first. It has to run on the shop laptop with no internet.

**Agent:** Decision D3: offline-only, local storage. Proof for review: tests pass on the laptop build.
