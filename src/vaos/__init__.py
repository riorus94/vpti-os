"""VAOS — VPTI AI Operating System.

Architecture: hexagonal (ports & adapters).

    domain/    pure types + rules, zero I/O      (unit-tested directly)
    ports/     interfaces the core depends on     (Protocols)
    adapters/  concrete implementations of ports  (Azure, FAISS, Telegram, ...)
    modules/   the deep modules, wired from ports
    pipeline/  request orchestration

See CONTEXT.md (glossary), docs/PRD.md (spec), docs/adr/ (decisions).
"""

__version__ = "0.1.0"
