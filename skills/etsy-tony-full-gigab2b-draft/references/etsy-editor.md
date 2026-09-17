# Etsy Copy-to-Draft Editor Contract

Use this reference immediately before any Etsy Listings write.

## Allowed Editor Sections

Modify only these four sections when copying a same-category listing:

1. `Photo & Video`
2. `Item Details`
3. `Item Options`
4. `Pricing & Delivery`

Do not change `How It's Made` or `Settings`.

## Photo & Video

- For unattended work, copy only a dedicated same-category master with zero photos. If Etsy cannot retain a zero-photo master, start a blank listing and set the verified category and approved delivery profile.
- Treat any copied photo, tag, variation, custom field, material, color, or dimension as a template-integrity failure. Do not enter an unattended cleanup path.
- Upload the 15 verified `final-01.png` through `final-15.png` files. When `final-images` has already passed the exact-count gate and contains only those 15 accepted files, use the Windows file picker address bar to open that folder, press `Ctrl+A`, and upload the entire folder selection in one action. Do not paste a long list of absolute paths into the filename field; Windows may silently truncate the selection.
- Wait for uploads to settle, then read the actual accepted image count. If the count is wrong, visually identify the accepted thumbnails and upload only the missing ASCII-ordered files once; never select the whole folder again because that can create duplicates.
- Confirm the current editor capacity at runtime. If it cannot accept the requested set, retain the full local set and report the exact limit before changing the upload scope.
- Confirm the featured image matches `final-01.png` and the dimension image is present.

## Item Details

- Replace the copied title completely.
- Replace the copied description completely.
- Keep the selected same-category taxonomy unless it is clearly wrong.
- Require the clean master to contain no unsupported material, finish, package, personalization, or other copied claims. If any are present in unattended mode, stop with a template-integrity failure instead of trying to clean them up.

## Item Options

- Require the unattended master to have no variations or custom buyer fields.
- If tags are skipped, require the tag field to be empty and verify `13 left` before writing product data.
- Replace copied dimensions with confirmed product dimensions, not package dimensions.
- Set confirmed color. Leave unsupported materials blank when Etsy has no accurate option.

## Pricing & Delivery

- Replace price with the deterministic calculation output.
- Use the current seller-confirmed quantity; 30 is only the original example default.
- Do not copy the supplier SKU into Etsy; leave `Add SKU` untouched unless the user provides an Etsy SKU.
- Keep the same-category delivery profile unless the user authorizes a profile change. Report a visible mismatch instead of changing another section.

## Save and Verify

- Click `Save as draft` only.
- Refresh Listings after the redirect. A stale `Draft 0` immediately after saving is not failure; refresh and reread.
- Open the `Draft` filter and verify the card title prefix, price, and stock.
- Reopen the draft and confirm the full title, Draft badge, 15 accepted photos, and `You have no unsaved changes`.
- Do not click `Publish` during verification.

## Browser Isolation and Recovery

- Bind supplier and Etsy work to their independently verified browser tabs/windows, using available authorized tools.
- Before each Etsy write stage, update the local stage file; after the stage, refresh and record the verified result.
- After interruption, search Etsy by stored draft ID or exact title before creating anything. Continue an existing draft when found.
- Keep normal runs silent. Alert only for login expiry, CAPTCHA, locked/unavailable desktop, or Computer Use/runtime failure.
