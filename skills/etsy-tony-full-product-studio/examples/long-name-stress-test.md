# Long-Name Stress Test

Use confirmed artwork zones and machine samples. The examples below define layout behavior, not untested minimum sizes.

## Test strings

| Case | Example | Required check |
|---|---|---|
| 4 characters | LENA | does not look undersized or lost |
| 10 characters | ALEXANDRIA | standard width and counter readability |
| 15 characters | CHRISTOPHERSON | long-state font/layout without unsafe shrinking |
| Two names | ALEXANDRIA & BENJAMIN | separator, hierarchy, two-line option |
| Surname | THE MONTGOMERYS | plural/case/width and family-name semantics |
| Date | SEPTEMBER 28, 2026 | permitted date format and secondary hierarchy |
| Multiline | ALEXANDRIA / & BENJAMIN / 09.28.2026 | line spacing, grouping, total height |
| Punctuation | O’NEILL-SMITH | apostrophe/hyphen glyph support |
| Accents | JOSÉ & CHLOË | supported characters in font and production file |

## Layout states

- Short: keep designed scale and add tracking/negative space; do not expand to edge limits.
- Medium: standard single-line or family composition.
- Long: switch to the approved long-name font or two-line layout; simplify secondary motif if needed.
- Dual names: use a dedicated relationship, not two independently scaled fields.
- Over limit: proof required, alternate layout, shorter requested text, or Not Offered.

## Dependency rules

- Name length → approved font and layout state.
- Layout state → allowed pattern and decoration density.
- Product size → maximum line count/detail.
- Process → minimum tested text behavior and file.
- Unsupported glyph → approved fallback font or manual proof.

## Acceptance

Each test passes readability at intended viewing distance, hierarchy, negative space, edge clearance, process reproduction, spelling/glyphs, and employee repeatability. Record sample photo, physical dimensions, machine profile, file version, and reviewer.

Do not set a maximum character count until tested layouts and the actual Product zone establish it.
