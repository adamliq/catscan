# other/

Data for the **Other Events** tab in the top-level `index.html` — event
and log-type references for vendors outside the Microsoft/AWS/Linux/
Threat-Detection catalogues. Unlike those four, this isn't one schema:
each vendor keeps whatever shape its own documentation actually has
rather than being forced into a common row shape. FortiGate's log
reference, FortiManager/FortiAnalyzer's log schema, Juniper EX-series's
log schema, and Infoblox DDI's log reference (all below) look nothing
alike — FortiGate has per-subtype CLI/GUI enable instructions, an
example log line, and a confidence rating; FortiManager/FortiAnalyzer
has a numeric category code, a `product` split (FortiManager vs
FortiAnalyzer), and a composite log-ID format instead; Junos doesn't use
a Fortinet-style type/subtype model at all — it organizes logs by
facility, severity, and a per-process/daemon message-tag catalog, plus
two entirely different message envelopes (BSD-style vs. RFC 5424
structured-data) rather than one common field set; Infoblox's category/
prefix reference has no enable instructions, confidence rating, or
product split at all, and its field schemas — several distinct ones,
one per exported log type, rather than one set of fields common to
every row — don't fold into its Log Types table as common-field rows
the way the other three vendors' do, since they aren't actually common
across Infoblox's own rows — and the tab doesn't paper over any of that:
each vendor gets its own flatten/render/modal logic in `index.html`,
sharing only the visual language (rail + toolbar + table + detail modal,
a Log Types/Reference mode toggle for material that doesn't belong
repeated per row) via the same `#app-other`-scoped CSS classes, not a
common data model.

The header carries a real vendor picker now that more than one vendor
exists — it was a single always-active pill through FortiGate alone, on
the stated basis that a picker isn't worth building for one option; it
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

- `data/juniper_switch_log_schema.json` — Juniper EX-series (Junos OS)
  switch log reference, compiled from Junos OS System Logging
  documentation and the System Log Messages Reference (see the file's
  own `source_documentation.urls` for every citation). Kept exactly as
  compiled, not reshaped. Junos has no top-level type/subtype split the
  way FortiGate (traffic/event/utm) or FortiManager (event/appevent) do
  — it's organized instead by 13 syslog `facilities`, 10 `severity_levels`,
  and a flat `message_tag_categories` catalog of 18 processes/daemons
  (chassisd, l2ald, lacpd, and so on — filtered from the full
  System Log Messages Reference's 100+ process chapters down to the ones
  relevant to an EX-series switch), each with a `covers` description
  rather than a per-tag field list or confidence rating — individual
  message tags within a category (e.g. `UI_COMMIT`, `LACPD_TIMEOUT`)
  aren't enumerated, so the Log Types explorer's single real row "type"
  here is the message-tag category, not a Fortinet-style grouping.

  What replaces FortiGate's confidence rating and FortiManager's
  `product` split is a `format` distinction on the file's other content:
  Junos logs use two genuinely different message envelopes rather than
  one common field set — a `standard_format` (default BSD-syslog-style,
  7 fields: `TAG`, `process`, `hostname`, and so on) and a
  `structured_data_format` (RFC 5424-compliant, enabled via the
  `structured-data` statement, 9 fields: `MSGID`, `STRUCTURED-DATA`, and
  so on), each with its own `example_raw_message`. Both formats' fields
  (16 total) are folded into the Log Types explorer the same way the
  other two vendors fold in their common fields — their own "Common
  fields" rail filter, each row tagged with a `format` badge (Standard /
  Structured-data) in place of a confidence rating or Product badge —
  and both are shown in full in the Reference view's "Message formats"
  section, alongside the facilities and severity-level tables and the
  four source URLs.

- `data/infoblox_log_reference.json` — Infoblox DDI (NIOS / Universal
  DDI) log category reference, compiled from data supplied directly by
  the repository maintainer rather than fetched from a published guide
  (see the file's own `source_documentation.note` — unlike the other
  three vendors, no source URL was supplied for this pass, though the
  `field_schemas.notes` array below does cite which official guides the
  field mappings themselves came from). Its `category_groups` (what the
  Log Types table itself renders) is a plain 75-row category/prefix/
  description reference with no enable instructions, example line,
  confidence rating, or product split of its own, across 4 groups:
  **Syslog Forwarding** (47 rows — the literal prefix NIOS puts on each
  forwarded syslog line, e.g. `client`, `dhcpd`, `AUTH_RADIUS`), **DNS
  Logging Categories (DNS Properties)** (16 rows — NIOS's own on-box
  BIND logging categories, configured separately from Syslog Forwarding
  and overlapping it in 13 of its 16 rows, with a handful of genuine
  differences noted on the group itself: `rate-limit` here vs.
  `security` there, a combined `transfer-in`/`transfer-out` naming here
  vs. separate `xfer_in`/`xfer_out` there), **Universal DDI Service
  Logs** (9 rows — the cloud-managed product's own service log sources),
  and **Universal DDI Exported Log Files** (3 rows — bulk export types
  rather than a live category). Because there's no severity table or
  source-citation list sitting alongside those 75 rows, `category_group`
  is the rail's only real top-level type (exactly like the other three
  vendors' real types), with each group's own explanatory note surfaced
  in its rows' detail modal instead of a Reference section that would
  otherwise hold only that.

  What *does* justify a Log Types/Reference toggle here is a second,
  separate top-level key, `field_schemas` — added in a follow-up pass
  once it became clear the category list alone was leaving out how each
  exported log type is actually structured. Unlike FortiGate's/
  FortiManager's/Juniper's common fields (one shared envelope every row
  in their Log Types table gets tagged with), Infoblox's field schemas
  are per-log-type and mutually exclusive — a DNS query/response schema,
  a DHCP lease schema, and three Universal DDI Parquet export schemas
  (DNS response/query, RPZ, IPAM metadata) — so folding them into the
  category table as common-field rows the way the other vendors do would
  misrepresent them as universal when they aren't. They get their own
  four-section Reference view instead: **DNS query/response fields** (21
  rows, each mapped across the internal field name and its CEF/LEEF/
  Splunk CIM equivalents — the same three SIEM-normalization schemes
  Threat Detection's own detections cite — plus 7 additional fields
  BloxOne Threat Defense adds), **DHCP lease fields** (18 rows, same
  four-way mapping), **Universal DDI exported log files (Parquet)** (the
  three Parquet schemas' field tables — RPZ's explicitly described as
  extending the DNS schema rather than replacing it, matching how
  Infoblox's own docs describe it), and **Notes** (4 free-text
  caveats, including the one citing which official guides the fields
  came from — the closest thing this file has to a sources list, kept
  as plain text rather than turned into fake clickable links).

All four files `fetch()` at runtime rather than embed inline (same
trade-off as AWS Events and Threat Detection's Heat Coverage tab: needs
the page served over http(s), not opened as a local `file://`), and all
four register their rows on the tab's shared `window.__compHub['other']`
entry (merged across vendors, each row tagged with its own `vendor` so
a cross-catalogue search result opens on the right vendor's own panel
and tab).

There's no build tool here (unlike `aws/tools/build_aws_json.py`) since
all four files are used as delivered, not derived from another file in
this repo.
