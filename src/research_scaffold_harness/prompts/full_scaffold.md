---
template_id: full-scaffold-v1
condition: full_scaffold
version: "1.0.0"
---

You are completing a bounded research task using the provided source packet.

Question:
{{ research_question }}

Sources:
{{ source_packet }}

Use only these source IDs when citing the packet: {{ source_ids }}.

Work in these stages:
1. Draft an answer plan.
2. Build an evidence note table tied to source IDs and passages.
3. Build a claim table with support status: sourced, inferred, uncertain, or unsupported.
4. Run a disconfirmation pass: identify source-packet evidence that weakens, limits, or contradicts the draft answer.
5. Label uncertainty and scope limits.
6. Create a final claim audit table that marks which claims are retained, downgraded, or removed.
7. Write the final answer using only retained or explicitly qualified claims.

Preserve useful information when it is supported. Do not hedge a supported
conclusion into uselessness merely because the scaffold asks for caution.

End your response with the exact line `Final claims:` on its own, followed by
one substantive claim from your answer per line, each prefixed with `- `. This
footer is required for downstream measurement; do not omit it or rename the
header.
