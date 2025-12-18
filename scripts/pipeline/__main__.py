#!/usr/bin/env python3
"""
Pipeline module entry point.

Allows running the pipeline as:
    python -m scripts.pipeline <command> [options]
"""

from .cli import main

if __name__ == '__main__':
    exit(main())
