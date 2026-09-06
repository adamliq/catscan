# other/

Data for the **Other Events** tab in the top-level `index.html` — event
and log-type references for vendors outside the Microsoft/AWS/Linux/
Threat-Detection catalogues. Unlike those four, this isn't one schema:
each vendor keeps whatever shape its own documentation actually has
rather than being forced into a common row shape. FortiGate's log
reference, FortiManager/FortiAnalyzer's log schema, Juniper EX-series's
log schema, Infoblox DDI's log reference, Zscaler's Splunk onboarding
reference, Cisco IOS XE's system message logging (syslog) reference,
and Cisco Catalyst SD-WAN's comprehensive logging reference
(all below) look nothing alike — FortiGate has per-subtype
CLI/GUI enable instructions, an example log line, and a confidence
rating; FortiManager/FortiAnalyzer has a numeric category code, a
`product` split (FortiManager vs FortiAnalyzer), and a composite log-ID
format instead; Junos doesn't use a Fortinet-style type/subtype model at
all — it organizes logs by facility, severity, and a per-process/daemon
message-tag catalog, plus two entirely different message envelopes
(BSD-style vs. RFC 5424 structured-data) rather than one common field
set; Infoblox's category/prefix reference has no enable instructions,
confidence rating, or product split at all, and its field schemas —
several distinct ones, one per exported log type, rather than one set of
fields common to every row — don't fold into its Log Types table as
common-field rows the way the other vendors' do, since they aren't
actually common across Infoblox's own rows; Zscaler's is the vendor
closest to FortiGate's own shape (per-input configuration instructions
and a per-input field list) but adds two more per-input datasets
(Splunk CIM eventtype/tag coverage and low-level CIM field-alias
mappings) that don't belong in the per-row modal alone, plus a
145-row field-mapping table too large to repeat per row; Cisco IOS
XE's is the odd one out entirely — it isn't a log-type catalog at
all, since the source says plainly that "there are thousands of
individual messages" and points to the per-release System Message Guide
as the authoritative list rather than enumerating them, so there's no
per-row confidence rating, product/format split, or example log line the
way FortiGate/FortiManager/Juniper/Zscaler have — its "Log Types" table
is four different named-thing lists (facilities, logging destinations,
configuration commands, advanced features) standing in for that shape
instead; and Cisco Catalyst SD-WAN's is the richest of the seven in raw
material but the least catalog-shaped — local log files, syslog
message-format templates, two independent severity scales (syslog's own
8 levels and a separate 4-level alarm/event scale), software modules
each with their own enumerated sample syslog messages, alarms/events,
audit logs, and operational reference (binary trace, remote logging) —
with no single per-row confidence rating, product, or format axis
running through all of it the way the other six vendors each have one
running through theirs, so its Log Types table is three genuinely
different row shapes (local log file / software module / syslog
message) rather than one. The tab doesn't paper over any of that: each
vendor gets its own flatten/render/
modal logic in `index.html`, sharing only the visual language (rail +
toolbar + table + detail modal, a Log Types/Reference mode toggle for
material that doesn't belong repeated per row) via the same
`#app-other`-scoped CSS classes, not a common data model.

Every vendor also carries a third mode, **Schema Explorer**, mirroring
Windows Events' own Schema Explorer tab: a flat, searchable table of
every field a vendor's source actually enumerates, distinct from that
vendor's own Log Types table. Two vendors' sources have real *per-row*
field data — FortiGate (63 fields across 7 of its 40 subtypes — the
ones with `confidence: "verified"`) and Zscaler (224 fields across 13
of its 15 overview inputs) — so clicking a field there jumps back to
Log Types and opens the exact row it came from, the "View this event"
pattern Windows' own version uses. Two more vendors' sources have field
data too, but shaped differently — common to a whole category rather
than tied to one Log Type row, so there's no individual row to jump
back to on click: Cisco Catalyst SD-WAN's `common_alarm_event_fields`
(13 fields, common to every alarm/event) and `audit_logs.common_fields`
(9 fields, common to every audit entry), and Infoblox's DNS
query/response (21), DHCP lease (18), and Universal DDI Parquet export
(67) field schemas. Both still get the same flat, searchable table —
22 fields for Cisco Catalyst SD-WAN, 106 for Infoblox — but clicking a
field jumps to and expands the Reference section it's already fully
documented in (Alarms & events / Audit logs for Cisco Catalyst SD-WAN;
DNS query/response fields / DHCP lease fields / Universal DDI exported
log files for Infoblox) instead of opening a row's modal. The
remaining three — FortiManager (per-subtype fields explicitly not
enumerated in the source), Juniper (individual message tags within a
category aren't enumerated, only the category itself), and Cisco IOS
XE (its only field-shaped data is the 6 common message-format fields,
already flat and searchable as their own Log Types rows and detailed
in full under Reference › Message format — nothing left to build a
per-facility or per-mnemonic schema list from without inventing one) —
genuinely have nothing to flatten here without inventing a schema the
source doesn't draw, so their Schema Explorer mode is a single
explanatory note instead of an empty table pretending there's data
behind it.

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

  Those same 106 fields (21 DNS + 18 DHCP + 67 Parquet, across the
  three Parquet sub-schemas' own `main_fields`/`resource_record`/
  `session_record` groupings) are what Schema Explorer flattens into
  its own searchable table here — real field data, not the empty-note
  treatment FortiManager's/Juniper's/Cisco IOS XE's genuinely-empty
  sources get, but not per-row either, since none of the three schemas
  ties one-to-one to a category row the way FortiGate's/Zscaler's do.
  Clicking a field jumps to and expands the Field Schemas section it's
  already fully documented in, in place of the "open the owning row's
  modal" behavior the two per-row vendors use.

- `data/zscaler_splunk_onboarding_reference.json` — a Zscaler-to-Splunk
  onboarding reference (title: "Zscaler to Splunk Onboarding Reference"),
  compiled by reading the real Zscaler Technical Add-on for Splunk
  package (Splunkbase app 3865, `TA-Zscaler_CIM`, v4.1.5) directly —
  `default/eventtypes.conf`, `default/tags.conf`, `default/props.conf` —
  rather than from public documentation alone, per the file's own
  provenance notes. Of the five vendors, this one's shape is the closest
  to FortiGate's: a 15-row `overview` of log inputs (ZIA's Web/Firewall/
  DNS/Tunnel/Alerts/Admin-Audit/Sandbox logs, ZPA's App-Access/Auth/
  Connector/Browser-Access/Web-Inspection/Admin-Audit logs, and two
  config-object lookups), each with its own configuration instructions
  (`configuration_settings`, the direct analog of FortiGate's CLI/GUI
  enable block) and — for 13 of the 15 — a per-input field list
  (`field_schemas`, joined by the `overview` row's own `input` name).
  What replaces FortiGate's confidence rating is an official-vs-unofficial
  distinction on the file's own `app` field (`Zscaler Technical Add-on
  for Splunk` for 13 rows vs. `TA-zscaler-api (unofficial community
  add-on)` for the two config-object lookups), reusing the exact
  verified/typical badge colors under new labels ("Official TA" /
  "Community add-on").

  Two more datasets don't fit per-row the way FortiGate's common fields
  do, because they're not universal either: `cim_coverage` (18 rows —
  which Splunk CIM eventtype/tags/data-models apply to a sourcetype, down
  to specific filtered subsets like the Web log's malware- and
  DLP-flagged rows) and `cim_field_mapping` (145 rows — the TA's actual
  per-sourcetype FIELDALIAS/EVAL directives, confirmed from its shipped
  `props.conf`, not inferred). Both get matched into each Log Type row's
  own modal by sourcetype (prefix-matched for `cim_coverage`'s filtered
  variants), the same "material specific to this row lives in its modal"
  principle the other four vendors already follow — but
  `cim_field_mapping` is also large enough (145 rows) that it gets its
  own full Reference-view table alongside a **Methodology notes** section
  (the file's three other top-level `*_notes` caveats: `cim_coverage_notes`,
  `cim_field_mapping_notes`, `ta_extra_sourcetypes_notes` — the fourth,
  `overview_notes`, is the Reference view's own intro line, the same
  role FortiGate's logging-prerequisites line plays).

  Two sourcetypes the file's own `cim_coverage`/`cim_field_mapping`
  entries flag as "not previously covered" by the 15-row overview
  (`zscalernss-audit`, a syslog-delivered variant of ZIA's admin-audit
  data; `zscalerlss-zpa-pse`, ZPA Private Service Edge logs) become their
  own Log Type rows too, rather than being silently dropped for not
  fitting the original 15-row scope. A separate `ta_extra_sourcetypes`
  array (11 rows: SaaS Security/CASB, Workload Segmentation, Deception,
  DLP Incident Reports, Posture Control, and five Cloud & Branch
  Connector "NSS for Workloads" feeds) covers sourcetypes the real TA
  package ships but that fall outside this reference's original ZIA/ZPA
  scope entirely — these get their own **Other Zscaler products**
  top-level type in the rail, alongside **ZIA** and **ZPA** for the
  rest, rather than being tucked into a Reference-only appendix where
  they wouldn't be searchable alongside everything else.

- `data/cisco_ios_xe_logging_reference.json` — a Cisco IOS XE system
  message logging (syslog) reference (wrapper key `cisco_ios_xe_logging`
  kept intact, not reshaped), covering Catalyst switches, ASR/ISR
  routers, and IOS XE Catalyst SD-WAN devices. Unlike the other five
  vendors above, this isn't a log-type catalog at all — the source says
  plainly that "there are thousands of individual messages" and points
  to the per-release System Message Guide as the authoritative list
  rather than enumerating them, so there's no per-row confidence rating,
  product/format split, or example log line the way FortiGate's/
  FortiManager's/Juniper's/Zscaler's have. What it has instead is a
  logging-configuration reference: **18 common facilities**
  (protocol/module codes like `OSPF`, `LINEPROTO`, `SYS`), **6 logging
  destinations** (console, buffer, monitor, file, remote syslog host,
  SNMP history table) each with its own enable command, **10 key
  configuration commands**, and **5 advanced features** (rate-limiting,
  discriminators, and so on) — four named-thing lists standing in for
  the Log Types table's usual per-subtype rows, rather than actual log
  types. **6 message-format fields** common to every syslog line
  (`FACILITY`, `SEVERITY`, `MNEMONIC`, `description`/`Message-text`,
  `seq no`, `timestamp`) fold into the same Log Types table as their own
  rows (a "Common fields" rail filter, exactly like FortiGate's/
  FortiManager's/Juniper's common fields), leaving 39 "real" rows
  (facilities + destinations + commands + features) counted separately
  from the 45-row table total the rail's "All types" shows.

  The Reference view carries what doesn't belong repeated per row:
  three message-format templates (standard, with-hostname,
  extended/sub-facility) with 4 example log lines between them, an
  8-level severity table (`emergencies` through `debugging`) with 3
  additional caveats, a 6-key default-behavior summary (is console
  logging on by default, what's the default buffer size story, and so
  on), 5 free-text notes (4 general notes plus the IOS XE Catalyst
  SD-WAN caveat that both standard and SD-WAN-specific facilities like
  `FTMD`/`OMP`/`VDAEMON` appear on those devices, merged in from a
  separate `relation_to_sdwan` key), and 5 source citations (kept as
  plain text, not turned into fake links, matching Infoblox's own
  convention). Since none of the four named-thing lists carry a field
  list of their own, Schema Explorer here is a single explanatory note
  like FortiManager's/Juniper's/Infoblox's, not an empty table.

- `data/cisco_sdwan_logging_reference.json` — a comprehensive Cisco
  Catalyst SD-WAN (formerly Viptela / Cisco SD-WAN) logging reference,
  kept exactly as delivered (wrapper key
  `cisco_catalyst_sdwan_logging_comprehensive` intact, not reshaped).
  Of the seven vendors, this one carries the most raw material but the
  least single catalog shape — no per-row confidence rating, product
  split, or format axis runs through all of it the way one axis runs
  through each of the other six vendors' rows. Its Log Types table is
  three genuinely different row shapes instead of one: **7 local log
  files** (`auth.log`, `vsyslog.log`, and so on, each with its own path
  and description), **8 software modules** (`CFGMGR`, `OMP`, `FTMD`,
  `VDAEMON`, `VCONFD`, `CFLOWD`, `CHMGR`, `MSGQ` — each with its own
  description and priority), and **32 syslog messages** (the modules'
  own enumerated `sample_messages`, each with a message number, an
  optional positional format template, a description, and an action
  code) — 47 rows total. A module's own row opens to a modal listing
  all of its own sample messages in one table (the same "material
  specific to this row lives in its modal" principle Zscaler's
  sourcetype-matched CIM tables already follow), while each message is
  also independently searchable as its own row, tagged with the module
  it belongs to.

  Two genuinely different severity scales exist side by side: syslog's
  own 8-level scale (`emergencies`/`debugging`, shared with Cisco IOS
  XE's own severity table) and a separate 4-level scale
  (Critical/Major/Medium/Minor) that alarms and events use instead —
  kept as two distinct Reference tables rather than merged into one,
  since the source itself never conflates them. `common_alarm_event_fields`
  (13 fields) and `audit_logs.common_fields` (9 fields) are each common
  only to their own narrow category — every alarm/event, every audit
  entry — not to the 47-row Log Types table the way FortiGate's/
  FortiManager's/Juniper's common fields are common to every one of
  their own rows, so they stay Reference-only tables (under **Alarms &
  events** and **Audit logs**) rather than becoming an invented
  "Common fields" rail chip with no real per-row home. `common_alarm_types_examples`
  (24 names) is explicitly framed by the source as illustrative rather
  than exhaustive, so it's rendered as a plain list inside the Alarms &
  events section rather than promoted to its own searchable rows the
  way the 32 actually-enumerated syslog messages are.

  Those same 22 category-common fields (13 alarm/event + 9 audit log)
  are what Schema Explorer flattens into its own searchable table here
  — not per-row fields the way FortiGate's/Zscaler's Schema Explorer
  content is, since neither category has individual Log Type rows of
  its own to tie a field to, but real field data all the same rather
  than the empty-note treatment FortiManager's/Juniper's/Cisco IOS
  XE's genuinely-empty sources get. Clicking a field jumps to and
  expands the Reference section it's already fully documented in
  (Alarms & events or Audit logs) in place of the "open the owning
  row's modal" behavior the two per-row vendors use, since there's no
  row to open instead.

  Everything else that doesn't belong repeated per row lives in the
  Reference view: three message-format templates (classic pre-20.15,
  newer from 20.15, RFC 5424) plus the vManage application log's own
  format, three examples between them, two alternative formats seen in
  other documentation, a 5-entry message-acronym glossary (`FTM`/`FTMD`,
  `RTM`, and so on), a 3-entry action-code lookup (what an `E`/`A`/`AE`
  tag on a syslog message means), binary trace support (5 daemons, 8
  trace levels) and remote logging (3 protocols, 4 notes), 6 general
  notes, and 5 source citations kept as plain text (matching Infoblox's
  own convention). The one dataset that doesn't fit any row or Reference
  section cleanly — `unused_standard_linux_files` (5 filenames Cisco
  Catalyst SD-WAN's own docs call out as present but unused) — gets a
  single short line above the Reference sections rather than being
  dropped or forced into a table of its own.

All seven files `fetch()` at runtime rather than embed inline (same
trade-off as AWS Events and Threat Detection's Heat Coverage tab: needs
the page served over http(s), not opened as a local `file://`), and all
seven register their rows on the tab's shared `window.__compHub['other']`
entry (merged across vendors, each row tagged with its own `vendor` so
a cross-catalogue search result opens on the right vendor's own panel
and tab).

There's no build tool here (unlike `aws/tools/build_aws_json.py`) since
all seven files are used as delivered, not derived from another file in
this repo.
