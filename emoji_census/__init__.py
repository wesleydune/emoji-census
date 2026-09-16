"""Count emoji sequences in text streams without loading them into memory."""

from .scanner import iter_sequences

__version__ = "0.1.0"
__all__ = ["iter_sequences"]
