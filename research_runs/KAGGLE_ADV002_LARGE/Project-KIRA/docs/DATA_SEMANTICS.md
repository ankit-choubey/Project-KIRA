# KIRA Data Semantics & Null Handling Standard

**Rule Definition**: `null == NOT MEASURED`  

---

## 1. Core Principle
In scientific and payment security reporting, **an unmeasured metric is fundamentally different from a zero metric**.
- `0.00%` attack success rate means an empirical attack was attempted and repelled 100% of the time.
- `null` attack success rate means no attack was evaluated under this configuration.

Treating `null` as `0.0` is an empirical falsehood that invalidates scientific claims.

---

## 2. Forbidden Coercions
Under no circumstances may any adapter, backend route, script, or frontend component execute the following conversions:
* ❌ `null` → `0` or `0.0`
* ❌ `null` → `0.0%`
* ❌ `null` → `false`
* ❌ `null` → `success`
* ❌ `null` → `"N/A"` (renders ambiguously)

---

## 3. Mandatory UI Presentation
When a metric value is `null` / `None`:
1. **Text**: Must display as `"Not measured"`.
2. **Style**: Must use muted, desaturated typography with italic styling (`font-style: italic; opacity: 0.6;`).
3. **Chip / Tag**: Must NOT be rendered as a green or grey success/value badge. It must render as an absence.
4. **Drawer**: The Provenance Drawer must indicate status `NOT_MEASURED` or `LOW_SAMPLE` and provide the reason (e.g. stage gated, insufficient sample count $n < 30$).
