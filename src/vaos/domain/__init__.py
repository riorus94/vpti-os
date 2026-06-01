"""Pure domain types and rules — no I/O, no LLM, no network.

Everything here is directly unit-testable. The Decision Engine and Context
validation live in this layer precisely so the ADR-0001 invariants and the
Q8 pure mapping can be tested without mocks.
"""
