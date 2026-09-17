import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_ENV_FILE = '';
const DEFAULT_OUTPUT_ROOT = path.resolve(process.cwd(), 'etsy-output', 'gigab2b-photo-runs');

const API_PATHS = {
  savedList: '/b2b-overseas-api/v1/buyer/product/skus/v1',
  detail: '/b2b-overseas-api/v1/buyer/product/detailInfo/v1',
  price: '/b2b-overseas-api/v1/buyer/product/price/v1',
  inventory: '/b2b-overseas-api/v1/buyer/inventory/quantity/v2'
};

const MANDATORY_ETSY_PROMPT = `我是etsy卖家，根据我提供的产品图，帮我生成15张符合etsy顾客喜欢的产品图，镜头需要有近有远，有大有小，整体要有生活气息，图片需包含产品展示，产品细节展示，产品尺寸效果图，尺寸图不的随意修改和线条叠加错乱，人物使用效果展示，生成时注意产品摆放角度和场景图需多样化，不的集中在某一角度和某一场景展示，你是资深的
etsy产品设计师，发挥你的设计才能开始设计吧 。`;

function argValue(name, fallback = '') {
  const prefix = `--${name}=`;
  const found = process.argv.find((arg) => arg.startsWith(prefix));
  return found ? found.slice(prefix.length) : fallback;
}

function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

function readEnvFile(file) {
  if (!file || !fs.existsSync(file)) return {};
  const env = {};
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const index = trimmed.indexOf('=');
    if (index < 0) continue;
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim().replace(/^["']|["']$/g, '');
    env[key] = value;
  }
  return env;
}

function required(value, name) {
  if (!value) throw new Error(`Missing ${name}`);
  return value;
}

function signHeaders(apiPath, clientId, clientSecret) {
  const timestamp = String(Date.now());
  const nonce = String(Math.floor(1000000000 + Math.random() * 9000000000));
  const string1 = `${clientId}&${apiPath}&${timestamp}&${nonce}`;
  const key = `${clientId}&${clientSecret}&${nonce}`;
  const hexDigest = crypto.createHmac('sha256', key).update(string1).digest('hex');
  return {
    'Content-Type': 'application/json',
    'client-id': clientId,
    timestamp,
    nonce,
    sign: Buffer.from(hexDigest).toString('base64')
  };
}

async function apiPost(ctx, apiPath, payload) {
  const response = await fetch(`${ctx.base}${apiPath}`, {
    method: 'POST',
    headers: signHeaders(apiPath, ctx.clientId, ctx.clientSecret),
    body: JSON.stringify(payload || {})
  });
  const text = await response.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    throw new Error(`Invalid JSON from ${apiPath}: ${text.slice(0, 240)}`);
  }
  if (!response.ok || json.success === false || (json.code && String(json.code) !== '200')) {
    throw new Error(`GigaB2B API failed ${apiPath}: HTTP ${response.status} ${JSON.stringify({
      code: json.code,
      msg: json.msg,
      subMsg: json.subMsg,
      requestId: json.requestId
    })}`);
  }
  return json;
}

function responseRows(json) {
  const data = json?.data ?? json;
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object' && data.sku) return [data];
  if (Array.isArray(data?.records)) return data.records;
  if (data && typeof data === 'object' && !Array.isArray(data)) return Object.values(data);
  return [];
}

function firstRowForSku(json, sku) {
  const rows = responseRows(json);
  return rows.find((row) => String(row?.sku || '').toLowerCase() === sku.toLowerCase()) || {};
}

function collectUrlValues(value, urls = []) {
  if (!value) return urls;
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (/^https?:\/\//i.test(trimmed)) urls.push(trimmed);
    return urls;
  }
  if (Array.isArray(value)) {
    for (const item of value) collectUrlValues(item, urls);
    return urls;
  }
  if (typeof value === 'object') {
    for (const item of Object.values(value)) collectUrlValues(item, urls);
  }
  return urls;
}

function uniqueUrls(values) {
  return Array.from(new Set(values.flatMap((value) => collectUrlValues(value))));
}

function productIdFromUrl(url) {
  if (!url) return '';
  try {
    return new URL(url).searchParams.get('product_id') || '';
  } catch {
    return '';
  }
}

