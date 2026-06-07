---
template_id: format-only-v1
condition: format_only
version: "1.0.0"
---

You are completing a bounded research task using the provided source packet.

Question:
{{ research_question }}

Sources:
{{ source_packet }}

Use only these source IDs when referring to the packet: {{ source_ids }}.

First create a claim table listing each substantive claim in your answer. For
each claim, include only:
- claim text

Then write the final answer.

End your response with the exact line `Final claims:` on its own, followed by
one substantive claim from your answer per line, each prefixed with `- `. This
footer is required for downstream measurement; do not omit it or rename the
header.
