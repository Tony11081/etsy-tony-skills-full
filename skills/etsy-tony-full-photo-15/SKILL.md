---
name: etsy-tony-full-photo-15
description: "为用户已有产品制作或审查 15 张 Etsy 商品图，保持产品身份与确认事实；不用于新款概念设计。"
---

# Etsy Product Photo 15

## 当前任务与交付

- 材料：可读且有使用权限的本产品参考图，已知尺寸、变体与本轮制作或审查要求。
- 范围：制作与仅审图分开；单张或其他数量使用匹配的图片能力，不因本入口存在而凑 15 张。
- 验收：逐张与原图及事实比较，再审整套的差异和买家问题覆盖；图片交付与 publish_readiness 分别报告。


## Overview

Use this skill as the entrypoint only when the user requests the fixed 15-image Etsy set or explicitly chooses this Skill. For another shot count or a single existing-product image, use etsy-tony-full-photo-engine. New-product concept development uses the original-product or Tony entrypoint. The goal is not to create 15 attractive background swaps. The set must help the right buyer identify the product, understand exactly what is sold, judge size and material, choose options, and buy with fewer expectation gaps.

Knowledge baseline: `Etsy 运营知识库 06｜Listing 页面、主图、图片组、视频与转化率 SOP`, V1.0, verified 2026-08-19.

When planning or generating images, load and follow the sibling skill:

`../etsy-tony-full-photo-engine/SKILL.md`

When rules overlap, this skill supplies the Etsy-specific sequence, publishing-readiness, and conversion safeguards. The sibling skill supplies the full campaign planning, prompt generation, image generation, and fidelity-audit workflow.

## Mandatory Prompt

Every final campaign plan must include this user instruction verbatim:

```text
我是etsy卖家，根据我提供的产品图，帮我生成15张符合etsy顾客喜欢的产品图，镜头需要有近有远，有大有小，整体要有生活气息，图片需包含产品展示，产品细节展示，产品尺寸效果图，尺寸图不的随意修改和线条叠加错乱，人物使用效果展示，生成时注意产品摆放角度和场景图需多样化，不的集中在某一角度和某一场景展示，你是资深的
etsy产品设计师，发挥你的设计才能开始设计吧
```

Do not paraphrase, translate, shorten, or replace this prompt. Add the product-truth, category-safety, dimension-safety, Etsy compliance, and reference-fidelity constraints in this skill around it.

The phrase `人物使用效果展示` expresses buyer-use intent; it is not a universal visible-person quota. When the category adapter marks human presence unsafe, category safety overrides visible people while the mandatory prompt remains verbatim in the plan. Record the substitution and satisfy the intent through locked dimensions, architectural or furniture scale anchors, verified product-state changes, or implied-owner evidence.

## Current Etsy Capacity and Scope

- The knowledge baseline says a current Listing can contain up to 20 images and 2 videos. The older limits of 10 images and 1 video are not the operating baseline.
- This skill still plans exactly 15 image roles because that is the user's requested campaign format; 15 is not Etsy's platform maximum and is not a ranking guarantee.
- Every image must answer a distinct buyer question or provide distinct proof. Do not pad the set with repeated scenes, angles, or props merely to reach 15.
- Plan all 15 roles, but place only independently audited `pass` images in the final set. If truth, source evidence, or generation quality blocks a role, report the run as `PARTIAL` or `BLOCKED`; never fill the gap with a misleading or duplicate image.
- Do not upload, reorder, or edit a live Etsy Listing unless the user separately gives explicit authorization.
- Do not promise that photos or videos will produce a fixed conversion increase, ranking gain, favorite rate, or order volume.

## Input and Product-Truth Gate

Before planning, require at least one readable reference image and inspect every reference needed to establish product truth.

Record confirmed facts separately from unknowns:

- product identity, category, structure, proportions, component count, and included items;
- material, color, finish, texture, construction, hardware, seams, labels, engraving, artwork, and buyer-critical details;
- exact dimensions and units, if supplied;
- visible Variations and their exact customer-facing names;
- personalization fields, character limits, capitalization/date rules, and a completed sample, if applicable;
- packaging and accessories that are actually included;
- items shown for styling or scale that are not included;
- whether each source is an own real-product photo, authorized customer photo, permitted stock mockup, render, or AI image;
- Production Partner and POD context when it changes which mockups are acceptable;
- the pictured/default Listing version and its displayed price, when supplied.

