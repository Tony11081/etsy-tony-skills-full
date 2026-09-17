#!/usr/bin/env python3
import argparse
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def money(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("money values must be finite numbers") from exc
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError("money values must be non-negative")
    return amount


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate the user's GigaB2B-to-Etsy draft price."
    )
    parser.add_argument("--unit-price", required=True, type=money)
    parser.add_argument("--shipping-max", required=True, type=money)
    parser.add_argument("--total-max", type=money)
    parser.add_argument("--markup", type=money, default=Decimal("150"))
    parser.add_argument("--divisor", type=money, default=Decimal("0.7"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.divisor == 0:
        parser.error("--divisor must be greater than zero")

    computed_landed = args.unit_price + args.shipping_max
    cost_basis = args.total_max if args.total_max is not None else computed_landed
    if args.total_max is not None and abs(args.total_max - computed_landed) > Decimal("0.01"):
        parser.error("--total-max must match --unit-price + --shipping-max within USD 0.01")

    price = ((cost_basis + args.markup) / args.divisor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    result = {
        "unit_price": f"{args.unit_price:.2f}",
        "shipping_max": f"{args.shipping_max:.2f}",
        "cost_basis": f"{cost_basis:.2f}",
        "markup": f"{args.markup:.2f}",
        "divisor": str(args.divisor),
        "etsy_price": f"{price:.2f}",
        "formula": "(cost_basis + markup) / divisor",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"USD {result['etsy_price']}")


if __name__ == "__main__":
    main()
