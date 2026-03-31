#!/usr/bin/env python3
"""
CLI tool for Rotkeeper to check markdown files for missing/None metadata
and dump a report.
"""

import os
import yaml
import glob
import argparse

def scan_md_files(source_dir, output_file):
    report = []
    md_files = glob.glob(os.path.join(source_dir, "**/*.md"), recursive=True)
    
    for path in md_files:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # frontmatter detection
        if lines and lines[0].strip() == "---":
            end_idx = None
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    end_idx = i
                    break
            if end_idx is None:
                report.append(f"{path}: frontmatter not closed")
                continue
            
            frontmatter_text = "".join(lines[1:end_idx])
            try:
                data = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError as e:
                report.append(f"{path}: YAML parse error: {e}")
                continue

            missing_fields = []
            for field in ["title", "tags", "author", "date"]:
                if not data or field not in data or data[field] is None:
                    missing_fields.append(field)
            if missing_fields:
                report.append(f"{path}: missing {', '.join(missing_fields)}")
    
    if report:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("\n".join(report))
    else:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("No issues found.\n")

def main():
    parser = argparse.ArgumentParser(description="Degum markdown frontmatter")
    parser.add_argument("--source", required=True, help="Directory of markdown files")
    parser.add_argument("--output", required=True, help="Output report file")
    args = parser.parse_args()

    scan_md_files(args.source, args.output)
    print(f"Scan complete. Report written to {args.output}")

def add_parser(subparsers):
    parser = subparsers.add_parser(
        "degumfrontmatter",
        help="Check markdown files for missing/None frontmatter metadata and dump a report"
    )
    parser.add_argument("--source", required=True, help="Directory of markdown files")
    parser.add_argument("--output", required=True, help="Output report file")
    parser.set_defaults(func=lambda args, ctx: scan_md_files(args.source, args.output) or print(f"Scan complete. Report written to {args.output}"))

if __name__ == "__main__":
    main()