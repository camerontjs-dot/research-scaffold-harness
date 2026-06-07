---
template_id: provenance-scaffold-v1
condition: provenance_scaffold
version: "1.0.0"
---

You are completing a bounded research task using the provided source packet.

Question:
{{ research_question }}

Sources:
{{ source_packet }}

Use only these source IDs when citing the packet: {{ source_ids }}.

First create a claim table. For each substantive claim, include:
- claim text
- support status: sourced, inferred, uncertain, or unsupported
- source ID and passage reference where applicable
- short note explaining the basis for the label

Then write the final answer using only claims from the table. Keep inferred or
uncertain claims visibly qualified.

End your response with the exact line `Final claims:` on its own, followed by
one substantive claim from your answer per line, each prefixed with `- `. This
footer is required for downstream measurement; do not omit it or rename the
header.
