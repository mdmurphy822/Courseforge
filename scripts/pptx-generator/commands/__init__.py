"""Slideforge CLI commands."""

from .validate import validate
from .inspect import inspect_cmd
from .generate import generate
from .catalog import catalog

__all__ = ['validate', 'inspect_cmd', 'generate', 'catalog']
