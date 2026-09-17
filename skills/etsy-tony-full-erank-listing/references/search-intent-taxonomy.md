# Customer Search Intent Taxonomy

Use Gemini to expand how US Etsy buyers may describe the product, then use eRank member data to validate the phrases. Do not invent demographic certainty or demand metrics.

## Intent classes

- `product`: the clear item noun or product family.
- `objective_trait`: material, color, size, finish, shape, or construction that is factually supported.
- `style`: design identity such as mid century, rustic, minimalist, or modern when visually and factually supportable.
- `room_use`: room, placement, or practical use such as nursery, reading nook, or small-space storage.
- `problem_solution`: the buyer's practical constraint or desired outcome, such as narrow, space-saving, washable, or personalized, only when the product supports it.
- `recipient_occasion`: recipient, event, holiday, or gift intent. Keep out of the title unless essential to the item.
- `personalization`: name, initials, pattern, embroidery, print, or other confirmed customization.
- `regional_synonym`: natural US-market alternatives and category vocabulary.
- `seasonal`: time-sensitive phrases that require current Trend Buzz or seasonal evidence.

## Search stages

- `discovery`: broad category exploration.
- `consideration`: product plus objective differentiators.
- `high_intent`: specific phrases indicating a buyer knows what they want.
- `seasonal`: event-driven or time-sensitive discovery.

## Gemini intent output

Generate 20-40 distinct English phrases when the product supports enough variation. For each phrase return:

- `phrase`
- `intent`
- `search_stage`
- `product_relevance`: `high`, `medium`, or `low`
- `fact_supported`: boolean
- `rationale`: concise Chinese explanation
- `evidence_status`: initially `GEMINI_HYPOTHESIS`

Reject or flag phrases that:

- require an unsupported product fact;
- are broad enough to describe a materially different product;
- rely on a protected brand, designer, celebrity, or copyrighted property;
- express a feature buyers would reasonably expect but the product lacks;
- use an occasion or recipient only to chase volume;
- duplicate another phrase without adding intent.

## Portfolio principles

- Apply product truth as a hard gate before considering demand.
- Choose a primary phrase that clearly names the product and has qualified demand.
- Balance core demand with narrower high-intent phrases; do not select only the highest raw search-volume terms.
- Use competitor tags as candidate discovery, not proof of keyword demand or listing-level sales.
- Use Shop Stats queries as first-party evidence for an existing listing.
- Preserve raw metrics and reasoning so the selection is explainable and reversible.
