import re

# Regex created by brave://leo-ai/
# Regex tested at https://regex101.com/

# Pre-compile the regex
# \b ensures we match whole words only
# (?: ... ) groups the variations without creating a capture group
# (?=...) lookaheads ensure 'bl' is followed by a separator or end of string to avoid 'ruble'
BL_PATTERN = re.compile(
    r"""
    \b
    (?:
        # 1. Acronyms: bl, bol, bls, bols
        # 'b' optionally 'o', then 'l', optionally 's'
        # Must be followed by a separator or end of string
        b(?:o)?l s?
        (?=[/_\s\-.]|$)
        
        |

        # 2. Full Phrases: bill of lading, bill lading
        # Flexible separators between words
        bill (?:of )? lading
        
        |

        # 3. Synonyms: cargo docs, cargo doc
        # CRITICAL FIX: Added separator between 'cargo' and 'doc(s)'
        cargo (?:\s|_|/|-)? doc s?
        # Must be followed by a separator or end of string
        (?=[/_\s\-.]|$)
    )
    \b
    """,
    re.IGNORECASE | re.VERBOSE,
)
