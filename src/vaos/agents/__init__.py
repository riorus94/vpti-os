"""Proactive agent layer (ADR-0009).

Scheduled/triggered runners that act without a user Query, reusing the domain +
ports. Each agent's core is a deep function with injected ports (testable with
fakes); the scheduler/trigger is an adapter concern kept out of the logic.
"""
