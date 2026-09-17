"""Storage adapters for the four-store architecture.

Adapters intentionally expose small async interfaces so production backends can
be plugged in without changing API or RAG code. The default implementation is
in-memory and is suitable for development/tests.
"""

