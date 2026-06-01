# Indonesian-first; cite pasal text verbatim, never machine-translated

**Status:** accepted

The system operates in Bahasa Indonesia: queries, reasoning, and output (with localized template headers — Ringkasan Eksekutif / Analisis / Risiko / Peluang / Rekomendasi). FAISS uses a multilingual embedding model. Official regulation text from `pasal-id` is cited **verbatim in Indonesian and never machine-translated**.

## Why

The audience is Indonesian VPTI/government operators and the authoritative sources are Indonesian. More importantly, a translation layer between the law and the citation introduces interpretation risk into compliance answers — directly undermining the grounding promise (ADR-0001). A future engineer may want to translate citations for an English-reading executive; that must be a *rendering* concern on a specific output, never a transformation of the authoritative text the answer is grounded in.

## Consequence

If an English deliverable is ever needed, translate the *surrounding analysis* but keep the pasal quotation in Indonesian with the official reference, clearly marked as the source of truth.
