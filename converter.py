#!/usr/bin/env python3
"""
Convert Baptist Confession JSON to GBA-friendly C array format
Each line limited to 27 characters to fit on screen with scrollbar
"""

import json
import textwrap
import re

def wrap_text(text, width=27):
    """Wrap text to specified width, handling punctuation intelligently"""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Use textwrap but also split on punctuation when needed
    lines = []
    
    # First pass: basic word wrapping
    wrapped = textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    
    # Second pass: check for lines that are still too long and split them better
    for line in wrapped:
        if len(line) <= width:
            lines.append(line)
        else:
            # Try to split on punctuation
            words = line.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= width:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                    
                    # If even a single word is too long, force break it
                    if len(current_line) > width:
                        while len(current_line) > width:
                            lines.append(current_line[:width-1] + "-")
                            current_line = current_line[width-1:]
            
            if current_line:
                lines.append(current_line)
    
    return lines

def convert_json_to_c_array(json_file, output_file):
    """Convert JSON confession to C array format"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    
    # Add title
    title = data.get('title', 'Baptist Confession of Faith')
    title_lines = wrap_text(title.upper())
    lines.extend(title_lines)
    lines.append("")  # Empty line
    
    # Process each chapter
    chapters = data.get('chapters', {})
    
    for chapter_num in sorted(chapters.keys(), key=int):
        chapter = chapters[chapter_num]
        chapter_title = chapter.get('title', f'Chapter {chapter_num}')
        
        # Add chapter header
        header = f"CHAPTER {chapter_num}: {chapter_title.upper()}"
        header_lines = wrap_text(header)
        lines.extend(header_lines)
        lines.append("")  # Empty line after chapter title
        
        # Process paragraphs
        paragraphs = chapter.get('paragraphs', {})
        
        for para_num in sorted(paragraphs.keys(), key=int):
            paragraph_text = paragraphs[para_num]
            
            # Add paragraph number
            lines.append(f"{para_num}.")
            
            # Clean up the paragraph text
            # Replace special quotes and characters
            paragraph_text = paragraph_text.replace('"', '"').replace('"', '"')
            paragraph_text = paragraph_text.replace(''', "'").replace(''', "'")
            paragraph_text = paragraph_text.replace('—', '-').replace('–', '-')
            
            # Split on existing newlines first
            sections = paragraph_text.split('\n\n')
            
            for section in sections:
                if section.strip():
                    section_lines = wrap_text(section.strip())
                    lines.extend(section_lines)
                    
                    # Add empty line between sections within a paragraph
                    if len(sections) > 1:
                        lines.append("")
            
            lines.append("")  # Empty line after each paragraph
        
        lines.append("")  # Extra empty line after each chapter
    
    # Generate C array
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Generated Baptist Confession text for GBA\n")
        f.write("// Each line limited to 27 characters\n\n")
        f.write("static const char* confession_text[] = {\n")
        
        for i, line in enumerate(lines):
            # Escape quotes and backslashes
            escaped_line = line.replace('\\', '\\\\').replace('"', '\\"')
            
            # Ensure line doesn't exceed 27 characters
            if len(escaped_line) > 27:
                print(f"Warning: Line {i+1} exceeds 27 chars: '{escaped_line}' ({len(escaped_line)} chars)")
            
            f.write(f'    "{escaped_line}"')
            if i < len(lines) - 1:
                f.write(',')
            f.write('\n')
        
        f.write("};\n\n")
        f.write(f"static int total_lines = {len(lines)};\n")
    
    print(f"Converted {len(lines)} lines to {output_file}")
    print(f"Processed {len(chapters)} chapters")
    
    # Show some statistics
    max_line_length = max(len(line) for line in lines)
    avg_line_length = sum(len(line) for line in lines) / len(lines)
    
    print(f"Max line length: {max_line_length} characters")
    print(f"Average line length: {avg_line_length:.1f} characters")
    
    # Show lines that are exactly at or near the limit
    long_lines = [line for line in lines if len(line) >= 25]
    if long_lines:
        print(f"\nLines near 27-char limit ({len(long_lines)} total):")
        for line in long_lines[:10]:  # Show first 10
            print(f"  ({len(line):2d}) '{line}'")
        if len(long_lines) > 10:
            print(f"  ... and {len(long_lines) - 10} more")

def create_updated_confession_c(input_c_file, confession_array_file, output_c_file):
    """Update the original confession.c file with new text array"""
    
    with open(confession_array_file, 'r', encoding='utf-8') as f:
        new_array = f.read()
    
    with open(input_c_file, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Find the confession_text array and replace it
    start_marker = "static const char* confession_text[] = {"
    end_marker = "};"
    
    start_idx = original_code.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find confession_text array in original file")
        return False
    
    # Find the end of the array
    end_idx = original_code.find(end_marker, start_idx)
    if end_idx == -1:
        print("Error: Could not find end of confession_text array")
        return False
    
    end_idx += len(end_marker)
    
    # Also update the total_lines variable
    total_lines_start = original_code.find("static int total_lines = ")
    if total_lines_start != -1:
        total_lines_end = original_code.find(";", total_lines_start) + 1
        
        # Replace both the array and total_lines
        new_code = (original_code[:start_idx] + 
                   new_array.strip() + 
                   original_code[total_lines_end:])
    else:
        # Just replace the array
        new_code = (original_code[:start_idx] + 
                   new_array.strip() + "\n\n" +
                   original_code[end_idx:])
    
    with open(output_c_file, 'w', encoding='utf-8') as f:
        f.write(new_code)
    
    print(f"Updated C file written to {output_c_file}")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 convert_json.py <json_file> [output_file]")
        print("Example: python3 convert_json.py confession.json confession_text.c")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "confession_text.c"
    
    try:
        convert_json_to_c_array(json_file, output_file)
        
        # If confession.c exists, offer to update it
        try:
            updated_file = "confession_updated.c"
            if create_updated_confession_c("confession.c", output_file, updated_file):
                print(f"\nAlso created updated confession file: {updated_file}")
                print("You can replace your original confession.c with this file.")
        except FileNotFoundError:
            print("\nTo use this data, replace the confession_text array in your confession.c file")
            print(f"with the contents of {output_file}")
    
    except FileNotFoundError:
        print(f"Error: Could not find {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)