# other/

Data for the **Other Events** tab in the top-level `index.html` — event
and log-type references for vendors outside the Microsoft/AWS/Linux/
Threat-Detection catalogues. Unlike those four, this isn't one schema:
each vendor keeps whatever shape its own documentation actually has
rather than being forced into a common row shape. FortiGate's log
reference and FortiManager/FortiAnalyzer's log schema (below) look
nothing alike — one has per-subtype CLI/GUI enable instructions, an
example log line, and a confidence rating; the other has a numeric
category code, a `product` split (FortiManager vs FortiAnalyzer), and a
composite log-ID format instead — and the tab doesn't paper over that:
each vendor gets its own flatten/render/modal logic in `index.html`,
sharing only the visual language (rail + toolbar + table + detail modal,
a Log Types/Reference mode toggle for material that doesn't belong
repeated per row) via the same `#app-other`-scoped CSS classes, not a
common data model.

The header carries a real vendor picker now that a second vendor exists
— it was a single always-active pill through FortiGate alone, on the
stated basis that a picker isn't worth building for one option; it
became one the moment a second vendor's data arrived, not ahead of that
need.

- `data/fortigate_log_reference.json` — FortiGate log types, subtypes,
  field schema, and the CLI/GUI setting that turns each one on, compiled
  from the FortiOS 7.6.0 / 8.0.0 documentation (see the file's own
  `sources` array for every citation). Kept exactly as compiled, not
  reshaped — `index.html`'s Other Events tab `fetch()`es it at runtime
  and flattens its `types` → `subtypes` nesting into 40 rows client-side
  (6 traffic + 16 event + 18 UTM/security-profile subtypes; 7 rows
  `confidence: "verified"` — field list and example log line pulled
  directly from Fortinet's published reference — the remaining 33
  `"typical"`, following FortiOS's standard field conventions for that
  feature with log IDs confirmed but not confirmed field-by-field
  against a specific build).

  Beyond the 40 per-subtype rows, the file also carries reference
  material that doesn't belong repeated on every row — 8 severity
  levels, 26 fields common to every log line, and the logging
  prerequisites paragraph. The 26 common fields aren't only a static
  Reference-view table: each also becomes its own lightweight row
  (`type: "Common Field"`, a dash instead of a confidence badge, since
  a plain field definition doesn't carry one) in the *same* Log Types
  table — reachable through the ordinary search box and a dedicated
  "Common fields" rail filter, alongside the 40 subtype rows, rather
  than being reachable only via a second click into Reference. Severity
  levels and the logging-prerequisites paragraph stay Reference-only
  (they're not discrete named things a search would look for the way a
  field name is).

- `data/fortimanager_log_schema.json` — FortiManager and FortiAnalyzer's
  shared log-type schema (they document both products in one Log
  Message Reference guide), compiled from the FortiManager/FortiAnalyzer
  7.6.2 documentation. 37 subtypes across 2 top-level types (32
  `event` + 5 `appevent`; 20 rows apply to FortiManager, 17 to
  FortiAnalyzer — `appevent` is FortiAnalyzer-only, and a handful of
  `event` subtypes, like `fazsys`/`logdev`/`report`, are also
  FortiAnalyzer-only despite sharing the `event` type with FortiManager's
  own rows). Each subtype carries a `category` number rather than a
  confidence rating, since this file has one source doc rather than
  FortiGate's verified/typical split.

  This file's shape doesn't have per-subtype enable instructions, an
  example log line, or an enumerated field list the way FortiGate's
  does — the source material explicitly doesn't enumerate per-subtype
  fields ("hundreds of message IDs across all subtypes"), so the detail
  modal says exactly that rather than showing an empty section, and
  points at the Reference view's 12 common fields instead. What this
  file *does* carry that FortiGate's doesn't: a `log_id_format`
  explainer (how the 10-digit composite ID is built from type + category
  + message ID) and one `example_raw_message`, both rendered in the
  Reference view alongside the six source URLs. Like FortiGate's, the
  12 common fields are also folded into the Log Types explorer as their
  own rows (their own "Common fields" rail filter, a dash instead of a
  Product badge) — clicking one opens a small modal showing its data
  type and the one example value, rather than the fuller Identification
  block a real log-type subtype gets.

Both files `fetch()` at runtime rather than embed inline (same trade-off
as AWS Events and Threat Detection's Heat Coverage tab: needs the page
served over http(s), not opened as a local `file://`), and both
register their rows on the tab's shared `window.__compHub['other']`
entry (merged across vendors, each row tagged with its own `vendor` so
a cross-catalogue search result opens on the right vendor's own panel
and tab).

There's no build tool here (unlike `aws/tools/build_aws_json.py`) since
both files are used as delivered, not derived from another file in this
repo.
