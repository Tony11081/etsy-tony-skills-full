from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "suite.yaml",
    "references/design-theory-framework.md",
    "references/product-dna-taxonomy.md",
    "references/product-architecture.md",
    "references/surface-zone-analysis.md",
    "references/element-style-library.md",
    "references/typography-framework.md",
    "references/color-framework.md",
    "references/composition-and-gestalt.md",
    "references/material-process-matrix.md",
    "references/process-style-compatibility.md",
    "references/manufacturing-engineering-gate.md",
    "references/production-profile-template.md",
    "references/production-file-requirements.md",
    "references/customization-architecture.md",
    "references/option-dependency-rules.md",
    "references/sku-coding-system.md",
    "references/originality-and-ip-rules.md",
    "references/etsy-listing-consistency.md",
    "references/quality-control-framework.md",
    "references/seller-operations-knowledge-base.md",
    "templates/employee-input.md",
    "templates/competitor-analysis.md",
    "templates/evidence-table.md",
    "templates/product-architecture.md",
    "templates/manufacturing-gate.md",
    "templates/design-family-card.md",
    "templates/sku-card.md",
    "templates/custom-options-matrix.md",
    "templates/option-dependency-matrix.md",
    "templates/manufacturing-card.md",
    "templates/sample-test-plan.md",
    "templates/qc-checklist.md",
    "templates/listing-launch-pack.md",
    "templates/quality-scorecard.md",
    "templates/sku-distinctness-matrix.md",
    "templates/seller-knowledge-update.md",
    "examples/wedding-cake-server.md",
    "examples/embroidered-pennant.md",
    "examples/wooden-sign.md",
    "examples/apparel-product.md",
    "examples/acrylic-product.md",
    "examples/long-name-stress-test.md",
    "examples/seller-operations-decision.md",
]

CHILD_SKILLS = [
    "etsy-tony-full-product-development",
    "etsy-tony-full-competitor",
    "etsy-tony-full-manufacturing",
    "etsy-tony-full-design-system",
    "etsy-tony-full-skus",
    "etsy-tony-full-launch-pack",
    "etsy-tony-full-seller-operations",
]

