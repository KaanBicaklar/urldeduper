#!/usr/bin/env python3
import sys
import argparse
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def prepare_blacklist(blacklist_args):
    ext_set = set()
    for ext in blacklist_args:
        ext_set.update({f".{e.strip().lower()}" for e in ext.split(',') if e.strip()})
    return ext_set


def is_blacklisted(url, ext_set):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in ext_set)
    except Exception:
        return False


def normalize_url(url):
    try:
        parsed = urlparse(url.strip())
        path_parts = parsed.path.strip('/').split('/')
        norm_path = '/' + '/'.join(['{id}' if part.isdigit() else part for part in path_parts])
        query_keys = tuple(sorted(k for k, _ in parse_qsl(parsed.query, keep_blank_values=True)))
        norm_tuple = (
            parsed.scheme,
            parsed.netloc,
            norm_path,
            parsed.params,
            query_keys,
            parsed.fragment
        )
        return norm_tuple
    except Exception:
        return ()


def dedupe_urls(urls):
    seen = set()
    unique = []
    for url in urls:
        key = normalize_url(url)
        if key and key not in seen:
            seen.add(key)
            unique.append(url.strip())
    return unique


def qsreplace_with_path(url, replace_value):
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        def replace_if_id(part):
            if part.isdigit() and len(part) not in (2, 4):
                return replace_value
            return part

        new_path = '/' + '/'.join([replace_if_id(part) for part in path_parts])
        query = parse_qsl(parsed.query, keep_blank_values=True)
        replaced_query = [(k, replace_value) for k, _ in query]
        new_query = urlencode(replaced_query)

        modified_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        return modified_url.strip()
    except Exception:
        return url.strip()


def extract_data(urls, mode):
    results = set()
    for url in urls:
        try:
            parsed = urlparse(url)
            host_parts = parsed.netloc.split('.')
            if mode == "subdomain":
                if len(host_parts) > 2:
                    subdomain = '.'.join(host_parts[:-2])
                    results.add(subdomain)
            elif mode == "domain":
                if len(host_parts) >= 2:
                    domain = '.'.join(host_parts[-2:])
                    results.add(domain)
            elif mode == "path":
                results.add(parsed.path)
            elif mode == "param":
                for k, _ in parse_qsl(parsed.query, keep_blank_values=True):
                    results.add(k)
            elif mode == "data":
                for _, v in parse_qsl(parsed.query, keep_blank_values=True):
                    results.add(v)
        except Exception:
            continue
    return sorted(results)


def main():
    parser = argparse.ArgumentParser(
        description="URL deduplication and filtering tool with flexible parameter extraction.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:

  cat urls.txt | python3 urldeduper.py --replace XSS -param
  cat urls.txt | python3 urldeduper.py -subdomain
  cat urls.txt | python3 urldeduper.py -domain
  cat urls.txt | python3 urldeduper.py -path
  cat urls.txt | python3 urldeduper.py -data
"""
    )

    parser.add_argument('--replace', metavar='REPLACE_VALUE', type=str,
                        help='Replace query param values and numeric path segments with this value')
    parser.add_argument('--blacklist', metavar='EXT', nargs='*', default=[],
                        help='Blacklist file extensions (e.g. jpg,png,pdf)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-param', action='store_true', help='Extract unique query parameter keys')
    group.add_argument('-subdomain', action='store_true', help='Extract unique subdomains')
    group.add_argument('-domain', action='store_true', help='Extract unique domains')
    group.add_argument('-path', action='store_true', help='Extract unique URL paths')
    group.add_argument('-data', action='store_true', help='Extract unique query parameter values')

    args = parser.parse_args()

    if sys.stdin.isatty():
        parser.print_help()
        sys.exit(0)

    blacklist_exts = prepare_blacklist(args.blacklist)

    input_urls = [line.strip() for line in sys.stdin if line.strip()]
    filtered_urls = [url for url in input_urls if not is_blacklisted(url, blacklist_exts)]
    unique_urls = dedupe_urls(filtered_urls)

    if args.replace:
        replaced_urls = [qsreplace_with_path(url, args.replace) for url in unique_urls]
    else:
        replaced_urls = unique_urls

    extract_mode = None
    if args.param:
        extract_mode = "param"
    elif args.subdomain:
        extract_mode = "subdomain"
    elif args.domain:
        extract_mode = "domain"
    elif args.path:
        extract_mode = "path"
    elif args.data:
        extract_mode = "data"

    if extract_mode:
        results = extract_data(replaced_urls, extract_mode)
        for item in results:
            print(item)
        return

    for url in replaced_urls:
        print(url)


if __name__ == '__main__':
    main()
