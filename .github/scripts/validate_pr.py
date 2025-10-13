#!/usr/bin/env python3
"""
Validate PR requirements:
1. Check if PR contains .py files
2. Check if corresponding .csv files exist
3. Verify CSV files have at least 10x the lines of the .py files
"""

import os
import sys
from pathlib import Path


def count_lines(file_path):
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def find_corresponding_csv(py_file, changed_files=None):
    """
    Find the corresponding CSV file for a Python file.
    Assumes CSV files are in the 'output/' directory with similar names.
    """
    # Get the base name without extension (handle numbered files like "18.reddit.py")
    base_name = Path(py_file).stem
    
    # Remove leading numbers and dots (e.g., "1. flipkart" -> "flipkart")
    import re
    cleaned_name = re.sub(r'^\d+\.\s*', '', base_name)
    
    # Check common patterns
    possible_csv_files = [
        f"output/{base_name}.csv",
        f"output/{base_name}_data.csv",
        f"output/{base_name.lower()}.csv",
        f"output/{base_name.lower()}_data.csv",
        f"output/{cleaned_name}.csv",
        f"output/{cleaned_name}_data.csv",
        f"output/{cleaned_name.lower()}.csv",
        f"output/{cleaned_name.lower()}_data.csv",
    ]
    
    for csv_file in possible_csv_files:
        if os.path.exists(csv_file):
            return csv_file
    
    # If not found and we have changed files, try to match with CSV files in PR
    if changed_files:
        csv_files_in_pr = [f for f in changed_files if f.endswith('.csv') and os.path.exists(f)]
        if csv_files_in_pr:
            # Try to match by name similarity
            py_base = cleaned_name.lower().replace('_', '').replace('-', '')
            for csv in csv_files_in_pr:
                csv_base = Path(csv).stem.lower().replace('_', '').replace('-', '')
                # Check if the names have significant overlap
                if py_base in csv_base or csv_base in py_base or \
                   any(word in csv_base for word in py_base.split() if len(word) > 3):
                    return csv
    
    return None


def validate_pr():
    """Main validation function."""
    # Get changed files from environment variable
    changed_files_str = os.environ.get('CHANGED_FILES', '')
    
    if not changed_files_str.strip():
        print("[WARNING] No changed files detected in this PR.")
        return True
    
    changed_files = [f.strip() for f in changed_files_str.split('\n') if f.strip()]
    
    print(f"[INFO] Analyzing {len(changed_files)} changed file(s)...\n")
    
    # Filter for .py files (excluding those in special directories)
    py_files = [
        f for f in changed_files 
        if f.endswith('.py') 
        and not f.startswith('.github/')
        and not f.startswith('scrapers/')
        and not f.startswith('webscraper_django/')
        and not any(part.startswith('__') for part in Path(f).parts)
    ]
    
    if not py_files:
        print("[INFO] No Python scraper files found in this PR.")
        print("[PASS] Validation passed (no scraper files to validate).\n")
        return True
    
    print(f"[INFO] Found {len(py_files)} Python scraper file(s):\n")
    for py_file in py_files:
        print(f"   - {py_file}")
    print()
    
    validation_passed = True
    errors = []
    warnings = []
    
    for py_file in py_files:
        print(f"[VALIDATE] Validating: {py_file}")
        
        # Check if the Python file exists
        if not os.path.exists(py_file):
            warnings.append(f"   [WARNING] File was deleted: {py_file}")
            print(f"   [WARNING] File was deleted (skipping validation)")
            continue
        
        # Count lines in Python file
        py_lines = count_lines(py_file)
        print(f"   Python file lines: {py_lines}")
        
        # Find corresponding CSV file
        csv_file = find_corresponding_csv(py_file, changed_files)
        
        if not csv_file:
            # Check if any CSV file was added in the PR
            csv_files_in_pr = [f for f in changed_files if f.endswith('.csv')]
            if csv_files_in_pr:
                print(f"   [WARNING] Could not auto-detect corresponding CSV file.")
                print(f"   [INFO] CSV files in PR: {', '.join(csv_files_in_pr)}")
                # Try to match by name similarity
                py_base = Path(py_file).stem.lower()
                for csv in csv_files_in_pr:
                    csv_base = Path(csv).stem.lower()
                    if py_base in csv_base or csv_base in py_base:
                        csv_file = csv
                        print(f"   [MATCH] Found possible match: {csv_file}")
                        break
        
        if not csv_file:
            validation_passed = False
            error_msg = f"   [ERROR] No corresponding CSV file found for {py_file}"
            errors.append(error_msg)
            print(error_msg)
            print(f"   [HINT] Expected location: output/{Path(py_file).stem}.csv\n")
            continue
        
        print(f"   Corresponding CSV: {csv_file}")
        
        # Check if CSV file exists
        if not os.path.exists(csv_file):
            validation_passed = False
            error_msg = f"   [ERROR] CSV file does not exist: {csv_file}"
            errors.append(error_msg)
            print(error_msg + "\n")
            continue
        
        # Count lines in CSV file
        csv_lines = count_lines(csv_file)
        print(f"   CSV file lines: {csv_lines}")
        
        # Calculate required lines (10x Python file lines)
        required_lines = py_lines * 10
        print(f"   Required CSV lines (10x): {required_lines}")
        
        # Validate the 10x requirement
        if csv_lines < required_lines:
            validation_passed = False
            error_msg = f"   [ERROR] CSV file has insufficient lines: {csv_lines} < {required_lines}"
            errors.append(error_msg)
            print(error_msg)
            print(f"   [HINT] CSV needs at least {required_lines - csv_lines} more lines\n")
        else:
            ratio = csv_lines / py_lines if py_lines > 0 else 0
            print(f"   [PASS] CSV file validation passed! (ratio: {ratio:.1f}x)\n")
    
    # Print summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if warnings:
        print("\n[WARNINGS]")
        for warning in warnings:
            print(warning)
    
    if errors:
        print("\n[ERRORS FOUND]")
        for error in errors:
            print(error)
        print("\n[FIX GUIDE]")
        print("   1. Ensure each Python scraper has a corresponding CSV file")
        print("   2. CSV files should be in the 'output/' directory")
        print("   3. CSV files must have at least 10x the lines of the Python file")
        print("   4. This ensures scrapers are actually producing data")
    else:
        print("\n[SUCCESS] All validations passed!")
    
    print("=" * 60)
    
    return validation_passed


if __name__ == "__main__":
    success = validate_pr()
    sys.exit(0 if success else 1)