function cleanText(value) {
  return String(value || '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function slugify(value) {
  const slug = cleanText(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 72);
  return slug || 'gigab2b-product';
}

function timestampSlug() {
  return new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
}

function utcMinusEightNow() {
  return new Date(Date.now() - 8 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 19)
    .replace('T', ' ');
}

function extensionFrom(url, contentType) {
  const type = String(contentType || '').toLowerCase();
  if (type.includes('png')) return '.png';
  if (type.includes('webp')) return '.webp';
  if (type.includes('pdf')) return '.pdf';
  if (type.includes('mp4')) return '.mp4';
  if (type.includes('jpeg') || type.includes('jpg')) return '.jpg';
  try {
    const ext = path.extname(new URL(url).pathname).toLowerCase();
    if (/^\.(jpg|jpeg|png|webp|pdf|mp4)$/i.test(ext)) return ext === '.jpeg' ? '.jpg' : ext;
  } catch {
    // Fall through to jpg.
  }
  return '.jpg';
}

async function downloadUrl(url, targetBase) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const ext = extensionFrom(url, response.headers.get('content-type'));
  const filePath = `${targetBase}${ext}`;
  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(filePath, buffer);
  return { filePath, bytes: buffer.length, contentType: response.headers.get('content-type') || '' };
}

function dimensionText(detail) {
  const assembled = [detail.assembledLength, detail.assembledWidth, detail.assembledHeight]
    .filter((value) => value !== undefined && value !== null && value !== '')
    .join(' x ');
  const packageDims = [detail.length, detail.width, detail.height]
    .filter((value) => value !== undefined && value !== null && value !== '')
    .join(' x ');
  return {
    assembled: assembled ? `${assembled} ${detail.assembledLengthUnit || 'unit not provided'}` : '',
    package: packageDims ? `${packageDims} ${detail.lengthUnit || 'unit not provided'}` : ''
  };
}

function buildHandoff({ manifest, detail }) {
  const dims = manifest.dimensions || {};
  const features = Array.isArray(detail.characteristics)
    ? detail.characteristics.map(cleanText).filter(Boolean).slice(0, 8)
    : [];
  const structureNotes = features.length
    ? features.join('; ')
    : cleanText(detail.description || detail.productName || manifest.productTitle);
  return [
    '# GigaB2B Etsy Product Photo Handoff',
    '',
    `Generation skill: etsy-tony-full-photo-engine`,
    `Source URL: ${manifest.sourceUrl || ''}`,
    `GigaB2B product_id: ${manifest.productId || ''}`,
    `SKU / Item Code: ${manifest.sku}`,
    `Product title: ${manifest.productTitle}`,
    `Reference image folder: ${manifest.referenceImageDir}`,
    `Reference image count: ${manifest.referenceImages.length}`,
    `Requested final image count: ${manifest.shotCount}`,
    '',
    'Product truth from API and references:',
    `- Category: ${detail.category || ''}`,
    `- Color/finish: ${detail.mainColor || ''}`,
    `- Material: ${detail.mainMaterial || ''}`,
    `- Assembled dimensions: ${dims.assembled || 'not provided'}`,
    `- Package dimensions: ${dims.package || 'not provided'}`,
    `- Weight: ${detail.assembledWeight || detail.weight || ''} ${detail.assembledWeightUnit || detail.weightUnit || ''}`.trim(),
    `- Product structure notes: ${structureNotes || 'Match the reference images exactly for shape, construction, and hardware.'}`,
    '',
    features.length ? 'Feature notes:' : '',
    ...features.map((feature) => `- ${feature}`),
    '',
    'Mandatory user prompt for image generation, use verbatim:',
    MANDATORY_ETSY_PROMPT.replace('生成15张', `生成${manifest.shotCount}张`),
    '',
    'Reusable generation direction:',
    `Inspect all verified references, then select 2-4 informative original files per shot; do not force every source image into every call or build oversized contact sheets to bypass the tool limit. Generate exactly ${manifest.shotCount} Etsy-ready square product images with a cohesive lifestyle campaign: wide, medium, close, and macro shots; varied room scenes; product display, detail display, scale/use context, and exactly one clean dimension/size image. The dimension image must use only the assembled dimensions above and must not invent sizes or create messy overlapping guide lines. Keep the product unchanged: match the reference images exactly, including drawer count, shelf openings, curved or straight silhouette, legs/base, handles/knobs, wood color, material, proportions, hardware, labels, and finish. Do not add or remove drawers, legs, shelves, mounts, or hardware. Use anonymous hands or partial body only when they prove scale or everyday use; avoid visible faces. Do not add logos, watermarks, badges, random text, or clutter. Keep scenes diverse and natural for Etsy buyers.`,
    '',
    'Reliability gate:',
    '- Persist the plan and individual prompts before generation.',
    '- Generate shot-01 alone with the 1-2 best original references and a concise prompt.',
    '- Continue one image call at a time only after a real output file exists and opens successfully.',
    '- After one network-error retry with fewer references and a shorter prompt, stop as BLOCKED and preserve resumable artifacts if the same error repeats.',
    '',
    'Suggested shot mix:',
    'Use the verified product category: hero, inventory, natural use, component/detail views, scale, confirmed dimensions and alternate use scenes. Furniture, jewelry and wedding products require different environments; do not reuse a bedroom template for every category.'
  ].filter((line) => line !== '').join('\n');
}

