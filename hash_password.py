#!/usr/bin/env python3
"""
SortRight - Password Hash Helper Utility
Securely generates a bcrypt password hash using getpass without echoing or saving the password.
"""
import sys
import getpass
import bcrypt

def main():
    try:
        pw1 = getpass.getpass("Enter password to hash (input will be hidden): ")
        if not pw1:
            print("Error: Password cannot be empty.", file=sys.stderr)
            sys.exit(1)
            
        pw2 = getpass.getpass("Confirm password (input will be hidden): ")
        if pw1 != pw2:
            print("Error: Passwords do not match.", file=sys.stderr)
            sys.exit(1)
            
        # Generate bcrypt hash with cost factor 12
        hashed = bcrypt.hashpw(pw1.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        
        # Clear variables from memory
        pw1 = None
        pw2 = None
        
        print("\nGenerated bcrypt hash (copy this for MUNICIPALITY_PASSWORD_HASH or RECYCLER_PASSWORD_HASH):")
        print(hashed)
        
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
