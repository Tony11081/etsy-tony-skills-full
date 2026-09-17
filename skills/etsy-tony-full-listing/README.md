# Etsy Listing Optimizer

A Codex skill for Etsy listing SEO and conversion work.

It helps diagnose Etsy titles, rewrite English listing titles, generate Etsy-ready tags, improve product descriptions, review image/click-through strategy, and give practical positioning advice for furniture and custom decor listings.

## What It Does

- Scores Etsy title and SEO quality.
- Rewrites product titles with the strongest keywords early.
- Generates exactly 13 Etsy-ready tags by default.
- Reviews listing images, first-image click-through quality, and missing product shots.
- Scores description/CRO quality and rewrites the opening copy.
- Gives practical pricing, positioning, customization, and Etsy Ads suggestions.
- Includes safety rules for uncertain claims such as `solid wood`, `glider`, `handmade`, branded terms, and medical/orthopedic language.
- Searches a bundled 945-record Etsy Seller Handbook reference knowledge base and passes relevant official summaries and URLs to Gemini.

## Install

Copy this folder into your Codex skills directory:

```powershell
$skillsDir = "$env:USERPROFILE\.codex\skills"
git clone https://github.com/Tony11081/etsy-tony-full-listing.git "$skillsDir\etsy-tony-full-listing"
```

Restart Codex after installing so the skill appears in the available skills list.

## Use

In Codex, invoke:

```text
$etsy-tony-full-listing
```

Then send the product data you want reviewed, such as:

- Current title
- Tags
- Description
- Product photos or image descriptions
- Price
- Materials
- Size
- Production time
- Shipping details
- Customization options

## Output

The default diagnosis uses Chinese analysis and English Etsy-facing listing assets:

- Title/SEO diagnosis
- 3 optimized English titles
- 13 Etsy tags on one comma-separated line
- Visual merchandising advice
- Description/CRO diagnosis
- Rewritten first three description lines
- Competitive strategy
- Important missing facts to confirm

## Notes

The bundled Seller Handbook knowledge base is a dated index-and-summary snapshot, not
a full-text mirror. The client reports the exact reference hits it used. Current Etsy
policy, fees, legal, tax, product-safety, and platform-change claims must still be
verified against the live official Etsy Seller Handbook or Etsy Help Center before action.
