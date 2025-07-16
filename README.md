# urldeduper-py

A fast, minimal and dependency-free CLI tool to **deduplicate**, **normalize**, and **extract components** from large URL lists.

This tool is inspired by and partially overlaps with utilities like [urldedupe](https://github.com/ameenmaali/urldedupe) and [qsreplace](https://github.com/tomnomnom/qsreplace), but combines multiple functionalities into a single script with extended flexibility.

---

## 🔍 Features

- Deduplicates URLs by normalizing dynamic path segments and sorting query keys
- Replaces query values and numeric path segments with a static value (like `FUZZ` or `XSS`)
- Filters out URLs with blacklisted file extensions (e.g. `.jpg`, `.pdf`)
- Extracts:
  - Subdomains
  - Root domains
  - URL paths
  - Query parameter keys
  - Query parameter values

---

## 💡 Why Use This?

When working with recon tools or crawling outputs, URL lists often contain:
- Repetitive entries with minor variations
- File types that are irrelevant for testing
- Query values that clutter analysis

This script solves all that in one go: clean, extract, and normalize your data — ready for fuzzing, scanning, or analysis.

---


## 🧪 Usage Examples

```bash
usage: urldeduper.py [-h] [--replace REPLACE_VALUE] [--blacklist [EXT ...]] [-param | -subdomain | -domain | -path | -data]

URL deduplication and filtering tool with flexible parameter extraction.

options:
  -h, --help            show this help message and exit
  --replace REPLACE_VALUE
                        Replace query param values and numeric path segments with this value
  --blacklist [EXT ...]
                        Blacklist file extensions (e.g. jpg,png,pdf)
  -param                Extract unique query parameter keys
  -subdomain            Extract unique subdomains
  -domain               Extract unique domains
  -path                 Extract unique URL paths
  -data                 Extract unique query parameter values

Examples:

  cat urls.txt | python3 urldeduper.py --replace XSS -param
  cat urls.txt | python3 urldeduper.py -subdomain
  cat urls.txt | python3 urldeduper.py -domain
  cat urls.txt | python3 urldeduper.py -path
  cat urls.txt | python3 urldeduper.py -data
```
