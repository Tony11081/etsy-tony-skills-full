"""List registered, readable Etsy skill definitions without reading any settings."""
import argparse
import json
from pathlib import Path
import re


def scalar(value):
    value = value.strip()
    if not value or value in ('|', '>'):
        raise ValueError('Expected a nonempty single-line field')
    if value.startswith('"'):
        result = json.loads(value)
        if not isinstance(result, str) or not result.strip():
            raise ValueError('Expected a string field')
        return result
    if value.startswith("'"):
        if not value.endswith("'"):
            raise ValueError('Unterminated field')
        return value[1:-1].replace("''", "'")
    return value


def discover(root, catalog):
    root = root.resolve()
    skills, issues, seen = [], [], set()
    for entry in catalog:
        name = entry.get('name', '')
        if not isinstance(name, str):
            issues.append(dict(name='', path='', issue='Invalid catalog name'))
            continue
        try:
            if name in seen:
                raise ValueError('Duplicate catalog name')
            seen.add(name)
            path = (root / entry['path']).resolve()
            if not path.is_relative_to(root) or path.name != 'SKILL.md':
                raise ValueError('Path outside skill root or not SKILL.md')
            text = path.read_text(encoding='utf-8-sig')
            match = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', text, re.S)
            if not match:
                raise ValueError('Missing frontmatter')
            fields = dict(re.findall(r'^(name|description):[ \t]*(.+)$', match[1], re.M))
            actual = scalar(fields['name'])
            description = scalar(fields['description'])
            if actual != name or path.parent.name != name:
                raise ValueError('Catalog, folder and frontmatter names differ')
            skills.append(dict(name=name, description=description, path=str(path)))
        except (OSError, UnicodeError, ValueError, KeyError, TypeError):
            issues.append(dict(name=name, path=entry.get('path', ''), issue='Missing, conflicting or invalid definition'))
    conflicts = {i['name'] for i in issues}
    return dict(skills=[s for s in skills if s['name'] not in conflicts], issues=issues,
                note='Filesystem discovery only; enabled state and tool availability must be checked in the current session.')


def main():
    skill_dir = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=skill_dir.parent)
    parser.add_argument('--catalog', type=Path, default=skill_dir / 'references/catalog.json')
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding='utf-8'))
        if not isinstance(catalog, list) or any(not isinstance(e, dict) for e in catalog):
            raise ValueError('Catalog must be a list of records')
        result = discover(args.root, catalog)
    except (OSError, UnicodeError, ValueError):
        print(json.dumps(dict(skills=[], issues=['Catalog unavailable or invalid'])))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['skills'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
