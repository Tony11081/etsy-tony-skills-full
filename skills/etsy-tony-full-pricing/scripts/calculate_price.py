#!/usr/bin/env python3
"""Deterministic Etsy collaboration pricing calculator."""

from __future__ import annotations

import argparse
import json
import math


def positive_number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than 0")
    return number


def nonnegative_number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than or equal to 0")
    return number


def percentage(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or not 0 <= number < 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return number


def money(value: float) -> float:
    return round(value + 1e-12, 2)


def price_for_net_margin(
    cost: float,
    target_margin: float,
    etsy_variable_rate: float,
    etsy_fixed_fee: float,
    ad_rate: float,
    partner_rate: float,
) -> float:
    retained_rate = (1 - partner_rate) * (1 - etsy_variable_rate - ad_rate)
    denominator = retained_rate - target_margin
    if denominator <= 0:
        raise ValueError("rates leave no room for the requested net margin")
    return (cost + (1 - partner_rate) * etsy_fixed_fee) / denominator


def evaluate_price(
    price: float,
    cost: float,
    etsy_variable_rate: float,
    etsy_fixed_fee: float,
    ad_rate: float,
    partner_rate: float,
) -> dict[str, float | bool]:
    etsy_fee = price * etsy_variable_rate + etsy_fixed_fee
    advertising = price * ad_rate
    partner_base = max(0.0, price - etsy_fee - advertising)
    partner_payment = partner_base * partner_rate
    profit = price - cost - etsy_fee - advertising - partner_payment
    no_ad_etsy_fee = price * etsy_variable_rate + etsy_fixed_fee
    no_ad_partner_base = max(0.0, price - no_ad_etsy_fee)
    no_ad_profit = price - cost - no_ad_etsy_fee - no_ad_partner_base * partner_rate
    break_even_ad_cost = max(0.0, no_ad_profit / (1 - partner_rate))
    return {
        "etsy_fee": money(etsy_fee),
        "advertising": money(advertising),
        "partner_base": money(partner_base),
        "partner_payment": money(partner_payment),
        "final_profit": money(profit),
        "final_margin_percent": round(profit / price * 100, 2),
        "break_even_ad_cost": money(break_even_ad_cost),
        "break_even_ad_rate_percent": round(break_even_ad_cost / price * 100, 2),
        "profitable": profit >= 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cost", required=True, type=positive_number, help="Total landed cost")
    parser.add_argument("--price", type=positive_number, help="Optional current selling price")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--etsy-variable-rate", type=percentage, default=9.5)
    parser.add_argument("--etsy-fixed-fee", type=nonnegative_number, default=0.45)
    parser.add_argument("--ad-rate", type=percentage, default=15.0)
    parser.add_argument("--partner-rate", type=percentage, default=7.0)
    parser.add_argument("--gross-margin", type=percentage, default=45.0)
    parser.add_argument("--target-net-margin", type=percentage, default=15.0)
    parser.add_argument("--safety-net-margin", type=percentage, default=20.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    etsy_variable = args.etsy_variable_rate / 100
    advertising = args.ad_rate / 100
    partner = args.partner_rate / 100
    gross_margin = args.gross_margin / 100
    target_margin = args.target_net_margin / 100
    safety_margin = args.safety_net_margin / 100

    if etsy_variable + advertising >= 1:
        raise SystemExit("etsy variable rate plus ad rate must be below 100%")
    if safety_margin < target_margin:
        raise SystemExit("safety net margin must be at least the target net margin")

    break_even = price_for_net_margin(
        args.cost, 0, etsy_variable, args.etsy_fixed_fee, advertising, partner
    )
    gross_price = args.cost / (1 - gross_margin)
    target_price = price_for_net_margin(
        args.cost, target_margin, etsy_variable, args.etsy_fixed_fee, advertising, partner
    )
    safety_price = price_for_net_margin(
        args.cost, safety_margin, etsy_variable, args.etsy_fixed_fee, advertising, partner
    )
    exact_recommended = max(gross_price, target_price)
    rounded_recommended = math.ceil(exact_recommended)

    result: dict[str, object] = {
        "currency": args.currency,
        "cost": money(args.cost),
        "assumptions": {
            "etsy_variable_rate_percent": args.etsy_variable_rate,
            "etsy_fixed_fee": money(args.etsy_fixed_fee),
            "advertising_rate_percent": args.ad_rate,
            "partner_rate_percent": args.partner_rate,
            "gross_margin_baseline_percent": args.gross_margin,
            "target_final_net_margin_percent": args.target_net_margin,
            "safety_final_net_margin_percent": args.safety_net_margin,
        },
        "prices": {
            "break_even": money(break_even),
            "gross_margin_baseline": money(gross_price),
            "target_net_margin": money(target_price),
            "safety_net_margin": money(safety_price),
            "recommended_exact": money(exact_recommended),
            "recommended_rounded_up": rounded_recommended,
        },
        "recommended_price_evaluation": evaluate_price(
            rounded_recommended,
            args.cost,
            etsy_variable,
            args.etsy_fixed_fee,
            advertising,
            partner,
        ),
    }
    if args.price is not None:
        result["current_price"] = money(args.price)
        result["current_price_evaluation"] = evaluate_price(
            args.price,
            args.cost,
            etsy_variable,
            args.etsy_fixed_fee,
            advertising,
            partner,
        )
        result["current_price_meets_recommendation"] = args.price >= exact_recommended

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
