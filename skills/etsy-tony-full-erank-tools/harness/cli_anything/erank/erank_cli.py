from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
from typing import Any

import click

from cli_anything.erank.core.analyzers import (
    api_surface_report,
    audit_listing,
    category_suggestions,
    compare_keywords,
    compare_listing_audits,
    competitor_sales as competitor_sales_analysis,
    delivery_status as delivery_status_analysis,
    generate_listing_helper,
    health_check as health_check_analysis,
    keyword_analysis,
    listings_summary,
    monthly_calendar,
    profit_calculator,
    rank_check as rank_check_analysis,
    roi_calculator,
    sales_map as sales_map_analysis,
    shop_info as shop_info_analysis,
    spell_check as spell_check_analysis,
    tag_report as tag_report_analysis,
    top_sellers as top_sellers_analysis,
    traffic_stats as traffic_stats_analysis,
    trend_buzz as trend_buzz_analysis,
)
from cli_anything.erank.core.models import Listing, parse_tags
from cli_anything.erank.core.shop_search import add_freshness, find_shops, load_shop_rows
from cli_anything.erank.core.session import SessionStore
from cli_anything.erank.utils.data_io import load_listings, load_orders, load_rows, write_csv
from cli_anything.erank.utils.etsy_backend import EtsyBackend
from cli_anything.erank.utils.live_sources import (
    ERANK_TOP_SELLERS_URL,
    ERANK_TREND_BUZZ_URL,
    fetch_erank_top_sellers,
    fetch_alura_top_sellers,
    parse_erank_or_export,
    probe_erank_live_api,
    source_status,
)


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def emit(ctx: click.Context, payload: Any) -> None:
    if ctx.obj.get("json"):
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return
    if isinstance(payload, dict):
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        click.echo(str(payload))


def session(ctx: click.Context) -> SessionStore:
    return ctx.obj["session"]


def backend(ctx: click.Context) -> EtsyBackend:
    return EtsyBackend(session(ctx).config())


def require_listings(path: str | None) -> list[Listing]:
    listings = load_listings(path)
    if not listings:
        raise click.ClickException("No listings loaded. Provide --listings CSV/JSON or use --source etsy where supported.")
    return listings


def listing_from_file(path: str) -> Listing:
    listings = load_listings(path)
    if not listings:
        raise click.ClickException(f"No listing rows found in {path}")
    return listings[0]


def listing_from_options(
    listing_file: str | None,
    listing_id: str,
    shop: str,
    title: str,
    description: str,
    tags_text: str,
    tags: tuple[str, ...],
    price: float,
    image_count: int,
    materials_text: str,
) -> Listing:
    if listing_file:
        return listing_from_file(listing_file)
    combined_tags = list(tags)
    if tags_text:
        combined_tags.extend(parse_tags(tags_text))
    return Listing(
        listing_id=listing_id,
        shop=shop,
        title=title,
        description=description,
        tags=combined_tags,
        price=price,
        image_count=image_count,
        materials=parse_tags(materials_text),
    )


def load_keyword_source(ctx: click.Context, source: str, listings: str | None, keyword: str, limit: int) -> list[Listing]:
    if source == "etsy":
        live = backend(ctx)
        try:
            return live.active_listings(keyword, limit=limit)
        except Exception as exc:  # pragma: no cover - live API branch
            raise click.ClickException(str(exc)) from exc
    return load_listings(listings)


def read_keywords(file_path: str | None, args: tuple[str, ...]) -> list[str]:
    keywords = list(args)
    if file_path:
        lines = Path(file_path).read_text(encoding="utf-8").splitlines()
        keywords.extend(line.strip() for line in lines if line.strip())
    deduped: list[str] = []
    for keyword in keywords:
        if keyword not in deduped:
            deduped.append(keyword)
    return deduped