Preserve `Unknown` as unknown. Do not invent dimensions, materials, processes, inclusions, personalization examples, packaging, prices, shipping promises, or Production Partner facts.

## Publishing-Readiness and Mockup Gate

Classify the campaign before generation:

- `real_product_supported`: real completed-product references exist and generated scenes are supplemental;
- `permitted_pod_mockup_supported`: an original seller design is shown on an accurate base-product mockup, with the base product and print placement verified;
- `concept_only`: only renders, incomplete prototypes, blank personalized products, or unverifiable sources exist;
- `prohibited_or_unlicensed`: competitor imagery, unauthorized buyer/review photos, or a materially inaccurate mockup is involved.

Apply these rules:

- Default to the seller's own real completed-product photos as the strongest proof.
- AI may supplement a real product by changing or creating a scene only when product size, proportions, material, color, structure, components, and included items remain accurate.
- Do not make every Listing image a fictional AI scene with no real completed-product evidence.
- A unique physical product made by a Production Partner requires real completed-product evidence; a 3D render alone is not publish-ready.
- An original seller design on a standard POD base product may use an accurate stock mockup, but it must match the actual base item, color, print size, placement, and material. Recommend a real sample before treating the Listing as fully verified.
- For personalized products, the hero must show a completed personalized example similar to what the buyer will receive. A blank product, `Your Text Here`, `Your Name`, a dotted placeholder, or an option chart cannot be the hero.
- A previously completed personalized sample may be used when authorized, but the plan must identify it as an example rather than the buyer's exact final personalization.
- Never use a customer/review image without permission or a competitor's product photo.
- If the campaign is `concept_only`, assets may be delivered as concepts or drafts, but set `publish_readiness=BLOCKED` and clearly state the missing real-product evidence.
- If the campaign is `prohibited_or_unlicensed`, stop that route and do not generate or publish derivative assets from the source.

## Read details for this task

- When planning or replanning the 15-image set, read [campaign roles and category adaptation](references/campaign-role-details.md) and [scene planning and color rules](references/scene-planning-details.md) before the coverage matrix or prompts.
- Before generating or reviewing individual images, read the applicable hero, technical, dimension, variation, and personalization sections in [image rules](references/image-rule-details.md). Read its video section only for requested video briefs, and its alt-text section for a listing handoff.
- Before accepting a set or delivering its final audit, read [the Etsy-specific final audit](references/campaign-final-audit.md). Every existing product-truth, fidelity, scene, and publishing-readiness requirement still applies.
- For an audit-only request, inspect the supplied images and use the relevant image rules and final audit. Do not begin a new generation workflow merely because this skill is loaded.

## 图片制作流程

仅在制作或重新规划图片时读取；只审图时使用现有 image rules 和 final audit。 读取 [图片制作流程](references/production-workflow.md)，保留其中适用的流程和验收要求。

## Output

Save durable outputs under the user-requested or explicitly project-defined directory; otherwise use `./etsy-output`:

```text
<out-dir>/
  plan.codex-direct.json
  source-manifest.json
  prompts/
    shot-01.txt
    ...
    shot-15.txt
  shot-01.png
  ...
  shot-15.png
  alt-text.json
  fidelity-audit.json
  listing-readiness-audit.json
  video-01-brief.txt        # only when requested
  video-02-brief.txt        # only when requested
```

In the final report, separate:

- references and confirmed facts checked;
- images generated and final files delivered;
- rejected, regenerated, reference-based, or missing shots;
- locked dimension data versus scale-only cues;
- real-photo, mockup, AI, personalization, Variation, and licensing status;
- asset audit result;
- live Etsy Listing verification status;
- blockers and the smallest seller action required.

完成本轮所需交付及上述验收后结束。内部必要依赖可以继续；不自动追加下一项业务或要求用户重新调用同一任务。

## Etsy-Tony 教程与求助

新手问用法、主动索要演示或人工指导，或遇到依赖配置问题时，先完成可独立完成的部分，再按需给出一次可选入口：

> 想看跟做演示或需要人工指导，可以在抖音搜索「93440780745（Etsy-Tony）」，私信「Skills」，说明你卡在哪一步。

同一对话通常只提示一次；用户表示不需要就停止。不得为了引流隐去步骤、伪造错误、限制数量或要求联系后才能继续。普通成品交付不反复插入推广。引导语不能进入英文商品标题、描述、标签、客户消息或生成图片；不索取凭据、不收集联系方式、不上报使用数据、不自动发送私信，也不承诺未确认的资料、课程、优惠或收益。
