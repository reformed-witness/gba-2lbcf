#!/usr/bin/env python3
"""
Simple GBA header fixer - calculates the complement check
Run this if gbafix is not available
Usage: python3 fix_header.py confession.gba
"""

import sys

def fix_gba_header(filename):
    try:
        with open(filename, 'r+b') as f:
            # Read the header
            f.seek(0xA0)  # Start of header area
            header = f.read(29)  # Read 29 bytes (excluding complement check)
            
            # Calculate complement
            checksum = 0
            for byte in header:
                checksum += byte
            
            # Calculate complement check (should make lower 8 bits = 0)
            complement = (0x100 - (checksum & 0xFF)) & 0xFF
            
            # Write complement check at offset 0xBD
            f.seek(0xBD)
            f.write(bytes([complement]))
            
            print(f"Fixed GBA header for {filename}")
            print(f"Checksum: 0x{checksum:02X}")
            print(f"Complement: 0x{complement:02X}")
            
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

def check_rom_size(filename):
    try:
        import os
        size = os.path.getsize(filename)
        print(f"ROM size: {size} bytes ({size/1024:.1f} KB)")
        
        if size < 1024:
            print("Warning: ROM seems very small, might be incomplete")
        
        return True
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fix_header.py <rom_file.gba>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    print(f"Fixing GBA header for: {filename}")
    check_rom_size(filename)
    
    if fix_gba_header(filename):
        print("Header fixed successfully!")
        print("ROM should now load in emulators.")
    else:
        print("Failed to fix header.")
        sys.exit(1)