#!/usr/bin/env python3
import json
import re

def hex_to_rgb(hex_color):
    """Convert #RRGGBB or #RGB to [R, G, B]"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        # Expand shorthand #RGB to #RRGGBB
        hex_color = ''.join(c * 2 for c in hex_color)
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def remove_comments(text):
    """Remove // style comments from JSONC"""
    # Use regex to remove single-line comments
    # This handles // comments but preserves strings containing //
    result = []
    in_string = False
    escape = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Handle escape sequences in strings
        if escape:
            result.append(char)
            escape = False
            i += 1
            continue
            
        # Check for escape character
        if char == '\\' and in_string:
            escape = True
            result.append(char)
            i += 1
            continue
            
        # Toggle string state
        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue
            
        # Check for comment start (only outside strings)
        if not in_string and i < len(text) - 1 and text[i:i+2] == '//':
            # Skip until end of line
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
            
        result.append(char)
        i += 1
    
    return ''.join(result)

def remove_trailing_commas(text):
    """Remove trailing commas before } or ] outside strings."""
    result = []
    in_string = False
    escape = False
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if escape:
            result.append(ch)
            escape = False
            i += 1
            continue

        if ch == '\\' and in_string:
            escape = True
            result.append(ch)
            i += 1
            continue

        if ch == '"':
            in_string = not in_string
            result.append(ch)
            i += 1
            continue

        # If we find a comma outside a string, look ahead for next non-whitespace character.
        if not in_string and ch == ',':
            j = i + 1
            # Skip whitespace (spaces, tabs, newlines, returns)
            while j < n and text[j] in " \t\r\n":
                j += 1
            # If the next non-whitespace char is ] or }, it's a trailing comma -> skip it.
            if j < n and text[j] in ']}':
                i += 1
                # Do not append the comma; continue scanning
                continue
            else:
                result.append(ch)
                i += 1
                continue

        result.append(ch)
        i += 1

    return ''.join(result)

def convert_colors(data):
    """Recursively convert hex colors to RGB arrays"""
    if isinstance(data, dict):
        return {k: convert_colors(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_colors(item) for item in data]
    elif isinstance(data, str) and re.match(r'^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$', data):
        return hex_to_rgb(data)
    return data

# Read JSONC file
with open('manifest (rgb).jsonc', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove comments
content_no_comments = remove_comments(content)

# Remove trailing (redundant) commas like ... ,] or ...,}
content_no_comments = remove_trailing_commas(content_no_comments)

# Parse JSON
data = json.loads(content_no_comments)

# Convert colors
data = convert_colors(data)

# Write to manifest.json
with open('manifest.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("✓ Converted manifest (rgb).jsonc to manifest.json")
