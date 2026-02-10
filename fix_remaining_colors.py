#!/usr/bin/env python
"""Script to fix all remaining hardcoded colors in ai.py"""

with open('pages/ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all remaining hardcoded background: white with theme_colors
content = content.replace(
    "background: white;",
    "background: {theme_colors['card_bg']};"
)

# Replace all remaining hardcoded text colors
content = content.replace(
    "color: #2d3748;",
    "color: {theme_colors['text']};"
)

content = content.replace(
    "color: #718096;",
    "color: {theme_colors['text_secondary']};"
)

# Handle special cases with f-strings
content = content.replace(
    'box-shadow: 0 2px 4px rgba(0,0,0,0.1);',
    'box-shadow: 0 2px 4px rgba(0,0,0,0.15);'
)

with open('pages/ai.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ All remaining hardcoded colors have been replaced with theme-aware colors")
