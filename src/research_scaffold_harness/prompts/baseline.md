---
template_id: baseline-v1
condition: baseline
version: "1.0.0"
---

You are completing a bounded research task using the provided source packet.

Question:
{{ research_question }}

Sources:
{{ source_packet }}

Write a concise, useful answer. Use only the provided sources unless the task
instructions explicitly allow outside knowledge. If the source packet does not
support a point, avoid stating it as fact.

End your response with the exact line `Final claims:` on its own, followed by
one substantive claim from your answer per line, each prefixed with `- `. This
footer is required for downstream measurement; do not omit it or rename the
header.
