"""Ports — interfaces the core depends on, as typing.Protocols.

The core imports only these, never a concrete adapter. This is what lets the
LLM provider be swapped (ADR-0007) and lets tests stub every external edge.
"""