function usage() {
  return [
    'Usage:',
    '  node scripts/etsy-tony-full-gigab2b-assets.mjs --sku=YOUR_SKU --shots=15',
    '',
    'Options:',
    '  --list-saved             List products added to My Saved Items and exit.',
    '  --start-time=DATETIME     Saved-time lower bound, UTC-8. Defaults to 2000-01-01 00:00:00.',
    '  --end-time=DATETIME       Saved-time upper bound, UTC-8. Defaults to now.',
    '  --sku=SKU                 Required. GigaB2B Item Code / SKU.',
    '  --url=URL                 Optional source product URL.',
    '  --product-id=ID           Optional product_id when URL is not supplied.',
    '  --shots=15                Final requested image count.',
    '  --out-root=PATH           Output root. Defaults to ./etsy-output/gigab2b-photo-runs.',
    '  --env-file=PATH           GigaB2B OpenAPI env file.',
    '  --dry-run                 Fetch API data and write metadata, but skip image/PDF downloads.'
  ].join('\n');
}

async function main() {
  if (hasFlag('help') || hasFlag('h')) {
    console.log(usage());
    return;
  }

  const envFile = argValue('env-file', DEFAULT_ENV_FILE);
  const env = { ...readEnvFile(envFile), ...process.env };
  const ctx = {
    base: (env.GIGAB2B_API_BASE || 'https://openapi.gigab2b.com').replace(/\/$/, ''),
    clientId: required(env.GIGAB2B_CLIENT_ID, 'GIGAB2B_CLIENT_ID'),
    clientSecret: required(env.GIGAB2B_CLIENT_SECRET, 'GIGAB2B_CLIENT_SECRET')
  };

  if (hasFlag('list-saved')) {
    const savedJson = await apiPost(ctx, API_PATHS.savedList, {
      page: Number(argValue('page', '1')),
      pageSize: Number(argValue('page-size', '1000')),
      sort: 2,
      queryTimeType: 2,
      startTime: argValue('start-time', '2000-01-01 00:00:00'),
      endTime: argValue('end-time', utcMinusEightNow())
    });
    console.log(JSON.stringify(savedJson, null, 2));
    return;
  }

  const sku = argValue('sku').trim();
  if (!sku) {
    throw new Error(`Missing --sku. Open the GigaB2B page in Chrome, copy "Item Code", then rerun.\n\n${usage()}`);
  }

  const sourceUrl = argValue('url').trim();
  const productId = argValue('product-id', productIdFromUrl(sourceUrl)).trim();
  const shotCount = Number(argValue('shots', '15'));
  if (!Number.isSafeInteger(shotCount) || shotCount < 1) throw new Error('--shots must be a positive integer');
  const outputRoot = argValue('out-root', DEFAULT_OUTPUT_ROOT);

  fs.mkdirSync(outputRoot, { recursive: true });

  const [detailJson, priceJson, inventoryJson] = await Promise.all([
    apiPost(ctx, API_PATHS.detail, { skus: [sku] }),
    apiPost(ctx, API_PATHS.price, { skus: [sku] }),
    apiPost(ctx, API_PATHS.inventory, { skus: [sku] })
  ]);

  const detail = firstRowForSku(detailJson, sku);
  if (!detail?.sku) {
    throw new Error(`SKU not found in detail API response: ${sku}`);
  }

  const productTitle = cleanText(detail.productName || sku);
  const runName = [
    productId ? `gigab2b-${productId}` : 'gigab2b',
    sku.toLowerCase(),
    timestampSlug(),
    slugify(productTitle)
  ].join('-');
  const outDir = path.join(outputRoot, runName);
  const referenceDir = path.join(outDir, 'reference-images');
  const filesDir = path.join(outDir, 'files');
  fs.mkdirSync(referenceDir, { recursive: true });
  fs.mkdirSync(filesDir, { recursive: true });

  const imageUrls = uniqueUrls([detail.mainImageUrl, detail.imageUrls])
    .filter((url) => !/\.pdf(?:\?|$)/i.test(url));
  const fileUrls = uniqueUrls([detail.fileUrls, detail.certificationList, detail.videoUrls, detail.productVideoUrl])
    .filter((url) => !imageUrls.includes(url));
  const dimensions = dimensionText(detail);

  fs.writeFileSync(path.join(outDir, 'api-detail.json'), JSON.stringify(detailJson, null, 2));
  fs.writeFileSync(path.join(outDir, 'api-price.json'), JSON.stringify(priceJson, null, 2));
  fs.writeFileSync(path.join(outDir, 'api-inventory.json'), JSON.stringify(inventoryJson, null, 2));
  fs.writeFileSync(path.join(outDir, 'product-title.txt'), `${productTitle}\n`);
  fs.writeFileSync(path.join(outDir, 'mandatory-etsy-prompt.txt'), `${MANDATORY_ETSY_PROMPT.replace('生成15张', `生成${shotCount}张`)}\n`);
  fs.writeFileSync(path.join(outDir, 'source-image-urls.txt'), `${imageUrls.join('\n')}\n`);
  fs.writeFileSync(path.join(outDir, 'source-file-urls.txt'), `${fileUrls.join('\n')}\n`);

  const referenceImages = [];
  const fileDownloads = [];
  const downloadErrors = [];
  if (!hasFlag('dry-run')) {
    for (let index = 0; index < imageUrls.length; index += 1) {
      const url = imageUrls[index];
      const base = path.join(referenceDir, `ref-${String(index + 1).padStart(2, '0')}`);
      try {
        referenceImages.push({ url, ...(await downloadUrl(url, base)) });
      } catch (error) {
        downloadErrors.push({ url, error: error.message || String(error) });
      }
    }

    for (let index = 0; index < fileUrls.length; index += 1) {
      const url = fileUrls[index];
      const base = path.join(filesDir, `file-${String(index + 1).padStart(2, '0')}`);
      try {
        fileDownloads.push({ url, ...(await downloadUrl(url, base)) });
      } catch (error) {
        downloadErrors.push({ url, error: error.message || String(error) });
      }
    }
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    workflow: 'etsy-tony-full-gigab2b-assets',
    sourceUrl,
    productId,
    sku,
    productTitle,
    shotCount,
    apiBase: ctx.base,
    productFacts: {
      category: detail.category || '',
      mainColor: detail.mainColor || '',
      mainMaterial: detail.mainMaterial || '',
      placeOfOrigin: detail.placeOfOrigin || '',
      seller: detail.sellerInfo?.sellerName || detail.sellerInfo?.shopName || ''
    },
    dimensions,
    referenceImageDir: referenceDir,
    referenceImages,
    sourceImageUrls: imageUrls,
    fileDownloads,
    sourceFileUrls: fileUrls,
    downloadErrors,
    mandatoryEtsyPrompt: MANDATORY_ETSY_PROMPT.replace('生成15张', `生成${shotCount}张`),
    generationSkill: 'etsy-tony-full-photo-engine',
    generationStatus: !hasFlag('dry-run') && referenceImages.length > 0 && downloadErrors.length === 0
      ? 'references_downloaded_pending_visual_review' : 'source_preparation_incomplete'
  };

  fs.writeFileSync(path.join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  fs.writeFileSync(path.join(outDir, 'product-photo-campaign-openrouter-handoff.txt'), buildHandoff({ manifest, detail }));

  console.log(JSON.stringify({
    outDir,
    sku,
    productId,
    productTitle,
    sourceImageCount: imageUrls.length,
    downloadedReferenceImages: referenceImages.length,
    sourceFileCount: fileUrls.length,
    downloadedFiles: fileDownloads.length,
    downloadErrors: downloadErrors.length,
    manifestPath: path.join(outDir, 'manifest.json'),
    handoffPath: path.join(outDir, 'product-photo-campaign-openrouter-handoff.txt')
  }, null, 2));
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
