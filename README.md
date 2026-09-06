# Cat Scan

*(Previously "Event Catalogue Compendium" / `catalogue-compendium` — moved
here.)*

The mark next to the name — a paw print behind a magnifying glass — is the
"Paw + Magnifier" concept from a five-direction logo exploration, picked
to run with. It appears twice: inline (themed, next to the wordmark in the
menu bar) and as the browser-tab favicon (fixed colors, since favicons
can't reference the page's own light/dark tokens).

A single entry point for [`Winevent-catalogue`](https://github.com/adamliq/Winevent-catalogue)
(4,737 Windows Event Log events),
[`linuxevent-catalogue`](https://github.com/adamliq/linuxevent-catalogue)
(77 Linux security/system events), and
[`Threat-detection-library`](https://github.com/adamliq/Threat-detection-library)
(4,017 platform-specific threat detections across fourteen catalogues),
merged into one self-contained web app with a menu to switch between them —
plus an **AWS Events** Action Explorer (21,164 AWS IAM actions across 455
services, each mapped to its CloudTrail event and ACSC logging guidance
where one exists) built directly in this repo from a [`Events_Other`](Events_Other/README.md)
data export rather than merged from an external source repo, and an
**Other Events** menu for vendor log/event references that don't belong to
any of the above — FortiGate's 40 log types, FortiManager/
FortiAnalyzer's 37, Juniper EX-series's 18 message-tag categories, DDI
Infoblox's 75 log categories, Zscaler's 28 log inputs, Cisco IOS XE's
39-row logging-configuration reference, and Cisco Catalyst SD-WAN's
47-row logging reference (see
[`other/`](other/README.md)) so far, with a real vendor picker and room
for more over time, each keeping
its own schema shape rather than a forced common one.

## Web lookup

`index.html` is a single, self-contained page (no build step, one runtime
fetch — see below) — open it directly in a browser. A menu bar at the top
switches between **Microsoft Events**, **AWS Events**, **Linux Events**,
**Threat Detection**, **Other Events**, and **Search**; Microsoft Events, Linux Events, and
Threat Detection are the exact lookup tool from their source repo (search,
filters, detail views, reference tables, and so on), running independently
side by side on the same page. AWS Events is this repo's own Action
Explorer, and Other Events its own vendor log-reference tab, both built to
match that same look and feel (see below). Your last-chosen tab is
remembered (`localStorage`) across visits.

All five catalogue tabs cap their page width the same way —
`max-width: min(1600px, 94vw)` — so every tab fills a wide screen instead
of sitting in a narrow column with unused margin either side; on anything
narrower than ~1700px the `94vw` term takes over and the page just fills
the viewport as before.

A **light/dark toggle** at the right of the menu bar switches the whole
page — the menu bar and Search pill, plus all five embedded apps — between
light and dark at once (it defaults to your OS preference until you click
it, then remembers your explicit choice). Threat Detection also ships its
own theme button in its own header, left over from the source app; the two
stay in sync — either one flips the whole page, since Threat Detection's
own button now hands off to the shared toggle rather than only touching
itself. Every text/background color pairing across Microsoft Events, Linux
Events, Threat Detection, and the shell chrome (both light and dark) was
checked against the [WCAG contrast formula](https://www.w3.org/TR/WCAG21/#contrast-minimum)
— not eyeballed — and the handful that fell short (a few de-emphasized
"faint" tokens, and Windows's accent color doubling as body-text link
color, all in light mode) were darkened just enough to clear AA, keeping
the same hue. AWS Events and Other Events are both new rather than merged from an
existing app, so their own palettes (AWS's blue accent, Other Events'
crimson — a nod to FortiGate's own brand red — each distinct from the
other tabs') were checked the same way from the start instead of
retrofitted.

**Search** is a sixth, shell-only pill: a single box that searches
Windows events, AWS IAM actions, Linux events, every Threat Detection
entry (detections and validations), and every Other Events vendor's log
types at once, grouped by source with up to 40 results per source. A **Sources** filter
row toggles Microsoft Events/AWS Events/Linux Events/Threat Detection/
Other Events in or out of the results, and a **Threat Detection type** row
(only meaningful when that source is on) separately toggles Detections
and Validations — both default to everything on. It's a thin layer on top
of the five apps, not a sixth schema — each app exposes a small
`{items, open}` index (id, title, a
short meta line, and a lowercased haystack of its own already-existing
fields) on `window.__compHub` for this to search over; clicking a result
switches to that catalogue's own tab and calls back into its own existing
selection/detail-opening code (`jumpToEvent`-style for Windows/Linux,
`openDetail`/`openValidationDetail` for Threat Detection, opening the
Action Explorer's own detail modal for AWS Events, the right vendor's own
log-type detail modal for Other Events) to actually show it there — so results
render exactly like they do from that app's own search, because they
*are* that app's own render path. AWS Events and Other Events each
register themselves on `window.__compHub` only once their own data has
finished loading (see below), so a search fired in the instant before
that finishes just won't have their results yet.

The five catalogues are **not** merged at the data level: they keep their
own ID schemes, column schemas, and reference tables exactly as authored
(Microsoft Events, Linux Events, and Threat Detection in their source
repos — see each repo's README for the full field reference; AWS Events in
[`Events_Other/aws_iam_actions_expanded.csv`](Events_Other/README.md), via
[`aws/`](aws/README.md); Other Events in [`other/`](other/README.md)'s own
per-vendor files, compiled from each vendor's own documentation). This page only merges the
*presentation* — one URL, one menu — not the underlying schemas, and each
Other Events vendor keeps whatever shape its own source material actually
has rather than being forced into a common row shape.

Three tabs fetch their data at runtime instead of embedding it inline, so
this page isn't fully "no external requests": the Threat Detection tab's
**Heat Coverage** sub-tab fetches its eleven `mitre-attack-*.json` files
(from `threat-detection/data/`, see below), the **AWS Events** tab
fetches its one `aws_iam_actions.json` file (from `aws/data/`, see below;
21,164 actions makes for a 6.5&nbsp;MB file, too large to comfortably
embed inline the way the other three catalogues' data is), and the
**Other Events** tab fetches `fortigate_log_reference.json`,
`fortimanager_log_schema.json`, `juniper_switch_log_schema.json`,
`infoblox_log_reference.json`, `zscaler_splunk_onboarding_reference.json`,
`cisco_ios_xe_logging_reference.json`, and `cisco_sdwan_logging_reference.json`
(from `other/data/`, see below — a modest ~46&nbsp;KB, ~10&nbsp;KB,
~9&nbsp;KB, ~32&nbsp;KB, ~97&nbsp;KB, ~9&nbsp;KB, and ~21&nbsp;KB
respectively, but all seven fetched rather
than embedded for consistency with the other two runtime-loaded tabs
and because Other Events is meant to grow more vendor files over time).
All three tabs
degrade gracefully under `file://` (browsers block
`fetch()` of local files) with an explanatory message — Heat Coverage the
same way the source repo already did, AWS Events and Other Events the
same way Heat Coverage does; serve the repo over http(s) (GitHub Pages,
`python3 -m http.server`, etc.) for those three spots specifically.
Everything else, including the other 4,017 detections and every
non-Heat-Coverage tab, works identically either way.

### How the merge was built

Three of the five catalogues arrive as source `index.html` files that
embed their app (styles, markup, data) in one file, and reuse a lot of the
same generic naming (`.panel`, `.card`, `.tab`, ids like
`search`/`list`/`detail`/`tabs`, etc.) — Winevent-catalogue and
linuxevent-catalogue deliberately share UI conventions, and
Threat-detection-library independently converges on the same common
patterns. Concatenating them naively would collide: matching CSS selectors
would bleed across apps, and shared `id="..."` values would make
`getElementById` return the wrong app's element. AWS Events and Other
Events are the other two — see their own paragraphs below — but each is
built directly into this repo following the same conventions, so both
participate in everything else described here (the shared
container-scoping pattern, the shared theme toggle, `window.__compHub`)
exactly like the other three.

So each of the three source apps was mechanically namespaced before
merging:

- Every element `id`/`for` gets a `win-`/`lnx-`/`td-` prefix (covering
  static HTML attributes and every dynamic `getElementById`/`querySelector`
  reference, including ones built via string concatenation or template
  literals — and, for Threat-detection-library, the `id="..."` on each of
  its 19 `<script type="application/json">` data blobs).
- Each app's `<style>` block is scoped by rewriting every selector to be a
  descendant of that app's own container (`#app-win` / `#app-lnx` /
  `#app-td`), including `:root` and `html`/`body` (so each app's CSS custom
  properties/theme variables stay independent, and compound selectors like
  `body.heat-active .search-wrap` still hit the right element once `body`
  becomes the container).
- Each app's script runs inside its own IIFE (so top-level `const`/`let`/
  `function` names in one app never collide with another's), and every
  `document.querySelector(All)` call is scoped to that app's own container
  element — otherwise a class-based query like `.panel` (used by more than
  one app's tab-switching logic) would also match and mutate *another*
  app's hidden DOM.
- The handful of functions invoked from inline `onclick="..."` attributes
  (which run in global scope, not inside the IIFE) are renamed and
  explicitly exported on `window` under their namespaced names.
- Threat-detection-library specifically: its dark/light theme toggle
  operates on the real `<html>`/`<body>` elements
  (`document.documentElement.setAttribute("data-theme", …)`,
  `document.body.classList.toggle("heat-active", …)`) — since this repo
  rescopes `:root`/`body` to `#app-td`, those calls are redirected to the
  container element too, or the toggle (and the Heat/Validations
  view-mode classes) would silently do nothing. Its eleven
  `data/mitre-attack-*.json` fetch paths are also repointed at
  `threat-detection/data/…` to match this repo's layout (see Structure).
- The shell's own light/dark toggle sets `data-theme` on `<body>` and on
  all five app containers at once, so Windows/Linux/AWS/Other Events'
  existing (but,
  before this toggle existed, unreachable-without-changing-your-OS-theme)
  `:root[data-theme="…"]` CSS and Threat Detection's own become live
  together. Its click handler is the one place this repo reaches back into
  Threat-detection-library's own code: `td-theme-toggle`'s listener now
  tries `document.getElementById('shell-theme-toggle').click()` first
  (falling back to its original self-contained logic if that element is
  ever absent), so either button drives all five apps and stays
  persisted under both a shared `compendium-theme` key and the source
  app's own pre-existing `tdl-theme` key.

(Found while adding the page-width fix mentioned above, and fixed
alongside it: the CSS namespacer that prefixes every selector with
`#app-win`/`#app-lnx`/`#app-td` split each rule's selector list on commas
*before* stripping CSS comments, so a comment containing a comma — plain
English, not code — before a selector could shear a stray word off the
front of the next selector instead of the real prefix. It only ever
mis-scoped three Threat Detection selectors that happen not to collide
with anything in the other two apps (`.lib-stats-wrap`, `.view-tabs-wrap`,
`.heat-view`), so it was invisible in practice, but it's fixed now
regardless.)

**AWS Events** and **Other Events**, unlike the other three, have no
source repo to namespace — each is written directly under its own
container id (`#app-aws`, `#app-other`), so its markup, `<style>` block,
and script follow the same conventions the namespacing step above
produces for the others (own IIFE, own CSS custom properties scoped to
its own container and that container's `[data-theme="dark"]`, every
query scoped to its own container) rather than needing to be transformed
into them. Neither app's data is embedded like Windows/Linux/Threat
Detection's core catalogues are, either: on load AWS Events `fetch()`es
`aws/data/aws_iam_actions.json` and Other Events fetches each vendor's
own file independently — `other/data/fortigate_log_reference.json`,
`other/data/fortimanager_log_schema.json`,
`other/data/juniper_switch_log_schema.json`,
`other/data/infoblox_log_reference.json`,
`other/data/zscaler_splunk_onboarding_reference.json`,
`other/data/cisco_ios_xe_logging_reference.json`, and
`other/data/cisco_sdwan_logging_reference.json` (see Structure) —
and only builds that vendor's stats tiles, rail list, and search table —
and registers its rows on the shared `window.__compHub['other']` entry
for the shell Search pill — once its own fetch resolves; each vendor
panel shows its own loading message (and, under `file://`, an
explanatory error) until then, the same pattern Threat Detection's own
Heat Coverage tab already used for its runtime fetches. The seven
vendors load and register independently, so a search fired before all
seven resolve just won't have the still-loading ones' results yet.

**AWS Events**' rail originally held only a Service filter; it now also
has **CloudTrail** and **ACSC** filter groups (`All actions` /
`Mapped` / `Not mapped`, and `All actions` / `Recommended` /
`Not recommended`), reusing the exact same `aws-service-chip` markup
and click-handling pattern as the Service rail — no new CSS, no new
interaction model, just two more instances of a pattern already proven
three times over. All three filters (service, CloudTrail, ACSC) and
the search box combine as an intersection, exactly like Cloud Actions
Explorer's own type-rail-plus-search filtering.

**Other Events** is built to hold more than one vendor over time. It
shipped with a single always-active "FortiGate" pill in its header on
the stated basis that a real selector isn't worth building for one
option; the second vendor, FortiManager/FortiAnalyzer, arrived days
later with a genuinely different shape — no confidence rating, no
per-subtype enable instructions or example line, no enumerated field
list, but a `product` split (FortiManager vs FortiAnalyzer) and a
composite log-ID format FortiGate's data doesn't have — which is exactly
the trigger that was waiting for: the header now carries a real,
clickable vendor picker (`FortiGate` / `FortiManager`, later joined by
`Juniper EX-series`, `DDI Infoblox`, `Zscaler`, `Cisco IOS XE`, and
`Cisco SD-WAN` — see below), each
vendor's whole panel (stats, rail, table, mode toggle, both modals) a
sibling `<div>` shown or hidden by the picker, each with its own
independent search/filter/mode state so switching vendors and switching
back preserves what you were doing on each.

FortiGate's own data — 40 log types (grouped `traffic`/`event`/`utm`)
each with CLI/GUI instructions for turning it on, an example raw log
line, and its own field list, plus material that doesn't belong repeated
per row (8 severity levels, 26 fields common to every log line) — keeps
its own **Log Types / Reference** mode toggle (visually modeled on Schema
explorer's own Search/Explore toggle). FortiManager/FortiAnalyzer's 37
log types get the identical toggle pattern but different Reference
content that matches *its* shape: a log-ID-format explainer (how the
10-digit composite ID is built) and 12 common fields with one example
raw message, no severity table (this source doesn't have one). Its
detail modal shows an Identification block (type, category number,
which product the subtype applies to) instead of enable/example
sections, and says plainly that per-subtype fields aren't enumerated in
the source ("hundreds of message IDs across all subtypes") rather than
showing an empty section or inventing one.

This is exactly the shape the tab's generic parts (container, theme
wiring, the vendor-tab switcher, `window.__compHub['other']`
registration — merged across vendors, each row tagged with its own
`vendor` so a cross-catalogue search result reopens on the right
vendor's panel — rail/toolbar/table/modal CSS) were meant to carry
forward for a second vendor without a rewrite; the parts specific to
*reading* each vendor's data (flattening its own nesting into rows,
rendering its own modal sections) got their own version instead of
being forced through FortiGate's, which is exactly why FortiManager's
rows don't have a confidence badge that isn't there or a fields list
that was never enumerated: nothing here is invented to fill a shape the
source data doesn't have.

Both vendors' common fields (FortiGate's 26, FortiManager's 12)
started out reachable only from the Reference view — a second click
away from the same search box that finds every other row, and outside
`window.__compHub` entirely. Both are now folded into the Log Types
table itself as their own lightweight rows (a `Common fields` rail
filter alongside the real types, a dash where a confidence/product
badge would be rather than a fabricated one, clicking one opens a
small modal instead of the full subtype detail) — reachable through
the same search box, the same rail, and the same cross-catalogue
search as every subtype row, without duplicating or removing the
Reference view's own table (severity levels and the FortiManager
log-ID-format explainer stay Reference-only, since they're not
individually-named things worth searching for the way a field name
is).

A third vendor, Juniper EX-series (Junos OS), arrived later and put the
generic/vendor-specific split to a harder test than FortiManager did:
Junos doesn't have a Fortinet-style type/subtype model at all — no
`traffic`/`event`/`utm` or `event`/`appevent` grouping, just a flat
18-row `message_tag_categories` catalog (one process/daemon per row,
e.g. `chassisd`, `lacpd`, `l2ald`) with a `covers` description in place
of a confidence rating or product split — so its Log Types table has
only one real row "type" (`category`) rather than several. What Junos
*does* have that neither Fortinet source does is two genuinely different
message envelopes rather one common field set: a `standard_format`
(BSD-syslog-style, 7 fields) and a `structured_data_format` (RFC
5424-compliant, 9 fields), each with its own example raw message. Rather
than force those two formats into a single undifferentiated "common
fields" bucket, each of the 16 fields folded into the Log Types table
carries a `format` badge (`Standard` / `Structured-data`, two new badge
colors added alongside FortiManager's `product` badges) so the two
envelopes stay visually distinguishable in the same table FortiGate's
confidence badges and FortiManager's product badges already share. The
Reference view gained a fourth collapsible section over FortiGate's
three (facilities, severity levels, message formats, sources — Junos
distinguishes facility from severity where FortiGate/FortiManager only
have one such table) rather than cramming a fourth concept into an
existing section. Once again, nothing in FortiGate's or FortiManager's
shape leaked into Juniper's rows: no confidence badge, no product split,
no per-tag field list that isn't in the source — just the same generic
container/picker/search/cross-catalogue-search machinery reused a third
time, and a third from-scratch flatten/render/modal implementation
underneath it.

A fourth vendor, DDI Infoblox (NIOS / Universal DDI), tested the split
from the opposite direction: rather than a genuinely different shape to
render, its source *started out* with less shape than any vendor before
it. Its initial data was a plain category/prefix/description reference —
75 rows across 4 `category_groups` (Syslog Forwarding, DNS Logging
Categories, Universal DDI Service Logs, Universal DDI Exported Log
Files) — with no enable instructions, no example line, no confidence
rating, no product split, and no field-envelope schema at all. Rather
than build a Log Types/Reference toggle with an empty or near-empty
Reference view just to match the other three vendors' silhouette, this
vendor shipped with no mode toggle at all: everything that first pass of
the source had fit in one table (`category_group` in the rail exactly
like the other three vendors' real top-level types), and each group's
own explanatory note — the two DNS category lists' partial overlap and
where their names/prefixes genuinely diverge, for instance — surfaced in
that group's rows' own detail modal instead of a separate section that
would otherwise hold only that one paragraph. Its data file also carries
a provenance difference worth being honest about: it was compiled from
data supplied directly by the repository maintainer rather than a
published vendor guide, and says so in its own
`source_documentation.note` rather than citing a URL it doesn't have.

A follow-up pass added exactly the shape that first version was missing:
a `field_schemas` key with the per-log-type field mappings a category
reference alone can't show — a DNS query/response schema and a DHCP
lease schema (each field mapped across its internal name and CEF/LEEF/
Splunk CIM equivalents, the same three SIEM-normalization schemes
Threat Detection's own detections already cite), and three Universal
DDI Parquet export schemas (DNS response/query, RPZ, IPAM metadata).
These aren't common fields the way FortiGate's/FortiManager's/Juniper's
are — each schema applies to one specific log type, not to every row in
the category table — so folding them in as common-field rows would
misrepresent them as universal when they're mutually exclusive instead.
That's exactly the trigger the mode toggle had been waiting for: DDI
Infoblox gained the same Log Types/Reference split the other three
vendors have (labeled "Field Schemas" here, since that's literally what
it holds), with four collapsible sections — DNS query/response fields,
DHCP lease fields, the three Parquet schemas, and a Notes section for
the source's own free-text caveats, including the one naming which
official guides the field mappings came from (kept as plain text, not
turned into fake clickable links the way the other three vendors' real
URLs are). Once again, the generic container/picker/search/
cross-catalogue-search machinery, and now the mode-toggle/Reference-view
machinery too, carried a fourth vendor's second pass without a rewrite,
and once again nothing was invented to fill a shape the source doesn't
have — first by *not* building UI for reference material that didn't
exist yet, then by building exactly the UI the material that arrived
actually called for, rather than forcing it through FortiGate's common-
fields shape because that shape was already there.

A fifth vendor, Zscaler, is the one whose source data comes closest to
FortiGate's own shape — a per-input list (`overview`, 15 rows across
ZIA and ZPA) where each row carries its own configuration instructions
and a per-input field list, the direct analog of FortiGate's per-subtype
CLI/GUI instructions and field list — compiled by reading the actual
Zscaler Technical Add-on for Splunk package (Splunkbase app 3865,
`TA-Zscaler_CIM` v4.1.5) directly rather than from public docs alone.
What replaces FortiGate's confidence rating is an official-vs-unofficial
axis already present in the source itself: 13 of the 15 inputs use the
real Zscaler Technical Add-on, the other two (config-object lookups) use
an unofficial community add-on — reusing the exact verified/typical
badge colors under new labels ("Official TA" / "Community add-on")
rather than inventing a new visual language for a distinction the data
already draws.

Two more Zscaler datasets don't fit per-row the way FortiGate's common
fields do, because — like Infoblox's field schemas — they aren't
universal either: `cim_coverage` (which Splunk CIM eventtype/tags/data
models apply to a sourcetype, including specific filtered subsets like
the Web log's malware- and DLP-flagged rows) and `cim_field_mapping`
(145 rows of the TA's actual per-sourcetype FIELDALIAS/EVAL directives,
confirmed from its shipped `props.conf`, not inferred). Both get matched
into each row's own modal by sourcetype, the same principle Infoblox's
CIM-adjacent data already followed — but `cim_field_mapping` is also
large enough on its own (145 rows) that it earns its own full table in
the Reference view, alongside a Methodology notes section for the
source's other three caveats. Two sourcetypes the data itself flags as
"not previously covered" by the 15-row overview become their own Log
Type rows rather than being silently dropped, and a separate 11-row
`ta_extra_sourcetypes` array — sourcetypes the real TA package ships but
that fall outside this reference's original ZIA/ZPA scope entirely
(CASB, Workload Segmentation, Deception, DLP Incident Reports, Posture
Control, and a distinct Cloud & Branch Connector product line) — gets
its own **Other Zscaler products** top-level type in the rail rather
than a Reference-only appendix, so it stays searchable alongside
everything else the same way Juniper's common fields and Infoblox's
field schemas already are.

One rendering bug surfaced and got fixed while building this vendor's
modal: several Zscaler field-name groups run far longer than one line
(e.g. one field entry alone is "srvocspresult / srvcertchainvalpass /
srvwildcardcert / srvcertvalidationtype / srvcertvalidityperiod"), and
the `<dl>`-based field list every other vendor's modal already uses
sizes its label column to `max-content` with `white-space: nowrap` —
correct for FortiGate's and Juniper's own short field names, but a
single field-name group that long forced that column to consume nearly
the entire modal width, squeezing every row's description into an
unreadable sliver. Zscaler's own Fields section renders as a table
instead (a field name column that wraps normally, not a label column
sized to its single longest entry) — a genuine layout fix that the
vendor-specific rendering split this whole tab is built around made
easy to isolate to just this one vendor, without touching the `<dl>`
rendering FortiGate's, FortiManager's, and Juniper's own modals still
use correctly.

Every one of the five vendors then gained a third mode, **Schema
Explorer**, mirroring Windows Events' own Schema Explorer tab: a flat,
searchable table of every field parsed out of an individual log-type
row (not the vendor's common fields, already flat and searchable as
their own Log Types rows) — clicking a field switches back to Log Types
and opens the exact row it came from, the same "View this event"
pattern Windows' original version uses, reusing each vendor's own
already-existing `xxOpenModal()` rather than building a second modal
type. Only two of the five vendors' sources actually have this kind of
per-row field data to flatten: FortiGate (63 fields across the 7 of its
40 subtypes marked `confidence: "verified"`) and Zscaler (224 fields
across 13 of its 15 overview inputs) — the other three (FortiManager,
Juniper, Infoblox) genuinely have nothing here without inventing a
per-row schema their own sources don't draw, so their Schema Explorer
mode is a single one-line explanation instead of a table that would
always read "no results." Adding this uniformly, rather than only to
the two vendors it applies to, is deliberate: a vendor's set of modes
is part of its own visual identity in the picker, and a menu that
silently changed shape per vendor would be harder to predict than one
that's occasionally honest about having nothing to show.

(Also fixed while adding this tab: `.compendium-tabs` had no
`flex-wrap`, so six tabs no longer fit one row on narrow/mobile
viewports — the row silently overflowed and, worse, clicking a tab
scrolled to it, dragging the whole page into an unwanted page-level
horizontal scroll rather than the tab row just wrapping onto a second
line the way `.compendium-menu` itself already does. One-line fix,
verified by clicking Other Events at a 375px viewport and confirming the
page no longer scrolls sideways.)

A sixth vendor, Cisco IOS XE, is the one whose source data doesn't
resemble a log-type catalog at all — its own documentation says plainly
that "there are thousands of individual messages" and points to the
per-release System Message Guide as the authoritative list rather than
enumerating them, so there's no per-subtype confidence rating, product
split, format axis, or example line the way FortiGate's/FortiManager's/
Juniper's/Zscaler's each have. What the source has instead is a
logging-configuration reference: 18 common facilities, 6 logging
destinations, 10 key configuration commands, and 5 advanced features —
four named-thing lists that stand in for the Log Types table's usual
per-subtype rows rather than being log types themselves (39 rows total,
searchable and filterable across those four types exactly like every
other vendor's real rows). Its 6 message-format fields common to every
syslog line (`FACILITY`, `SEVERITY`, `MNEMONIC`, and so on) fold into
the same table as their own "Common fields" rows, the same pattern
FortiGate's, FortiManager's, and Juniper's common fields already
established, bringing the rail's "All types" total to 45. Everything
that doesn't belong repeated per row — three message-format templates,
an 8-level severity table, a 6-key default-behavior summary, source
citations kept as plain text like Infoblox's — lives in the Reference
view instead, and because none of the four named-thing lists carry a
field list of their own, its Schema Explorer mode is a single
explanatory note, joining FortiManager's, Juniper's, and Infoblox's as
the fourth vendor for whom that's the honest answer rather than an
invented one.

A seventh vendor, Cisco Catalyst SD-WAN, brought the most raw material
of any vendor so far but the least single catalog shape — no confidence
rating, product split, or format axis runs through all of it the way
one axis runs through each of the other six vendors' own rows.
Instead of one row shape, its Log Types table holds three genuinely
different ones: 7 local log files (path + description), 8 software
modules (`CFGMGR`, `OMP`, `FTMD`, and so on, each with its own
description and priority), and 32 syslog messages — the modules' own
enumerated `sample_messages`, each with a message number, an optional
positional format template, a description, and an action code (47 rows
total). A module's own row opens to a modal listing all of its own
sample messages in one table, the same "material specific to this row
lives in its modal" principle Zscaler's sourcetype-matched CIM tables
already established, while each message stays independently searchable
as its own row too.

Two severity scales exist side by side in this source and stay two
separate Reference tables rather than being merged into one: syslog's
own 8-level scale, and a separate 4-level scale (Critical/Major/Medium/
Minor) that alarms and events use instead. `common_alarm_event_fields`
(13 fields) and `audit_logs.common_fields` (9 fields) are each common
only to their own narrow category — every alarm/event, every audit
entry — not to the 47-row Log Types table the way FortiGate's/
FortiManager's/Juniper's common fields are common to every one of
their own rows, so — following the same reasoning Infoblox's own field
schemas already established — they stay Reference-only tables instead
of becoming an invented "Common fields" rail chip with no real per-row
home. That same reasoning means Schema Explorer here is a single
explanatory note, joining FortiManager's/Juniper's/Infoblox's/Cisco IOS
XE's as the fifth vendor for whom that's the honest answer: the
source's only field-shaped data already lives in Reference, tied to a
category, not to individual Log Type rows, and the syslog messages' own
`format` strings are positional templates, not named fields.

(Found while checking the AWS Events table's text color against the other
tables on the page, and fixed with a one-line change: `index.html` never
had a `<!DOCTYPE html>` — none of the three source apps carried one into
the merge (two had none in the first place; Threat-detection-library's
was dropped since only its `<body>`/`<style>` content is extracted), so
the whole page was rendering in the browser's legacy Quirks Mode rather
than Standards Mode. Quirks Mode carries an old, still-replicated
behavior where `<table>`/`<tr>`/`<td>` don't inherit `color` from
ancestors outside the table, falling back to whatever `<body>` has
instead — which, since every embedded app's tables never set `color`
explicitly (relying on ordinary inheritance from their own `--ink`
token), silently pulled *every* table's text on the page to the shell's
own dark title color regardless of which app or theme it was in. This
wasn't new to AWS Events: Windows's own schema-explorer and pivot-explorer
tables had the exact same bug, just less obvious against their own
color choices. Adding the doctype puts the page in Standards Mode, which
fixes ordinary inheritance for every table at once.)

Windows's own **Cloud Actions Explorer** sub-tab (next to its Cloud logs
tab — 5,148 operations across six Microsoft cloud audit/log schemas
(Microsoft Entra ID, Azure resource logs, the Azure Activity Log,
Microsoft Intune, Microsoft Purview's unified audit log, and Azure
DevOps), mapped to their category, resource provider, and resource type)
is a good example of why the id/CSS-scoping and
container-scoped-query machinery above earns its keep even *inside* a
single app: it reuses Schema explorer's own table/modal CSS classes for a
consistent look, and that reuse surfaced a real bug in Schema explorer's
own code (a `table.se-table th[data-sort]` click-sort selector with no
`#panel-schema` scoping, harmless until a second such table existed on
the page) — fixed upstream in Winevent-catalogue, not patched around
here.

Cloud Actions Explorer also carries Schema explorer's Search/Explore view
toggle, same reuse: Search is the sortable/filterable table; Explore
groups rows into collapsible cards by `(service, category)` — the one
grouping every row can join, since `resource_type`/`provider` are `N/A`
for four of the six services — each card showing its operations as
clickable chips (falling back to `resource_type`, then `provider`, then
the category name itself) that open the same detail modal a table row
does. The search box and Service filter apply to whichever view is
active, and switching between the two toggles doesn't disturb the
other's — Schema explorer's own Explore view still renders its 892 cards
untouched.

Every app's script, and the merged file as a whole, was verified with
`node --check` and exercised end-to-end in headless Chromium (search,
filters, detail views, reference tables, combo boxes, the auditd/
fapolicyd subpanels, the Windows schema-explorer field modal, the Windows
Cloud Actions Explorer's own search/service-filter/sort/detail-modal and
Search/Explore toggle (independent of Schema explorer's), cross-link jump
buttons, dark-mode theming, the Threat Detection Heat Coverage matrix and
Validations tab, the AWS Events Action Explorer's own
search/service-filter/sort/detail-modal plus its CloudTrail and ACSC
filter groups (Mapped/Not mapped and Recommended/Not recommended each
narrowing to their exact stat-tile counts — 5,254 and 38 respectively —
and combining correctly with the Service filter and search box), the
Other Events vendor picker
switching cleanly between FortiGate's 40 rows and FortiManager's 37 (each
with its own type-rail filter, Log Types/Reference toggle, and detail
modal rendering correctly — severity levels/common fields/sources for
FortiGate, the log-ID-format explainer/common fields/sources for
FortiManager), each vendor's `Common fields` rail filter surfacing its
own field rows in the same Log Types table (26 for FortiGate, 12 for
FortiManager) with dashes in place of a fabricated confidence/product
badge and a working lightweight modal, the stats tiles staying accurate
to real subtype counts (not inflated by the field rows now mixed into
`All types`), cross-catalogue search finding and opening an AWS action,
a FortiGate log type (jumping to the FortiGate vendor panel), a
FortiAnalyzer-only log type (jumping to the FortiManager vendor panel),
and a FortiGate common field by name (jumping to the FortiGate vendor
panel and its field modal), and repeated tab-switching in every
direction) to confirm none of the five apps — or, here, none of two
sub-tabs *within* the same app, nor the two vendor panels within Other
Events — leaks into or interferes with the others.

## Structure

- `index.html` — the merged lookup page described above.
- `windows/` — `Winevent-catalogue`'s data and docs, unchanged:
  `data/events.csv`/`.json`, `data/cloud_logs.csv`/`.json`,
  `data/cloud_actions.csv`/`.json`, `data/reference/*`, `docs/*`, and its
  own `README.md` (the full field reference for every column). Also
  holds four files kept only here, not mirrored from Winevent-catalogue:
  `data/MicrosoftCloud_Schema.xlsx`/`.json` (a spreadsheet- and
  JSON-native export of the same Cloud Actions Explorer schema, enriched
  with Azure Resource Manager resource-type metadata — API versions,
  supported capabilities like private endpoints/managed identity/tags/
  locking — joined from `data/azureresourcetypes.json`, an ARM
  resource-type catalog snapshot; the JSON nests that enrichment under an
  `arm` key, present only on matched rows, with `api_versions` as a real
  array and the `supports_*` fields as real booleans rather than the
  xlsx's plain strings) and `data/azureresourcetypes.json`/`.csv`
  themselves, kept for provenance (the join reads the JSON — its
  `providerDisplayName`/`locationsCount` fields are properly typed,
  `null`/number, rather than the CSV's empty-string/numeric-string
  encoding of the same data; the CSV stays for anyone who wants a
  spreadsheet-native copy). `tools/enrich_microsoft_schema.py` reapplies the join
  to the xlsx and `tools/export_schema_json.py` regenerates the JSON from
  it — both idempotent, safe to re-run after either input changes. The
  JSON also carries a handful of optional keys straight from the xlsx's
  own columns, generically list-driven (`OPTIONAL_COLUMNS` in
  `export_schema_json.py`) so a future column needs no code change: `api`,
  present only on the 795 purview rows sourced from Microsoft's raw
  Office 365 Management Activity API schema reference (value `"Office
  365 Management Activity"`) rather than the rest of purview's
  workload-research documentation; and `friendly_name`/`description`
  (always present together), a human-readable name and plain-English
  sentence for the operation, on the 1,340 purview rows whose source
  publishes them — same "absent unless present in the source, nothing
  invented" convention as `arm`.

  This enrichment isn't just a standalone data file anymore — Cloud
  Actions Explorer's own detail view shows it directly (provider/
  resource-type display names, API versions, region count, the four
  `supports_*` capability flags, a "Source API" row when `api` is
  present, "Friendly name"/"Description" rows when those are present,
  and a same-resource-type "other operations here" cross-reference
  computed from the tab's own already-embedded data) on whichever row
  you open, one more reason to keep this file and the page's embedded
  copy in sync. That embedded copy used to be Winevent-catalogue's own
  `index.html`'s `DATA.cloud_actions` (copied over each time
  Winevent-catalogue regenerated it the normal way) — Winevent-catalogue
  is no longer updated from this repo's work, so as of this data's most
  recent expansion the two repos' Cloud Actions Explorer data have
  diverged: this repo's own merged `index.html` embeds
  `MicrosoftCloud_Schema.json` directly, and Winevent-catalogue's own
  copy stays wherever it was last left.

  The link runs the other way too: `tools/roll_schema_into_arm_types.py`
  rolls `MicrosoftCloud_Schema.json` back into `azureresourcetypes.json`,
  adding a `schemaOperations` array to every ARM resource type that has
  one or more matching schema rows (192 of the 12,233 resource types do
  — the same 205 provider/type combinations the forward join matches,
  minus 13 whose resource type isn't itself a row in the ARM catalog).
  Each entry is trimmed to `{service, category, operation, source}`
  (provider/resource type are dropped — they're already that row's own
  `resourceType`). So `MicrosoftCloud_Schema.json` answers "what ARM
  metadata does this schema operation's resource type have," and this
  script makes `azureresourcetypes.json` able to answer the reverse,
  "what schema operations exist for this resource type" — both derived
  from the same two source files, kept in sync by re-running the
  relevant script rather than hand-edited. Only the JSON carries this;
  `azureresourcetypes.csv` stays the plain, unenriched flat catalog,
  since CSV has no natural way to nest a list per row.
- `linux/` — `linuxevent-catalogue`'s data and docs, unchanged:
  `data/events.csv`/`.json`, `data/reference/*`, `docs/*`, and its own
  `README.md`.
- `threat-detection/` — `Threat-detection-library`'s data, docs, schema,
  and build tooling, unchanged: `data/*.json` (the fourteen detection
  catalogues plus the MITRE technique files the Heat Coverage tab fetches
  at runtime), `docs/*`, `schema/*.schema.json`, `tools/*.py`, and its own
  `README.md`, `CHANGELOG.md`, `VERSION`.
- `Events_Other/` — raw reference data that doesn't belong to any of the
  three merged catalogues above; not read directly by `index.html` (it
  feeds `aws/` below instead — see its own `README.md`).
- `aws/` — data and build tooling for the AWS Events tab: `data/aws_iam_actions.json`
  (fetched by `index.html` at runtime, generated from `Events_Other`'s
  CSV) and `tools/build_aws_json.py` (regenerates it). See its own
  `README.md`.
- `other/` — data for the Other Events tab, one file per vendor, each
  fetched by `index.html` at runtime and kept exactly as compiled rather
  than reshaped (see its own `README.md`): `data/fortigate_log_reference.json`
  (from FortiOS's own documentation),
  `data/fortimanager_log_schema.json` (from the FortiManager/FortiAnalyzer
  7.6.2 documentation — the two products share one Log Message Reference
  guide), `data/juniper_switch_log_schema.json` (from Junos OS's
  System Logging documentation and System Log Messages Reference),
  `data/infoblox_log_reference.json` (compiled from data supplied
  directly by the repository maintainer rather than a published guide —
  see the file's own `source_documentation.note`), and
  `data/zscaler_splunk_onboarding_reference.json` (compiled by reading
  the real Zscaler Technical Add-on for Splunk package — Splunkbase app
  3865, `TA-Zscaler_CIM` v4.1.5 — directly, per the file's own
  provenance notes), `data/cisco_ios_xe_logging_reference.json`
  (a logging-configuration reference — facilities, destinations,
  commands, features, message format — rather than a log-type catalog,
  covering Catalyst switches, ASR/ISR routers, and IOS XE Catalyst
  SD-WAN devices), and `data/cisco_sdwan_logging_reference.json` (a
  comprehensive Cisco Catalyst SD-WAN logging reference — local log
  files, syslog formats, two severity scales, per-module syslog
  messages, alarms/events, audit logs — rather than a single log-type
  catalog). No
  build tooling here, unlike `aws/`: all seven JSON files are used
  as delivered, not derived from another file in this repo.

These directories are kept for anyone who wants the raw data (e.g. to load
into Splunk, or to extend a catalogue — see each source repo's README for
how). `index.html` doesn't read from `windows/` or `linux/` at runtime
(each of those apps' data is already embedded in the page); it does read
from `threat-detection/data/` for the Heat Coverage fetches, from
`aws/data/` for the AWS Events tab, and from `other/data/` for the Other
Events tab, all described above.

## Source repos

- [`Winevent-catalogue`](https://github.com/adamliq/Winevent-catalogue)
- [`linuxevent-catalogue`](https://github.com/adamliq/linuxevent-catalogue)
- [`Threat-detection-library`](https://github.com/adamliq/Threat-detection-library)

AWS Events and Other Events have no separate source repo — both are
maintained directly in this one (see `Events_Other/`/`aws/` and `other/`
above, respectively).

To extend Microsoft Events, Linux Events, or Threat Detection, edit the
source repo the normal way, then regenerate this repo's `index.html` from
its updated `index.html` export. To extend AWS Events, update
`Events_Other/aws_iam_actions_expanded.csv`, run
`python3 aws/tools/build_aws_json.py`, then regenerate `index.html` the
same way. To extend Other Events for an existing vendor, update that
vendor's own file in place (`other/data/fortigate_log_reference.json`,
`other/data/fortimanager_log_schema.json`,
`other/data/juniper_switch_log_schema.json`,
`other/data/infoblox_log_reference.json`,
`other/data/zscaler_splunk_onboarding_reference.json`,
`other/data/cisco_ios_xe_logging_reference.json`, or
`other/data/cisco_sdwan_logging_reference.json`), then regenerate
`index.html`. Adding a genuinely new vendor follows the pattern
FortiManager, Juniper EX-series, DDI Infoblox, Zscaler, Cisco IOS XE,
and Cisco SD-WAN each set inside `build_app_other()` (not a
separate top-level function — all of Other Events' vendors share one
`#app-other` container): a new data file, a new pill in the vendor-tab
row, a new sibling `<div>` panel (own stats/rail/table/modal markup,
plus a mode-toggle and Reference view only once the vendor's own source
material actually has material to put there — DDI Infoblox's first pass
didn't and skipped both, then gained them in a follow-up once its
`field_schemas` key arrived — reusing the shared `other-*` CSS classes
either way), and that vendor's own flatten/render/modal JS — written for
its own data's shape rather than forced through an existing vendor's —
registered in the `vendorPanels` map and merged into
`window.__compHub['other']` the same way. See `other/`'s own README for
why that part isn't generic across vendors.