def repl(ctx: click.Context) -> None:
    click.echo("eRank CLI-Anything REPL. Type 'help' or 'exit'.")
    while True:
        try:
            line = input("erank> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo()
            return
        if not line:
            continue
        if line.lower() in {"exit", "quit", ":q"}:
            return
        if line.lower() == "help":
            click.echo(ctx.get_help())
            continue
        try:
            cli.main(args=shlex.split(line), prog_name="erank", standalone_mode=False, obj=ctx.obj)
        except click.ClickException as exc:
            click.echo(f"Error: {exc.message}", err=True)
        except SystemExit:
            pass


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--session", "session_path", type=click.Path(dir_okay=False), help="Path to a local session state file.")
@click.pass_context
def cli(ctx: click.Context, json_output: bool, session_path: str | None) -> None:
    """eRank-like Etsy SEO CLI-Anything harness."""
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["json"] = json_output or ctx.obj.get("json", False)
    ctx.obj["session"] = ctx.obj.get("session") or SessionStore(session_path)
    if ctx.invoked_subcommand is None:
        repl(ctx)


@cli.command("api-check")
@click.pass_context
def api_check(ctx: click.Context) -> None:
    """Report eRank API findings and supported backend policy."""
    emit(ctx, api_surface_report())


@cli.command("status")
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show local session status."""
    emit(ctx, session(ctx).summary())


@cli.command("undo")
@click.pass_context
def undo(ctx: click.Context) -> None:
    """Undo the last local-state mutation."""
    emit(ctx, session(ctx).undo())


@cli.command("redo")
@click.pass_context
def redo(ctx: click.Context) -> None:
    """Redo the last undone local-state mutation."""
    emit(ctx, session(ctx).redo())


@click.group("config")
def config_group() -> None:
    """Manage local harness configuration."""


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    store = session(ctx)
    store.begin(f"config set {key}")
    store.config()[key] = value
    store.record("config.set", {"key": key})
    store.save()
    emit(ctx, {"ok": True, "key": key})


@config_group.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx: click.Context, key: str) -> None:
    value = session(ctx).config().get(key)
    if key.lower().endswith(("token", "key", "secret")) and value:
        value = f"{str(value)[:4]}...{str(value)[-4:]}"
    emit(ctx, {"key": key, "value": value})


@config_group.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    masked = {}
    for key, value in session(ctx).config().items():
        if key.lower().endswith(("token", "key", "secret")) and value:
            masked[key] = f"{str(value)[:4]}...{str(value)[-4:]}"
        else:
            masked[key] = value
    emit(ctx, {"config": masked})


cli.add_command(config_group)


@click.group("keyword")
def keyword_group() -> None:
    """Keyword research tools."""


@keyword_group.command("tool")
@click.argument("keyword")
@click.option("--listings", type=click.Path(dir_okay=False), help="CSV/JSON listing export.")
@click.option("--source", type=click.Choice(["local", "etsy"]), default="local", show_default=True)
@click.option("--limit", default=20, show_default=True)
@click.pass_context
def keyword_tool(ctx: click.Context, keyword: str, listings: str | None, source: str, limit: int) -> None:
    data = load_keyword_source(ctx, source, listings, keyword, limit)
    emit(ctx, keyword_analysis(keyword, data, limit=limit))


@keyword_group.command("compare")
@click.argument("keywords", nargs=-1, required=True)
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def keyword_compare(ctx: click.Context, keywords: tuple[str, ...], listings: str) -> None:
    emit(ctx, compare_keywords(keywords, require_listings(listings)))


@keyword_group.command("bulk")
@click.argument("keywords", nargs=-1)
@click.option("--file", "file_path", type=click.Path(dir_okay=False), help="One keyword per line.")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--limit", default=10, show_default=True)
@click.pass_context
def keyword_bulk(ctx: click.Context, keywords: tuple[str, ...], file_path: str | None, listings: str, limit: int) -> None:
    terms = read_keywords(file_path, keywords)
    data = require_listings(listings)
    emit(ctx, {"keywords": [keyword_analysis(term, data, limit=limit) for term in terms]})


@keyword_group.group("lists")
def keyword_lists_group() -> None:
    """Save and manage keyword lists."""


@keyword_lists_group.command("add")
@click.argument("list_name")
@click.argument("keyword")
@click.option("--note", default="")
@click.pass_context
def keyword_list_add(ctx: click.Context, list_name: str, keyword: str, note: str) -> None:
    store = session(ctx)
    store.begin(f"keyword add {keyword}")
    items = store.state.setdefault("keyword_lists", {}).setdefault(list_name, [])
    if not any(item.get("keyword") == keyword for item in items):
        items.append({"keyword": keyword, "note": note, "added_at": datetime.now(timezone.utc).isoformat()})
    store.record("keyword_lists.add", {"list": list_name, "keyword": keyword})
    store.save()
    emit(ctx, {"ok": True, "list": list_name, "count": len(items)})


@keyword_lists_group.command("show")
@click.argument("list_name", required=False)
@click.pass_context
def keyword_list_show(ctx: click.Context, list_name: str | None) -> None:
    lists = session(ctx).state.get("keyword_lists", {})
    emit(ctx, {list_name: lists.get(list_name, [])} if list_name else {"keyword_lists": lists})


@keyword_lists_group.command("remove")
@click.argument("list_name")
@click.argument("keyword")
@click.pass_context
def keyword_list_remove(ctx: click.Context, list_name: str, keyword: str) -> None:
    store = session(ctx)
    store.begin(f"keyword remove {keyword}")
    items = store.state.setdefault("keyword_lists", {}).setdefault(list_name, [])
    store.state["keyword_lists"][list_name] = [item for item in items if item.get("keyword") != keyword]
    store.record("keyword_lists.remove", {"list": list_name, "keyword": keyword})
    store.save()
    emit(ctx, {"ok": True, "list": list_name, "count": len(store.state["keyword_lists"][list_name])})


cli.add_command(keyword_group)


@click.group("rank")
def rank_group() -> None:
    """Rank checker tools."""


@rank_group.command("check")
@click.argument("keyword")
@click.option("--shop", required=True)
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--limit", default=100, show_default=True)
@click.pass_context
def rank_check(ctx: click.Context, keyword: str, shop: str, listings: str, limit: int) -> None:
    emit(ctx, rank_check_analysis(keyword, require_listings(listings), shop=shop, limit=limit))


@rank_group.command("bulk")
@click.argument("keywords", nargs=-1)
@click.option("--file", "file_path", type=click.Path(dir_okay=False))
@click.option("--shop", required=True)
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def rank_bulk(ctx: click.Context, keywords: tuple[str, ...], file_path: str | None, shop: str, listings: str) -> None:
    terms = read_keywords(file_path, keywords)
    data = require_listings(listings)
    emit(ctx, {"shop": shop, "results": [rank_check_analysis(term, data, shop=shop) for term in terms]})


cli.add_command(rank_group)


@click.group("competitor")
def competitor_group() -> None:
    """Competitor research tools."""


@competitor_group.command("shop-info")
@click.argument("shop")
@click.option("--listings", type=click.Path(dir_okay=False))
@click.option("--source", type=click.Choice(["local", "etsy"]), default="local", show_default=True)
@click.option("--shop-id", default="", help="Numeric Etsy shop id for live Etsy calls.")
@click.pass_context
def competitor_shop_info(ctx: click.Context, shop: str, listings: str | None, source: str, shop_id: str) -> None:
    if source == "etsy":  # pragma: no cover - live API branch
        live = backend(ctx)
        if shop_id:
            emit(ctx, live.shop_by_id(shop_id))
            return
        matches = live.find_shops(shop)
        emit(ctx, {"shop": shop, "matches": matches})
        return
    emit(ctx, shop_info_analysis(shop, require_listings(listings)))


@competitor_group.command("tags")
@click.argument("shop")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def competitor_tags(ctx: click.Context, shop: str, listings: str) -> None:
    emit(ctx, tag_report_analysis(require_listings(listings), shop=shop))


@competitor_group.command("listings")
@click.argument("shop")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--limit", default=50, show_default=True)
@click.pass_context
def competitor_listings(ctx: click.Context, shop: str, listings: str, limit: int) -> None:
    selected = [item.to_dict() for item in require_listings(listings) if item.shop.lower() == shop.lower()]
    selected.sort(key=lambda row: (row.get("updated", ""), row.get("sales", 0)), reverse=True)
    emit(ctx, {"shop": shop, "listings": selected[:limit], "count": len(selected)})


@competitor_group.command("sales")
@click.argument("shop")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def competitor_sales(ctx: click.Context, shop: str, listings: str) -> None:
    emit(ctx, competitor_sales_analysis(shop, require_listings(listings)))


@competitor_group.command("top-sellers")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--limit", default=100, show_default=True)
@click.pass_context
def competitor_top_sellers(ctx: click.Context, listings: str, limit: int) -> None:
    emit(ctx, top_sellers_analysis(require_listings(listings), limit=limit))


cli.add_command(competitor_group)


@click.group("listing")
def listing_group() -> None:
    """Listing optimization tools."""


def listing_options(func):
    func = click.option("--materials", "materials_text", default="")(func)
    func = click.option("--image-count", default=0, show_default=True)(func)
    func = click.option("--price", default=0.0, show_default=True)(func)
    func = click.option("--tag", "tags", multiple=True, help="Repeatable tag option.")(func)
    func = click.option("--tags", "tags_text", default="", help="Comma/semicolon/pipe-separated tags.")(func)
    func = click.option("--description", default="")(func)
    func = click.option("--title", default="")(func)
    func = click.option("--shop", default="")(func)
    func = click.option("--listing-id", default="")(func)
    func = click.option("--listing-file", type=click.Path(dir_okay=False))(func)
    return func


@listing_group.command("audit")
@listing_options
@click.pass_context
def listing_audit(
    ctx: click.Context,
    listing_file: str | None,
    listing_id: str,
    shop: str,
    title: str,
    description: str,
    tags_text: str,
    tags: tuple[str, ...],
    price: float,
    image_count: int,
    materials_text: str,
) -> None:
    listing = listing_from_options(listing_file, listing_id, shop, title, description, tags_text, tags, price, image_count, materials_text)
    emit(ctx, audit_listing(listing))


@listing_group.command("compare")
@click.argument("listing_files", nargs=-1, required=True)
@click.pass_context
def listing_compare(ctx: click.Context, listing_files: tuple[str, ...]) -> None:
    emit(ctx, compare_listing_audits([listing_from_file(path) for path in listing_files]))


@listing_group.command("draft-audit")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def listing_draft_audit(ctx: click.Context, listings: str) -> None:
    drafts = [item for item in require_listings(listings) if item.status.lower() in {"draft", "inactive"}]
    emit(ctx, {"draft_count": len(drafts), "drafts": [audit_listing(item) for item in drafts]})


@listing_group.group("changes")
def listing_changes_group() -> None:
    """Track local listing revisions and audit deltas."""


@listing_changes_group.command("track")
@click.argument("listing_id")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--note", default="")
@click.pass_context
def listing_changes_track(ctx: click.Context, listing_id: str, listings: str, note: str) -> None:
    data = require_listings(listings)
    matches = [item for item in data if item.listing_id == listing_id]
    if not matches:
        raise click.ClickException(f"Listing id not found: {listing_id}")
    listing = matches[0]
    store = session(ctx)
    store.begin(f"listing snapshot {listing_id}")
    snapshots = store.state.setdefault("listing_snapshots", {}).setdefault(listing_id, [])
    snapshots.append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "note": note,
            "listing": listing.to_dict(),
            "audit": audit_listing(listing),
        }
    )
    store.record("listing_changes.track", {"listing_id": listing_id})
    store.save()
    emit(ctx, {"ok": True, "listing_id": listing_id, "snapshot_count": len(snapshots)})


@listing_changes_group.command("show")
@click.argument("listing_id", required=False)
@click.pass_context
def listing_changes_show(ctx: click.Context, listing_id: str | None) -> None:
    snapshots = session(ctx).state.get("listing_snapshots", {})
    emit(ctx, {listing_id: snapshots.get(listing_id, [])} if listing_id else {"listing_snapshots": snapshots})


@listing_group.command("ai-helper")
@click.argument("seed")
@click.argument("keywords", nargs=-1)
@click.option("--listings", type=click.Path(dir_okay=False))
@click.pass_context
def listing_ai_helper(ctx: click.Context, seed: str, keywords: tuple[str, ...], listings: str | None) -> None:
    emit(ctx, generate_listing_helper(seed, keywords, load_listings(listings)))


cli.add_command(listing_group)


@click.group("shop")
def shop_group() -> None:
    """Shop insight tools."""


@shop_group.command("health-check")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--shop", default="")
@click.pass_context
def shop_health_check(ctx: click.Context, listings: str, shop: str) -> None:
    emit(ctx, health_check_analysis(require_listings(listings), shop=shop or None))


@shop_group.command("tag-report")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--shop", default="")
@click.pass_context
def shop_tag_report(ctx: click.Context, listings: str, shop: str) -> None:
    emit(ctx, tag_report_analysis(require_listings(listings), shop=shop or None))


@shop_group.command("sales-map")
@click.option("--orders", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def shop_sales_map(ctx: click.Context, orders: str) -> None:
    emit(ctx, sales_map_analysis(load_orders(orders)))


@shop_group.command("delivery-status")
@click.option("--orders", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def shop_delivery_status(ctx: click.Context, orders: str) -> None:
    emit(ctx, delivery_status_analysis(load_orders(orders)))


@shop_group.command("spotted")
@click.argument("keywords", nargs=-1, required=True)
@click.option("--shop", required=True)
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def shop_spotted(ctx: click.Context, keywords: tuple[str, ...], shop: str, listings: str) -> None:
    data = require_listings(listings)
    emit(ctx, {"shop": shop, "results": [rank_check_analysis(keyword, data, shop=shop) for keyword in keywords]})


@shop_group.command("spell-check")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.option("--shop", default="")
@click.pass_context
def shop_spell_check(ctx: click.Context, listings: str, shop: str) -> None:
    emit(ctx, spell_check_analysis(require_listings(listings), shop=shop or None))


@shop_group.command("traffic-stats")
@click.option("--traffic-csv", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def shop_traffic_stats(ctx: click.Context, traffic_csv: str) -> None:
    emit(ctx, traffic_stats_analysis(load_rows(traffic_csv)))


cli.add_command(shop_group)


@click.group("tools")
def tools_group() -> None:
    """Calculators and planning tools."""


@tools_group.command("profit")
@click.option("--price", required=True, type=float)
@click.option("--shipping-charged", default=0.0, show_default=True)
@click.option("--item-cost", default=0.0, show_default=True)
@click.option("--shipping-cost", default=0.0, show_default=True)
@click.option("--ad-cost", default=0.0, show_default=True)
@click.option("--offsite-ad-rate", default=0.0, show_default=True)
@click.pass_context
def tools_profit(
    ctx: click.Context,
    price: float,
    shipping_charged: float,
    item_cost: float,
    shipping_cost: float,
    ad_cost: float,
    offsite_ad_rate: float,
) -> None:
    emit(ctx, profit_calculator(price, shipping_charged, item_cost, shipping_cost, ad_cost, offsite_ad_rate=offsite_ad_rate))


@tools_group.command("roi")
@click.option("--ad-spend", required=True, type=float)
@click.option("--clicks", required=True, type=int)
@click.option("--orders", required=True, type=int)
@click.option("--revenue", required=True, type=float)
@click.option("--cost-of-goods", default=0.0, show_default=True)
@click.pass_context
def tools_roi(ctx: click.Context, ad_spend: float, clicks: int, orders: int, revenue: float, cost_of_goods: float) -> None:
    emit(ctx, roi_calculator(ad_spend, clicks, orders, revenue, cost_of_goods))


@tools_group.command("category")
@click.option("--title", required=True)
@click.option("--tag", "tags", multiple=True)
@click.option("--tags", "tags_text", default="")
@click.pass_context
def tools_category(ctx: click.Context, title: str, tags: tuple[str, ...], tags_text: str) -> None:
    combined = list(tags) + parse_tags(tags_text)
    emit(ctx, category_suggestions(title, combined))


@tools_group.command("calendar")
@click.option("--country", default="US", show_default=True)
@click.option("--month", type=int)
@click.pass_context
def tools_calendar(ctx: click.Context, country: str, month: int | None) -> None:
    emit(ctx, monthly_calendar(country, month))


@tools_group.command("shortcut")
@click.option("--keyword", default="")
@click.option("--shop", default="")
@click.option("--listing-url", default="")
@click.pass_context
def tools_shortcut(ctx: click.Context, keyword: str, shop: str, listing_url: str) -> None:
    links = {}
    if keyword:
        links["keyword_tool"] = f"https://members.erank.com/keyword-tool?keyword={keyword.replace(' ', '+')}"
    if shop:
        links["shop_info"] = f"https://erank.com/shop-info/{shop}"
    if listing_url:
        links["listing_audit"] = f"https://members.erank.com/listing-audit?url={listing_url}"
    emit(ctx, {"links": links})


cli.add_command(tools_group)


@click.group("trends")
def trends_group() -> None:
    """Trend tracking tools."""


@trends_group.command("buzz")
@click.option("--trends-csv", type=click.Path(dir_okay=False), required=True)
@click.option("--marketplace", default="")
@click.option("--limit", default=100, show_default=True)
@click.pass_context
def trends_buzz(ctx: click.Context, trends_csv: str, marketplace: str, limit: int) -> None:
    emit(ctx, trend_buzz_analysis(load_rows(trends_csv), marketplace or None, limit=limit))


@trends_group.command("monthly")
@click.option("--trends-csv", type=click.Path(dir_okay=False), required=True)
@click.option("--category", default="")
@click.option("--limit", default=100, show_default=True)
@click.pass_context
def trends_monthly(ctx: click.Context, trends_csv: str, category: str, limit: int) -> None:
    rows = load_rows(trends_csv)
    if category:
        rows = [row for row in rows if str(row.get("category", "")).lower() == category.lower()]
    emit(ctx, trend_buzz_analysis(rows, None, limit=limit))


cli.add_command(trends_group)


@click.group("live")
def live_group() -> None:
    """Realtime data connectors and member-export helpers."""


@live_group.command("sources")
@click.pass_context
def live_sources(ctx: click.Context) -> None:
    """Show which realtime sources are ready."""
    live = backend(ctx)
    emit(
        ctx,
        source_status(
            etsy_configured=live.configured(),
            etsy_oauth_configured=live.configured(require_oauth=True),
        ),
    )


@live_group.command("source-probe")
@click.option("--timeout", default=10, show_default=True, type=click.IntRange(1, 60))
@click.pass_context
def live_source_probe(ctx: click.Context, timeout: int) -> None:
    """Probe current no-cookie access to the undocumented eRank endpoint."""
    emit(
        ctx,
        {
            "source": "erank-undocumented-read-only-api",
            "probe": probe_erank_live_api(timeout=timeout),
            "security_boundary": "No browser cookies, tokens, localStorage, or sessionStorage are read or copied.",
            "fallback": "Use the logged-in member browser or a CSV/JSON/HTML export when authentication is required.",
        },
    )


@live_group.command("open")
@click.argument("tool", type=click.Choice(["top-sellers", "trend-buzz"]))
@click.pass_context
def live_open(ctx: click.Context, tool: str) -> None:
    """Return the eRank member URL to open in the logged-in browser."""
    urls = {
        "top-sellers": ERANK_TOP_SELLERS_URL,
        "trend-buzz": ERANK_TREND_BUZZ_URL,
    }
    emit(
        ctx,
        {
            "tool": tool,
            "url": urls[tool],
            "next_step": "Open this in the logged-in Chrome profile, export CSV or save HTML, then run live top-sellers --source erank-export --input <file>.",
            "security_boundary": "Use browser login state only; do not copy cookies.",
        },
    )


@live_group.command("top-sellers")
@click.option(
    "--source",
    type=click.Choice(["erank-live", "erank-export", "alura-public"]),
    default="erank-live",
    show_default=True,
)
@click.option("--timeframe", type=click.Choice(["yesterday", "all-time"]), default="yesterday", show_default=True)
@click.option("--input", "input_path", type=click.Path(dir_okay=False), help="eRank CSV/HTML export path.")
@click.option("--limit", default=100, show_default=True)
@click.option("--output", type=click.Path(dir_okay=False), help="Optional CSV output path.")
@click.pass_context
def live_top_sellers(ctx: click.Context, source: str, timeframe: str, input_path: str | None, limit: int, output: str | None) -> None:
    """Read current top sellers from eRank export or a public live fallback."""
    if source == "erank-live":
        rows = fetch_erank_top_sellers(timeframe=timeframe, limit=limit)
    elif source == "erank-export":
        if not input_path:
            raise click.ClickException("Missing --input for eRank exports. Use live open top-sellers, export/save the member page, then pass that file.")
        rows = parse_erank_or_export(input_path, source="erank-export")
    else:
        rows = fetch_alura_top_sellers(limit=limit)
    rows = rows[:limit]
    result: dict[str, Any] = {
        "source": source,
        "timeframe": timeframe,
        "limit": limit,
        "count": len(rows),
        "rows": rows,
        "realtime": source != "erank-export",
        "snapshot": source == "erank-export",
        "limitations": [],
    }
    if source == "alura-public":
        result["limitations"].append("Public fallback is current public data, not eRank member data and not yesterday-only sales.")
    if source == "erank-live" and timeframe == "all-time" and len(rows) < limit:
        result["limitations"].append("The no-cookie all-time endpoint returned a server-limited sample; this is not exhaustive coverage.")
    if output:
        written = write_csv(output, rows)
        result["output"] = {"path": str(Path(output).resolve()), "rows": written}
    emit(ctx, result)


@live_group.command("shop-search")
@click.option("--source", type=click.Choice(["erank-export", "erank-live"]), default="erank-export", show_default=True)
@click.option("--input", "input_path", type=click.Path(exists=True, dir_okay=False), help="eRank CSV/JSON/HTML export or saved API response.")
@click.option("--limit", default=100, show_default=True, type=click.IntRange(1, 1000), help="Requested rows for --source erank-live.")
@click.option("--sales-min", default=660, show_default=True, type=int)
@click.option("--sales-max", default=680, show_default=True, type=int)
@click.option("--age-months", default=4, show_default=True, type=int)
@click.option("--age-tolerance", default=0, show_default=True, type=int, help="Allowed whole-month deviation from --age-months.")
@click.option("--as-of", type=click.DateTime(formats=["%Y-%m-%d"]), help="Deterministic age calculation date; defaults to today.")
@click.option("--max-age-hours", default=24.0, show_default=True, type=float, help="Maximum snapshot age before evidence is marked stale.")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional CSV containing strict matches only.")
@click.pass_context
def live_shop_search(
    ctx: click.Context,
    source: str,
    input_path: str | None,
    limit: int,
    sales_min: int,
    sales_max: int,
    age_months: int,
    age_tolerance: int,
    as_of: datetime | None,
    max_age_hours: float,
    output: str | None,
) -> None:
    """Find shops by lifetime-sales range and exact shop age."""
    if max_age_hours <= 0:
        raise click.ClickException("--max-age-hours must be greater than zero.")
    try:
        if source == "erank-export":
            if not input_path:
                raise click.ClickException("Missing --input for eRank export shop search.")
            rows, metadata = load_shop_rows(input_path)
            metadata["coverage"] = "input_rows_only"
        else:
            rows = fetch_erank_top_sellers(timeframe="all-time", limit=limit)
            metadata = {
                "source": "erank-live",
                "period": "all-time",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "coverage": "server_limited_sample" if len(rows) < limit else "requested_rows",
            }
        result = find_shops(
            rows,
            sales_min=sales_min,
            sales_max=sales_max,
            age_months=age_months,
            age_tolerance=age_tolerance,
            as_of=(as_of or datetime.now()).date(),
            default_period=metadata.get("period"),
        )
    except click.ClickException:
        raise
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    add_freshness(result, metadata, max_age_hours)
    if metadata.get("coverage") == "server_limited_sample":
        result["limitations"].append("The no-cookie all-time endpoint returned only a server-limited sample; no-match does not mean no qualifying shop exists.")
    if output:
        written = write_csv(output, result["matches"])
        result["output"] = {"path": str(Path(output).resolve()), "rows": written}
    emit(ctx, result)


cli.add_command(live_group)


@click.group("data")
def data_group() -> None:
    """Data import and inspection helpers."""


@data_group.command("summarize")
@click.option("--listings", type=click.Path(dir_okay=False), required=True)
@click.pass_context
def data_summarize(ctx: click.Context, listings: str) -> None:
    emit(ctx, listings_summary(require_listings(listings)))


@data_group.command("remember")
@click.argument("kind", type=click.Choice(["listings", "orders", "trends", "traffic"]))
@click.argument("path", type=click.Path(dir_okay=False))
@click.pass_context
def data_remember(ctx: click.Context, kind: str, path: str) -> None:
    store = session(ctx)
    store.begin(f"remember {kind}")
    store.state.setdefault("imports", {})[kind] = str(Path(path).resolve())
    store.record("data.remember", {"kind": kind, "path": str(Path(path).resolve())})
    store.save()
    emit(ctx, {"ok": True, "imports": store.state["imports"]})


@data_group.command("sample")
@click.argument("output", type=click.Path(dir_okay=False))
@click.pass_context
def data_sample(ctx: click.Context, output: str) -> None:
    rows = [
        {
            "listing_id": "1001",
            "shop": "BrightMockupStudio",
            "title": "Personalized Wall Art Print Custom Family Portrait Gift",
            "description": "A custom printable wall art gift with personalized names, warm neutral colors, sizing details, and instant digital delivery instructions.",
            "tags": "wall art;custom print;family portrait;personalized gift;digital download;home decor;printable art;anniversary gift;custom poster;minimalist art;portrait print;new home gift;gift for mom",
            "price": "18.00",
            "views": "1200",
            "favorites": "88",
            "sales": "42",
            "image_count": "8",
            "materials": "digital file;printable",
            "created": "2026-01-10",
            "status": "active",
        },
        {
            "listing_id": "1002",
            "shop": "BrightMockupStudio",
            "title": "Printable Wedding Welcome Sign Template",
            "description": "Editable wedding welcome sign template with simple instructions, multiple sizes, and download information.",
            "tags": "wedding sign;welcome sign;printable wedding;editable template;wedding decor;minimalist sign;bride gift;ceremony sign;reception sign;instant download",
            "price": "9.50",
            "views": "780",
            "favorites": "51",
            "sales": "25",
            "image_count": "6",
            "materials": "digital file",
            "created": "2026-02-20",
            "status": "active",
        },
        {
            "listing_id": "2001",
            "shop": "CozyCraftSupply",
            "title": "Crochet Pattern for Plush Bunny",
            "description": "Beginner friendly crochet bunny pattern with step by step instructions and materials list.",
            "tags": "crochet pattern;bunny pattern;plush pattern;amigurumi;pdf pattern;craft supply;beginner crochet;easter crochet;toy pattern;digital pattern;crochet bunny;stuffed animal;handmade toy",
            "price": "5.25",
            "views": "2150",
            "favorites": "200",
            "sales": "140",
            "image_count": "9",
            "materials": "pdf;yarn guide",
            "created": "2025-11-01",
            "status": "active",
        },
    ]
    count = write_csv(output, rows)
    emit(ctx, {"ok": True, "path": str(Path(output).resolve()), "rows": count})


cli.add_command(data_group)


from cli_anything.erank.extensions import register_extensions


register_extensions(
    cli=cli,
    live_group=live_group,
    competitor_group=competitor_group,
    listing_group=listing_group,
    keyword_group=keyword_group,
    shop_group=shop_group,
    tools_group=tools_group,
    trends_group=trends_group,
)
