"""Check title/tag formatting only. Does not verify facts or Etsy eligibility."""

import json
import re
import sys
from pathlib import Path

TAG_CHARACTERS = re.compile(
    r"[A-Za-z0-9 ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØŒÙÚÛÜÝÞßàáâãäåæçèéêëìíîïñòóôõöøœùúûüýþÿ'-]+"
)

# Characters AI models often emit that Etsy tags do not accept, mapped to the allowed form.
SMART_CHARACTERS = {
    "’": "'", "‘": "'", "ʼ": "'", "′": "'",
    "–": "-", "—": "-", "‑": "-", "‐": "-",
}


def validate(data):
    errors, warnings = [], []
    result = {"valid": False, "scope": "format_only", "errors": errors, "warnings": warnings}
    if not isinstance(data, dict) or not ({"title", "tags"} & data.keys()):
        errors.append("Provide a JSON object with title and/or tags.")
        return result
    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors.append("Title must be a nonempty string.")
        else:
            result["title_characters"] = len(title)
            result["title_words"] = len(title.split())
            if len(title) > 140:
                errors.append("Title exceeds 140 characters.")
            if "\n" in title or "\r" in title:
                errors.append("Deliver the title on a single line.")
            if len(title.split()) >= 15:
                warnings.append("Consider fewer than 15 words; this is guidance, not a hard limit.")
    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, str):
            if "\n" in tags or "\r" in tags:
                errors.append("Deliver tags on a single comma-separated line.")
            tags = tags.split(",")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append("Tags must be a string list or an English-comma-separated string.")
        else:
            tags = [tag.strip() for tag in tags]
            empty = [i for i, tag in enumerate(tags, 1) if not tag]
            if empty:
                errors.append(
                    f"Found {len(empty)} empty tag(s) at position(s) {empty} - usually an extra or trailing comma. "
                    "Empty entries were removed before the checks below."
                )
                tags = [tag for tag in tags if tag]
            fixes = {}
            for index, tag in enumerate(tags, 1):
                fixed = tag
                for bad, good in SMART_CHARACTERS.items():
                    fixed = fixed.replace(bad, good)
                if fixed != tag:
                    fixes[index] = fixed
            if fixes:
                errors.append(
                    "Curly quotes or dashes found in tag(s) "
                    f"{sorted(fixes)}: replace with a straight apostrophe (') or hyphen (-). "
                    "See suggested_tags_line."
                )
                result["suggested_tags_line"] = ", ".join(fixes.get(i, t) for i, t in enumerate(tags, 1))
            result["tag_count"] = len(tags)
            result["tag_lengths"] = [len(tag) for tag in tags]
            if len(tags) != 13:
                errors.append("This workflow requires exactly 13 tags (Etsy allows up to 13).")
            if len({tag.casefold() for tag in tags}) != len(tags):
                errors.append("Duplicate tags are not allowed in this deliverable.")
            for index, tag in enumerate(tags, 1):
                if not 1 <= len(tag) <= 20:
                    errors.append(f"Tag {index} must contain 1 to 20 characters.")
                if index in fixes:
                    continue  # already reported with a suggested fix
                if not TAG_CHARACTERS.fullmatch(tag) or tag.startswith(("'", "-")):
                    errors.append(f"Tag {index} contains unsupported characters or a leading apostrophe/hyphen.")
            result["tags_line"] = ", ".join(tags)
    result["valid"] = not errors
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_copy.py <candidate.json>", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"valid": False, "scope": "format_only", "errors": ["Cannot read valid UTF-8 JSON."]}))
        return 2
    result = validate(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
