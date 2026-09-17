import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


STAGES = {
    "QUEUED",
    "CLAIMED",
    "FACTS_READY",
    "IMAGES_READY",
    "ETSY_EDITING",
    "ETSY_DRAFT_SAVED",
    "ETSY_DRAFT_VERIFIED",
    "IN_REVIEW",
    "WAITING_LOGIN",
    "WAITING_CAPTCHA",
    "WAITING_RUNTIME",
    "FAILED",
}


def utc_now():
    return datetime.now(timezone.utc)


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def main():
    parser = argparse.ArgumentParser(description="Atomically update an unattended Etsy job state file.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--stage", required=True, choices=sorted(STAGES))
    parser.add_argument("--status", default="active")
    parser.add_argument("--lease-owner")
    parser.add_argument("--lease-minutes", type=int, default=30)
    parser.add_argument("--expected-stage", choices=sorted(STAGES))
    parser.add_argument("--etsy-draft-id")
    parser.add_argument("--blocker-class")
    parser.add_argument("--blocker-detail")
    parser.add_argument("--increment-attempt", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    state = {}
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
        if str(state.get("productId")) != args.product_id:
            raise SystemExit("product_id does not match the existing state file")
        if args.expected_stage and state.get("stage") != args.expected_stage:
            raise SystemExit(f"expected stage {args.expected_stage}, found {state.get('stage')}")

    now = utc_now()
    state.update(
        {
            "productId": args.product_id,
            "stage": args.stage,
            "status": args.status,
            "updatedAt": iso(now),
            "heartbeatAt": iso(now),
            "attemptCount": int(state.get("attemptCount", 0)) + int(args.increment_attempt),
        }
    )
    if args.lease_owner:
        state["leaseOwner"] = args.lease_owner
        state["leaseExpiresAt"] = iso(now + timedelta(minutes=args.lease_minutes))
    if args.etsy_draft_id is not None:
        state["etsyDraftId"] = args.etsy_draft_id
    if args.blocker_class is not None:
        state["blockerClass"] = args.blocker_class
    if args.blocker_detail is not None:
        state["blockerDetail"] = args.blocker_detail
    if args.stage in {"ETSY_DRAFT_VERIFIED", "IN_REVIEW"}:
        state["lastVerifiedAt"] = iso(now)

    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)
    print(json.dumps(state, ensure_ascii=False))


if __name__ == "__main__":
    main()
