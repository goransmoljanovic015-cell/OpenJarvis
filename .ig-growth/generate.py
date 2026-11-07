#!/usr/bin/env python3
"""Compatibility entry point for the real content production pipeline.

Examples:
    python .ig-growth/generate.py build --id 02-gmail-filter
    python .ig-growth/generate.py build --model YOUR_MODEL

This command creates review packages. It does not publish or send messages.
"""
from content_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())
