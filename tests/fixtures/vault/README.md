# Golden-set fixture vault

A tiny, fixed set of internal-Vault notes used to make FAISS retrieval tests
deterministic (vaos-mvp/04). Do **not** point retrieval tests at the live vault.

Add small `.md` notes here with known content so ranking assertions (top-k,
empty-on-no-match) are stable.
