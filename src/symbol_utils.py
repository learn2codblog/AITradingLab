"""Symbol normalization helpers

Provide `normalize_symbol` to convert user input like 'infy' or 'NSE:infy'
to a canonical form used across the app (e.g. 'INFY.NS' or 'NSE:INFY').
"""
from typing import Optional


def normalize_symbol(symbol: Optional[str], default_exchange: str = 'NS') -> Optional[str]:
    """Normalize a stock symbol input.

    - Strips whitespace and uppercases.
    - If input contains a dot (.) or colon (:), returns an uppercased form.
    - If input is a bare symbol (e.g., 'infy'), appends the default exchange suffix
      (e.g., '.NS') and returns uppercased.

    Returns None if input is falsy.
    """
    if not symbol:
        return None

    s = symbol.strip()
    if not s:
        return None

    # If already contains exchange prefix (e.g., 'NSE:INFY'), normalize both parts
    if ':' in s:
        parts = s.split(':', 1)
        return f"{parts[0].upper()}:{parts[1].upper()}"

    s = s.upper()

    # If already has dot suffix like '.NS' or includes market code, return as-is
    if '.' in s:
        return s

    # Otherwise append default exchange suffix
    return f"{s}.{default_exchange}"
