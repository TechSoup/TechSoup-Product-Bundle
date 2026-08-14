# Contract guard

`products.json` is the VKB's published "headless API" — the Offer Center and any
other tool `fetch` it and depend on its shape. This directory pins that shape so
the federation / standardization work (`civic/0.5` and beyond) can proceed
underneath it **without ever silently breaking a consumer.**

## Files

- `golden_products.json` — the frozen snapshot of the published contract.

## Usage

```bash
# verify the contract still holds (CI gate; exit 1 on a break)
python3 VKB-Core/scripts/check_contract.py

# deliberately bless an additive or version change (re-freeze the snapshot)
python3 VKB-Core/scripts/check_contract.py --update
```

The checker **rebuilds the catalog into a temp file** (it never touches the live
`Offer-Center/products.json`) and diffs it against the golden snapshot.

## What counts as a break vs. an allowed change

**Violation (fails the build):** anything that would break a consumer reading the
current shape —
- a product in the snapshot disappears,
- a key on a product is removed,
- a key's value changes,
- a stable `meta` key changes or disappears.

**Allowed (passes, reported as additive):**
- new products,
- new keys on a product (e.g. the federation `id`, an external `relations` edge),
- new `meta` keys (e.g. `namespace`),
- a change to `meta.profile` (the `civic/0.5` bump is expected — see
  `MUTABLE_META` in `check_contract.py`).

## Workflow

1. Make a standardization/federation change.
2. Run `build_products.py`, then `check_contract.py`.
3. If it reports only additive changes → you're safe, contract preserved.
4. If it reports violations → either fix them, or, if the change is intentional
   (e.g. you meant to bump `profile`), re-run with `--update` to bless it. Commit
   the updated `golden_products.json` alongside the change so the new contract is
   recorded.