FULL_SECTIONS = [
    "01 Input Summary",
    "02 Evidence Table",
    "03 Product Understanding",
    "04 Buyer and Purchase Motivation",
    "05 Competitor Listing Consistency",
    "06 Product Architecture",
    "07 Product Surface and Functional Zones",
    "08 Material Analysis",
    "09 Manufacturing Engineering Gate",
    "10 Material–Process Compatibility",
    "11 Process–Style Compatibility",
    "12 Competitor Design DNA",
    "13 Design Elements",
    "14 Element Style Expansion",
    "15 Typography System",
    "16 Graphic Style System",
    "17 Color System",
    "18 Placement System",
    "19 Composition System",
    "20 Design Theory Assessment",
    "21 Style Compatibility Matrix",
    "22 Design Families",
    "23 SKUs Generation Strategy",
    "24 Generated SKUs",
    "25 Custom Options Structure",
    "26 Option Dependency Rules",
    "27 Manufacturing Cards",
    "28 Production File Requirements",
    "29 Sample Test Plans",
    "30 QC Checklists",
    "31 Originality Distance Check",
    "32 Listing Launch Pack",
    "33 Listing Consistency Check",
    "34 Scores and Ranking",
    "35 Top 5 Recommended SKUs",
    "36 Employee Action List",
]


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size < 120:
            errors.append(f"file is too small to be operational: {rel}")

    for child in CHILD_SKILLS:
        for rel in ("SKILL.md", "agents/openai.yaml"):
            path = root.parent / child / rel
            if not path.is_file():
                errors.append(f"missing child skill file: skills/{child}/{rel}")

    markdown = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.rglob("*.md")
        if path.is_file()
    )
    if re.search(r"\bSKU['’]s\b", markdown, flags=re.IGNORECASE):
        errors.append("forbidden plural spelling found")
    if "[TODO" in markdown or "TODO:" in markdown:
        errors.append("unfinished TODO marker found")

    for source in [root / "SKILL.md", root / "README.md"]:
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken relative link in {source.name}: {target}")

    main_skill = (root / "SKILL.md").read_text(encoding="utf-8")
    process_index = main_skill.find("Manufacturing gate")
    design_index = main_skill.find("Design and originality gates")
    if process_index < 0 or design_index < 0 or process_index > design_index:
        errors.append("manufacturing gate is not visibly before design")

    seller_reference = root / "references" / "seller-operations-knowledge-base.md"
    if seller_reference.is_file():
        seller_text = seller_reference.read_text(encoding="utf-8")
        required_seller_terms = [
            "Current Official Policy",
            "Internal Business Rule",
            "Empirical Observation",
            "Historical Snapshot",
            "Unverified / High Risk",
            "accounts are not transferable",
            "new shops cannot open in China",
            "accurate ships-from",
            "production partner",
            "Delivery Duty Paid",
            "出口易 SUR",
            "燕文",
            "2026-08-29",
            "41,937",
            "Do not automate or recommend",
            "Daily update protocol",
        ]
        missing_seller_terms = [term for term in required_seller_terms if term not in seller_text]
        if missing_seller_terms:
            errors.append(f"seller operations reference missing: {', '.join(missing_seller_terms)}")
        required_quarantine_terms = [
            "buying, transferring, or taking over an Etsy account",
            "proxy/fingerprint setup intended to appear in another country",
            "US postal codes chosen from IP location",
            "tracking chosen to hide the real origin or route",
        ]
        quarantine_start = seller_text.find("## 11. Quarantined actions and claims")
        quarantine_end = seller_text.find("## 12. Daily update protocol")
        quarantine = seller_text[quarantine_start:quarantine_end] if quarantine_start >= 0 and quarantine_end > quarantine_start else ""
        missing_quarantine = [term for term in required_quarantine_terms if term not in quarantine]
        if missing_quarantine:
            errors.append(f"seller operations quarantine missing: {', '.join(missing_quarantine)}")

        seller_hard_gates = [
            "Etsy accounts are not transferable",
            "identity, bank, tax, payment, and recovery records",
            "not a safe-harbor period",
            "IP is not fulfillment evidence",
            "Do not select a US postal code based on operating IP",
            "do not state that it ships from the United States",
            "must not be selected to hide the real origin or route",
        ]
        missing_hard_gates = [term for term in seller_hard_gates if term not in seller_text]
        if missing_hard_gates:
            errors.append(f"seller operations hard gate missing: {', '.join(missing_hard_gates)}")

    seller_example = root / "examples" / "seller-operations-decision.md"
    if seller_example.is_file():
        example_text = seller_example.read_text(encoding="utf-8")
        red_team_markers = [
            "Account Acquisition Claim",
            "Three-Day Survival Claim",
            "Third-Party Payout Proposal",
            "IP-Derived Postal Code",
            "False Ships-From",
            "Route-Concealment Purpose",
            "Carrier Candidate Is Not Approval",
            "PROHIBITED / DO NOT IMPLEMENT",
            "这不表示原方案被批准",
        ]
        missing_markers = [term for term in red_team_markers if term not in example_text]
        if missing_markers:
            errors.append(f"seller operations red-team example missing: {', '.join(missing_markers)}")

    example_path = root / "examples" / "wedding-cake-server.md"
    if example_path.is_file():
        example = example_path.read_text(encoding="utf-8")
        def section_body(number: int) -> str:
            marker = f"## {number:02d} "
            start = example.find(marker)
            if start < 0:
                return ""
            next_start = example.find(f"## {number + 1:02d} ", start + len(marker))
            return example[start:] if next_start < 0 else example[start:next_start]

        for section_name in FULL_SECTIONS:
            if f"## {section_name}" not in example:
                errors.append(f"wedding example missing section: {section_name}")
        sku_ids = set(re.findall(r"\bCS-[A-Z0-9-]+-\d{2}\b", example))
        if len(sku_ids) < 20:
            errors.append(f"wedding example has {len(sku_ids)} unique SKU codes; expected at least 20")
        top_cards = len(re.findall(r"^### Manufacturing Card — Top ", example, flags=re.MULTILINE))
        if top_cards != 5:
            errors.append(f"wedding example has {top_cards} top manufacturing cards; expected 5")
        card_codes = set(re.findall(r"\bCS-[A-Z0-9-]+-\d{2}\b", section_body(27)))
        if len(card_codes) != 20:
            errors.append(f"manufacturing card section covers {len(card_codes)} SKUs; expected 20")
        sample_codes = set(re.findall(r"\bCS-[A-Z0-9-]+-\d{2}\b", section_body(29)))
        if len(sample_codes) != 5:
            errors.append(f"sample plan section covers {len(sample_codes)} recommended SKUs; expected 5")
        qc_codes = set(re.findall(r"\bCS-[A-Z0-9-]+-\d{2}\b", section_body(30)))
        if len(qc_codes) != 5:
            errors.append(f"QC section covers {len(qc_codes)} recommended SKUs; expected 5")
        top_codes = set(re.findall(r"^\d+\. (CS-[A-Z0-9-]+-\d{2})", section_body(35), flags=re.MULTILINE))
        detail_card_codes = set(re.findall(r"^### Manufacturing Card — Top \d+: (CS-[A-Z0-9-]+-\d{2})", section_body(27), flags=re.MULTILINE))
        if len(top_codes) != 5:
            errors.append(f"Top recommendation section has {len(top_codes)} unique SKUs; expected 5")
        if detail_card_codes != top_codes:
            errors.append("detailed manufacturing card SKUs do not exactly match Top 5")
        if sample_codes != top_codes:
            errors.append("sample plan SKUs do not exactly match Top 5")
        if qc_codes != top_codes:
            errors.append("QC-linked SKUs do not exactly match Top 5")

        family_members = {
            "VB": {"01", "02", "03", "04", "05"},
            "MM": {"06", "07", "08", "09", "10"},
            "CG": {"11", "12", "13", "14", "15"},
            "AD": {"16", "17", "18", "19", "20"},
        }
        pair_rows = re.findall(
            r"^\| (VB|MM|CG|AD) \| (\d{2}) ↔ (\d{2}) \| ([^|]+) \| Pass \|$",
            section_body(23),
            flags=re.MULTILINE,
        )
        observed_pairs: dict[str, set[tuple[str, str]]] = {family: set() for family in family_members}
        axis_patterns = [
            r"buyer|market|intent|occasion|couple|family|wedding",
            r"hierarchy|primary|secondary",
            r"composition|L01|L02|vertical|horizontal|radial|symmetric|asymmetric|corner|arch|flow|register|frame|horizon|emblem",
            r"personalization|ordering|fields|proof|monogram|coordinates|long-name|full names|initials",
            r"process|material|placement|zone|risk",
        ]
        for family, left, right, differences in pair_rows:
            pair = tuple(sorted((left, right)))
            if left == right or left not in family_members[family] or right not in family_members[family]:
                errors.append(f"invalid sibling pair: {family} {left}/{right}")
            observed_pairs[family].add(pair)
            axis_count = sum(bool(re.search(pattern, differences, flags=re.IGNORECASE)) for pattern in axis_patterns)
            if axis_count < 2:
                errors.append(f"sibling pair lacks two auditable axes: {family} {left}/{right}")
        for family, members in family_members.items():
            expected_pairs = {
                tuple(sorted((left, right)))
                for index, left in enumerate(sorted(members))
                for right in sorted(members)[index + 1 :]
            }
            if observed_pairs[family] != expected_pairs:
                errors.append(f"sibling pair matrix is incomplete or duplicated for {family}")

        card_blocks = re.findall(
            r"^### Manufacturing Card — Top \d+: (CS-[A-Z0-9-]+-\d{2})\n(.*?)(?=^### Manufacturing Card — Top |^## 28 |\Z)",
            section_body(27),
            flags=re.MULTILINE | re.DOTALL,
        )
        if len(card_blocks) != 5:
            errors.append(f"parsed {len(card_blocks)} detailed manufacturing card blocks; expected 5")
        required_card_terms = [
            "Components",
            "Material",
            "Zone",
            "Primary",
            "Secondary",
            "Finishing",
            "Assembly",
            "Packaging",
            "File",
            "Machine Profile",
            "Sample",
            "Complexity",
            "Manual",
            "QC",
            "Risk",
            "Rework",
            "Cost",
            "Time",
            "Production Approval",
        ]
        for code, block in card_blocks:
            missing_terms = [term for term in required_card_terms if term.lower() not in block.lower()]
            if missing_terms:
                errors.append(f"detailed manufacturing card {code} missing: {', '.join(missing_terms)}")
        tag_lines = re.findall(r"^Tags \(13\): (.+)$", example, flags=re.MULTILINE)
        if len(tag_lines) < 5:
            errors.append("wedding example needs five Top-SKU tag lines")
        for index, line in enumerate(tag_lines, start=1):
            tags = [item.strip() for item in line.split(",") if item.strip()]
            if len(tags) != 13:
                errors.append(f"tag line {index} has {len(tags)} tags")
            for tag in tags:
                if len(tag) > 20:
                    errors.append(f"tag exceeds 20 characters: {tag}")

    if errors:
        print("AUDIT FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("AUDIT PASSED")
    print(f"- root: {root}")
    print(f"- required files: {len(REQUIRED_FILES)}")
    print(f"- child skills: {len(CHILD_SKILLS)}")
    print("- terminology, ordering, seller-operations policy precedence and quarantine, FULL sections, 40 unique sibling pairs, 20 cards, Top 5 card/sample/QC identity, card fields, scores, and tags passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
