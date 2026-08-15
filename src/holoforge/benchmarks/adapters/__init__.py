"""Command-facing adapters for the built-in Forge/Verify benchmarks.

Each module owns only parser, execution, rendering, and evidence-metadata glue
for one benchmark. Numerical implementations remain in ``holoforge.benchmarks``.
The explicit built-in composition root remains ``holoforge.benchmarks.registry``.
"""
