# Cat Scan

*(Previously "Event Catalogue Compendium" / `catalogue-compendium` — moved
here.)*

The mark next to the name — a paw print behind a magnifying glass — is the
"Paw + Magnifier" concept from a five-direction logo exploration, picked
to run with. It appears twice: inline (themed, next to the wordmark in the
menu bar) and as the browser-tab favicon (fixed colors, since favicons
can't reference the page's own light/dark tokens).

A small tag sits next to the wordmark in the menu bar, reading the
current [`VERSION`](VERSION) (`v1.5.10` as of this line) — this
merge's own version, distinct from any individual source repo's (the
vendored `threat-detection/` source already has its own `VERSION`/
`CHANGELOG.md`, tracking that upstream project independently). Cat Scan
had never been versioned before `1.0.0`; [`VERSION`](VERSION) is the
single source of truth (mirroring `threat-detection/`'s own convention)
and the menu bar tag is kept in sync with it by hand on every merge to
`main`, since this repo has no build step to stamp it automatically.
**Every PR that merges bumps it** — not just ones that feel significant
enough to warrant one, and not on every commit within a branch (a PR
that picks up review-comment fixups before merging isn't three bumps,
it's one, applied when it lands) — using Semantic Versioning
(`MAJOR.MINOR.PATCH`), same thresholds as `threat-detection/`'s own
scheme, held to deliberately: MAJOR for a breaking change to an id/
schema/URL scheme something external could depend on, MINOR for a
whole new catalogue, tab, or app-level capability, PATCH for
everything else — which is most merges, including fixes, data
corrections, documentation-only updates, this versioning policy note
itself, and incremental additions to a page that already exists
(a new filter, toggle, search refinement, or sort option on an
existing Events page, say). PATCH is the default; a merge only earns
MINOR or MAJOR when it clearly clears that higher bar, per ordinary
semver (a MINOR bump resets PATCH to 0; a MAJOR bump resets both to
0). No separate top-level
changelog file — this README's own chronological narrative already
serves that role in far more detail than a changelog would.

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
39-row logging-configuration reference, Cisco Catalyst SD-WAN's
47-row logging reference, and Dell iDRAC's 44-row alert-category/
message-ID-prefix reference (see
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
`cisco_ios_xe_logging_reference.json`, `cisco_sdwan_logging_reference.json`,
and `idrac_syslog_schema.json`
(from `other/data/`, see below — a modest ~46&nbsp;KB, ~10&nbsp;KB,
~9&nbsp;KB, ~32&nbsp;KB, ~97&nbsp;KB, ~9&nbsp;KB, ~21&nbsp;KB, and
~16&nbsp;KB respectively, but all eight fetched rather
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
`other/data/cisco_ios_xe_logging_reference.json`,
`other/data/cisco_sdwan_logging_reference.json`, and
`other/data/idrac_syslog_schema.json` (see Structure) —
and only builds that vendor's stats tiles, rail list, and search table —
and registers its rows on the shared `window.__compHub['other']` entry
for the shell Search pill — once its own fetch resolves; each vendor
panel shows its own loading message (and, under `file://`, an
explanatory error) until then, the same pattern Threat Detection's own
Heat Coverage tab already used for its runtime fetches. The eight
vendors load and register independently, so a search fired before all
eight resolve just won't have the still-loading ones' results yet.

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
`Juniper EX-series`, `DDI Infoblox`, `Zscaler`, `Cisco IOS XE`,
`Cisco SD-WAN`, and `Dell iDRAC` — see below), each
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
home. Schema Explorer here still gets those same 22 fields, though: a
real flat, searchable table exactly like FortiGate's/Zscaler's own, just
without a per-row modal to jump back to, since neither category has one
— clicking a field instead jumps to and expands the Reference section
it's already fully documented in (Alarms & events or Audit logs).

Infoblox's own Schema Explorer got the same treatment in the same pass,
for the same reason: its 106 field-schema fields (21 DNS query/response
+ 18 DHCP lease + 67 across the three Universal DDI Parquet
sub-schemas) were already real, named field data sitting in the
Field Schemas view, just never flattened into Schema Explorer's own
searchable table the way FortiGate's/Zscaler's per-row fields are —
the empty note it carried undersold what the source actually has.
Populated the same way: a real table, clicking a field jumps to and
expands the DNS query/response fields, DHCP lease fields, or Universal
DDI exported log files section it's already fully documented in.

That leaves three genuinely different Schema Explorer patterns rather
than two: FortiGate/Zscaler jump to a Log Type row's modal; Cisco
Catalyst SD-WAN and Infoblox jump to a Reference section instead, since
their field data is real but category-common rather than per-row; and
FortiManager/Juniper/Cisco IOS XE get a single explanatory note,
because their sources genuinely have nothing further to flatten —
Cisco IOS XE's own message-format fields are already Log Types rows,
FortiManager's/Juniper's common fields are too, and none of the three
enumerates anything below that.

An eighth vendor, Dell iDRAC (compiled from a syslog schema covering
iDRAC8/9/10 rather than fetched from one published guide, with the
source's own caveat that unverified items are reasonable inferences,
not confirmed line-for-line), has no enumerated per-message catalog
either — only category and prefix names — so its Log Types table holds
two named-thing lists instead of one row shape: 6 alert categories
(each carrying the source's own `verified` flag, reusing the exact
verified/typical badge colors FortiGate's confidence rating already
established) and 38 message ID prefixes (44 rows total). Its real
field data lives one level up, at the envelope and registry level: the
RACLOG full record envelope's own 9 fields, the iSM OS log envelope's
own 10, and the Redfish message registry's own 8 meta-fields — 27
fields that don't belong to any of the 44 rows individually, so Dell
iDRAC joins Cisco Catalyst SD-WAN and Infoblox in the "jump to a
Reference section" Schema Explorer pattern rather than starting a
fourth: three vendors now, not two.

At eight vendors the picker itself needed attention: the pill row was
already wrapping to two lines on narrower screens, the failure mode
the very first vendor picker was built to avoid back when it was still
a single always-active FortiGate pill. Rather than replace the pills
with a dropdown — which would hide how many vendors exist behind a
click — a search box now sits above the row and filters it: typing
narrows which pills show, Enter jumps to the first visible match,
Escape clears back to all eight. It reuses the same `other-search-box`
component every vendor's own toolbar already uses, and switching
vendors by any path (click, Enter, or a cross-catalogue search jump
via `otherOpenRef`) clears the filter first, so the newly active pill
is never left hidden by a stale search from a moment ago.

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

Cross-catalogue **Search**'s own result list got the same kind of attention
next: every Other Events vendor shared one purple `OTHER` badge, so a query
that spanned several of them (searching `user` currently returns 20 Other
Events rows across 7 of the 8 vendors) rendered as one visually
undifferentiated stack, and — unlike every per-vendor table's own search,
which already wraps matched substrings in `<mark>` via a shared
`highlight()` helper — universal search results were never highlighted at
all. Now, whenever a source's own current match set spans more than one
distinct vendor, results sub-group under a vendor sub-header (an
accent-colored label plus a count, one visual step below the existing
source `cs-group-label`) with the now-redundant per-row badge dropped, and
every title/meta cell goes through `highlight()` instead of plain escaping
— both flat and grouped rows alike. The vendor sub-header's label is read
live from the vendor's own picker pill (`.other-vendor-tab[data-vendor=...]`)
rather than a second hardcoded name map, so a ninth vendor picks up correct
sub-grouping with no changes here. Sources that never split by vendor
(Microsoft Events, AWS Events, Linux Events, Threat Detection) render
exactly as before, just now highlighted; an Other Events match set that
happens to land on a single vendor (e.g. searching `bios`, which matches
only Dell iDRAC) still renders flat with its `OTHER` badge, unchanged.
Verified against real data across `user` (7 vendors), `config` (7
vendors), `audit` (3 vendors), and `certificate` (3 vendors) — each
sub-header's count matching the vendor's true share of that query's Other
Events matches — plus the `bios` single-vendor case, click-through from a
grouped row still switching tabs and opening the right detail, and both
themes at 1500px and 375px with zero console errors.

That vendor grouping immediately surfaced two real bugs in the cap/order
logic underneath it, both invisible in the old flat design. First: Other
Events matches were scanned with the same 40-row `PER_SOURCE_CAP` every
source uses, applied *before* grouping — so a broad query could fill the
entire cap from whichever vendors happened to sit first in
`hub.other.items` and silently omit the rest. Searching `log` has 185 real
matches spread across all 8 vendors (Infoblox 75, Cisco SD-WAN 30,
FortiGate 25, Cisco IOS XE 19, Zscaler 16, FortiManager 13, Juniper 4, Dell
iDRAC 3), but the old cap only ever reached FortiGate/FortiManager/Juniper
— Infoblox's 75 matches, the largest group by far, never appeared at all.
Second: `hub.other.items` is built by each vendor's own async `fetch()`
appending its rows on resolve, so their relative order — and therefore
which vendor sub-header showed first — depended on network timing; the
same query re-run five times shuffled FortiGate/FortiManager/Zscaler's
position in the list.

Both are fixed in `runSearch`/`renderMatches`, scoped to the `other`
source only (the other four sources never carry a `vendor` field, so
neither bug can occur there, and their scan keeps the original early-exit
cap for performance — Other Events is ~400 items total, cheap to scan in
full on every keystroke, but AWS Events alone is 20k+). Other Events is
now scanned without a cap so every real match is known, `renderMatches`
sorts vendor sub-groups by descending match count (alphabetical by label
as a tiebreak) so the same query renders identically on every load, and
each vendor gets a fair share of the display budget (`Math.max(5,
Math.ceil(40 / vendor count))` rows) instead of the first vendors
exhausting it — with an honest `+N more — narrow your search to see them`
note (reusing the exact "Showing the first N of M matches" idiom already
used by every vendor's own table) wherever a vendor has more real matches
than its shown share.

Verified: `node --check` on the modified block; `log` now shows all 8
vendors with correct real counts and matching "+N more" notes (Infoblox
75 shown 5 +70 more, down to Dell iDRAC's 3 shown with no note); `user`
re-run five times produces byte-identical vendor ordering; `config`/
`audit`/`certificate` re-verified against their real per-vendor counts
under the new sort; the `bios` single-vendor fallback, non-vendor sources
(`logon` on Microsoft Events, still capped at 40 with no note, unchanged),
and click-through from a grouped row to the right tab/detail all still
work; zero console errors across both themes.

Universal search's filter row also picked up a third chip group: **Other
Events vendor**, one toggle per vendor (FortiGate, FortiManager, Juniper
EX-series, DDI Infoblox, Zscaler, Cisco IOS XE, Cisco SD-WAN, Dell iDRAC),
on by default, next to the existing Sources and Threat Detection type
groups. It reuses the exact chip/`data-filter-type`/`data-filter-value`
pattern the other two groups already use — one generic click handler
dispatches through a `{source, kind, vendor}` store lookup, no new event
wiring — and combines with them the same way Sources and Threat Detection
type already do: as an independent intersection, filtering every source
that carries the field it targets (here, `it.vendor`, which only Other
Events items ever have) and leaving every other source's own results
completely untouched. Turning a vendor off removes it entirely from the
scan, so a now-single-vendor match set correctly falls back to the flat
badged rendering, and turning every vendor off just leaves Other Events
with nothing to show (the other four sources, unaffected, still render
normally) rather than needing a special-cased empty state.

Verified: `node --check` on the modified block; all 8 vendor chips render
active by default; disabling FortiGate and Cisco IOS XE on a `log` query
removes exactly those two vendor groups from the results (6 remain) and
re-enabling them restores all 8; toggling any vendor chip leaves Microsoft
Events results (`logon`, still 40 rows) completely unchanged; disabling
every vendor chip and searching `bios` (previously Dell iDRAC only) shows
zero Other Events rows while Microsoft Events results still render
normally; the chip row wraps cleanly at 375px; zero console errors, both
themes.

Threat Detection's own validations were still one more layer down in
universal search than everywhere else: both detections and validations
lived in a single `td` compHub source, so search results showed one
`THREAT DETECTION` group with both kinds inside it (a "TV" badge on
validation rows was the only visual cue), rather than sitting alongside
Microsoft Events/AWS Events/Linux Events/Other Events as their own thing.
Split `td` into two independent top-level compHub sources - `td`
(detections) and a new `tv` (validations, label "Threat Validations") -
each with its own `open()` (detections switch to the Detections sub-view,
validations to the Validations sub-view; both still live in the one
Threat Detection panel, so a `tv` row's click handling now maps to that
same physical tab via a small `TAB_TARGET` lookup rather than searching
for a `tv` tab that doesn't exist). `tv` got its own Sources filter chip
and its own `cs-group-label`/`cs-badge-tv` (sharing the `td` badge's color
token, since they're still visually one family, just no longer nested).
This made the old "Threat Detection type" filter chip group (detection/
validation, via a separate `kindFilter`) entirely redundant - the Sources
chips now already draw that line - so it, `kindFilter`, and every `kind`
field/check that only existed to support it were removed outright rather
than left as dead weight. Picked up two more accuracy fixes already
sitting in the same code: the "no sources selected" check was hand-listing
every source key (already once out of sync, missing nothing today but a
repeat of exactly the bug fair-capping fixed elsewhere) - now reads
`order` directly, so a future source can't be forgotten there again - and
the intro/empty-state copy ("three catalogues") had been stale since AWS
Events and Threat Detection were added; reworded count-agnostically so it
can't go stale again.

Verified: `node --check` on both the Threat Detection app's script block
and the search shell's. Six Sources chips render (Threat Detection and
Threat Validations both present, no leftover kind chips). Searching `log`
produces six separate group labels, `THREAT DETECTION` and
`THREAT VALIDATIONS` among them, each with correctly colored/labeled `TD`/
`TV` badges. Toggling the Threat Validations chip off removes only that
group (Threat Detection's own group stays); re-enabling restores it.
Clicking a `tv` row switches to the Threat Detection tab's Validations
sub-view; clicking a `td` row switches to its Detections sub-view. Turning
off every Sources chip shows the existing "No sources selected" message.
Other Events vendor grouping/fairness and the vendor filter are
unaffected. Confirmed at 375px and in both themes with zero console
errors.

Universal search also gained a results **summary**: a small card right
above the per-source groups, showing the total match count and a
color-coded chip per source (reusing each source's own `cs-badge` from the
rows below it) with its real count - "2,830 matches · WIN Microsoft
Events 524 · AWS AWS Events 627 · ..." - so the overall shape of a broad
query is visible without scrolling through every group first. Getting
real (not capped) counts required a change one level down: every source
except Other Events was scanned with an early-exit `PER_SOURCE_CAP` (40)
during collection - fine for capping what's *rendered*, but it meant the
scan itself never learned the true total once a source hit the cap, so a
summary built from `matches.length` would have quietly underreported
every source except Other Events (which #31 had already fixed to scan in
full). Benchmarked full, uncapped scans directly in the browser first
rather than assuming: even AWS Events' 21,164 items scan in under a
millisecond, so the early-exit was removed everywhere - the existing
`PER_SOURCE_CAP` now applies only to what's rendered (via renderMatches'
already-existing slice-plus-"+N more" logic, previously exercised only by
Other Events), not to what's counted or known. That's a second, incidental
fix: Microsoft Events/AWS Events/Threat Detection results past the 40-row
cap were previously cut off with no indication anything was hidden;
they now get the same honest `+N more — narrow your search to see them`
note Other Events already had.

Verified: `node --check` on the modified block. Summary counts for `log`
cross-checked directly against `window.__compHub` (524/627/22/1409/63/185
for Microsoft/AWS/Linux/Threat Detection/Threat Validations/Other Events,
summing to the displayed 2,830) - exact match. Toggling a Sources chip or
an Other Events vendor chip updates both the summary and its total
correctly. A query with zero matches shows no summary card, just the
existing "No matches." message. `+N more` notes now appear for every
capped source, not just Other Events. Click-through from a row still
works with the summary card now sitting above it. Confirmed at 375px and
in both themes with zero console errors.

**Microsoft Events** then gained a new data source: ASD's ACSC, jointly with
CISA, NSA, CCCS, NCSC-NZ and NCSC-UK, "Detecting and mitigating Active
Directory compromises" (September 2026), Appendix B (Tables 18-23) - the
guidance's own event-ID-to-compromise-technique mapping (DCSync,
Kerberoasting, Golden Ticket, Skeleton Key, AS-REP Roasting, Password
Spray, MachineAccountQuota, Unconstrained Delegation, Silver Ticket,
Dumping ntds.dit, SID History, One-way Trust Bypass, AD CS, Golden
Certificate, Golden SAML, Microsoft Entra Connect - Shadow Credentials and
the DCSync/event-5712-correlation note are both real per that guidance but
explicitly *not* listed in the Compromise column of their own row, so
they're carried as a citation caveat rather than added to the technique
list itself). 48 distinct event IDs, mapped against the existing 4,737-event
catalogue one row at a time rather than by number alone, since Windows
event IDs are only unique per log/provider, not globally - 39/40/41
collide with an unrelated Application-log Certificate Services event under
the same numbers, so trusting the ID alone would have silently mislabeled
the wrong row. 45 rows across 39 distinct events matched a real existing
catalogue entry (verified event-by-event against Microsoft's own
documentation of each channel, not assumed from ACSC's table alone,
including a live check of where events 39/40/41 actually log to -
Applications and Services Logs > Microsoft > Windows >
Kerberos-Key-Distribution-Center, not the Application-log false match) and
got two additions: a new `ad_compromise_techniques` field (semicolon-
joined technique names, same convention as the existing `mitre_techniques`
field) and the new citation appended to `reference` (joined onto whatever
citation, if any, was already there - e.g. the existing ASD/ACSC "Priority
logs for SIEM ingestion" citation many of these rows already carried -
never overwritten). The remaining 9 event IDs had no real existing match
(39/40/41 under Kerberos-Key-Distribution-Center; 307 under AD FS/Admin,
confirmed against 510's own description, which already references it;
611/650/651/656/657 for Microsoft Entra Connect password-hash sync,
confirmed against Microsoft's own troubleshooting docs as Application-log
"Directory Synchronization" events) and became 9 new catalogue entries,
following the exact existing schema and the same "illustrative example"
`sample_type` and generic header-only `field_schema` convention already
used for entries without a captured real sample.

The new field surfaces the same way `mitre_techniques`/`acsc_priority_log`
already do: an "AD COMPROMISE" badge (reusing the existing ACSC-accent
badge style) on both the row list and the detail view, a new "AD
compromise techniques" row in the detail view's field grid, and inclusion
in both the app's own internal search (`matches()`) and the compHub `text`
index universal search reads - so searching "DCSync" or "Kerberoasting"
from either Microsoft Events' own search box or the cross-catalogue Search
tab finds these rows.

The merge itself was done as a surgical text splice, not a full
re-serialization: Microsoft Events' entire dataset lives as a single
~9.8MB `const DATA = {...};` line (one of the largest single lines in the
file), inconsistently mixing literal-UTF-8 and `\uXXXX`-escaped characters
throughout (evidence of having been edited by different tools over time) -
re-serializing the whole structure with any one JSON encoder would have
normalized that escaping everywhere and produced a multi-megabyte diff
touching nearly every event, not just the ones this change actually
touches. Instead, each of the 45 target rows was located by an anchor
built from its own `event_id`/`log`/`source`/`category`/`subcategory`
(verified unique before touching anything), and only its `reference` value
and a newly-inserted `ad_compromise_techniques` field were rewritten in
place - every other byte of every other event, including untouched fields
on the *same* rows, stayed byte-identical. The 9 new entries were appended
at the true end of the `events` array specifically (found via the exact
`],"audit_configuration":` boundary marking the next top-level key,
after an earlier version of this same merge mistakenly appended into
`cloud_actions` - the JSON's actual final array - since a naive
last-`]};` search doesn't know the DATA object has eighteen other
top-level keys after `events`, not just the one being edited).

Verified: `node --check` on the full extracted Microsoft Events script
block, both before and after the UI wiring changes. `git diff --stat`
confirms exactly one line changed in the whole file. Full round-trip
parse of the merged JSON confirms exactly 4,746 events (4,737 + 9), all
18 other top-level keys (`audit_configuration` through `cloud_actions`)
untouched in both key set and count, and all 54 tagged rows (45 enriched +
9 new) carrying the expected `ad_compromise_techniques` value. In the
running app: the stats tile reads 4,746 events; searching "Kerberoasting"
returns exactly the 3 expected rows (4738, 4769, 5136) each showing the
AD COMPROMISE badge and technique list; searching by the new
Kerberos-Key-Distribution-Center/Directory Synchronization/AD FS log
names finds the 9 new rows with fully-populated, non-empty detail views;
an unrelated pre-existing event (4205) correctly shows no AD COMPROMISE
badge; cross-catalogue Search finds and correctly opens both an enriched
row (4662) and confirms Threat Detection's own DCSync coverage is
unaffected; and every other tab (AWS Events, Linux Events, Threat
Detection, Other Events) still switches cleanly with zero console errors,
in both themes.

That citation then got its source URL added
(cyber.gov.au/business-government/detecting-responding-to-threats/
detecting-and-mitigating-active-directory-compromises) across the same 54
rows: a single literal-substring replace of the exact citation phrase
(`\"Detecting and mitigating Active Directory compromises\" (September
2026), Appendix B, `, escaped-quote form since it's a JSON string value
inside the raw file text) into the same phrase with the URL inserted right
after the edition date - counted at exactly 54 occurrences first (matching
the 54 tagged rows precisely, confirming no stray match elsewhere in the
file) before touching anything. This drive-by also fixed a footer line
("4,737 events indexed") that had gone stale the moment the AD-compromise
PR's 9 new events landed - a plain static count next to the header stats
tile's own live `events.length`, not sourced from it, so it silently drifted
the instant the dataset grew. Verified: `node --check`; `git diff --stat`
shows exactly 2 lines changed (the DATA line plus the footer); JSON
round-trip confirms all 54 rows now carry the URL and the event count is
still 4,746; the Related section renders the URL as plain readable text in
both an enriched row and a brand-new row, consistent with the one other
bare-URL `reference` already in the catalogue; footer now reads "4,746
events indexed"; zero console errors.

That same "Priority logs for SIEM ingestion" document (already the source
behind 212 existing `acsc_priority_log: Yes` entries, referenced without a
URL) got a real coverage check next: cross-referenced all 199 distinct
event IDs across its four requested tables - Microsoft Domain Controller
Log Types, Active Directory (AD) and Domain Service Security Logs,
Microsoft Windows endpoint logs, and Critical Azure service and app logs
(the "Entra & Entra Connect Servers" row, its only row with actual numeric
IDs rather than "All") - against the catalogue. All 199 were present,
including via spot-check of the highest-collision-risk generic IDs (`1`,
`21`-`25`, `118`/`119`/`129`/`200`, `400`, `5857`-`5861`, the `8000`-`8040`
AppLocker range) against their *specific* matching entries, not just bare
number membership - the same lesson event 39/40/41 taught earlier in this
same document's companion guidance. That check surfaced a real gap one
level down, though: of those 199 IDs, 8 had a correct catalogue match but
were never actually flagged `acsc_priority_log: Yes` - the 5 Entra Connect
entries added in the AD-compromise PR (left untagged at the time for lack
of a source confirming SIEM-priority status; this document is exactly
that source) plus two pre-existing entries, 4765/4766 (SID History account
add success/fail) and 4771 (Kerberos pre-authentication failure, which
already carried the AD-compromise citation from earlier and needed this
one appended alongside it, not in place of it).

Fixed the same way as the URL addition above - each of the 8 located by
its own event_id/log/source/category/subcategory anchor (all eight have
exactly one catalogue entry each, no duplicate-row disambiguation needed
this time), given `acsc_priority_log: "Yes"` and a citation naming the
specific table it appears in (not the generic multi-table phrase the
existing 212 entries share) with the new URL included from the start:
`ASD/ACSC "Priority logs for SIEM ingestion: Practitioner guidance"
(2025), <url>, <table name>`. Existing citations (four of the eight
already carried the AD-compromise citation) were extended with `; `, never
replaced.

Verified: `node --check`; `git diff --stat` shows exactly one line
changed; JSON round-trip confirms the event count is still 4,746 and all
eight rows carry both the new tag and the URL. In the running app: all
eight show the "ACSC priority log" badge and the new URL in their Related
section; the existing "ACSC priority logs only" filter toggle - unchanged
code, since it just reads the field - now correctly includes 4765 without
any code change; 611 and 4771's Related sections show both citations
chained, not one overwriting the other; zero console errors.

Cat Scan then got its own version, visible in the menu bar - see the
versioning note near the top of this README for the full convention
(`VERSION` as source of truth, semver thresholds matching
`threat-detection/`'s own, no separate changelog since this README's
narrative already is one). Starting point is `1.0.0`: not a
reconstruction of every change that happened before versioning existed
(everything from the original three-repo merge through this point stays
undated/unversioned in the narrative above, same as always), just where
tracking begins going forward.

Verified: `node --check` on the unaffected script blocks (this change
touches only static HTML/CSS - the `.compendium-title` markup and one new
`.version-tag` rule reusing the existing `--shell-tab-text` token, no new
colors). The tag renders next to the wordmark, survives switching between
every tab, wraps cleanly at 375px, and is legible in both themes with zero
console errors.

That first bump was also meant to be the last "when a change warrants
it" one - the policy is now every merge to `main` increments the
version, not just ones judged significant, and not once per commit
within a branch, only once when the PR actually lands. This one PR is
the explicit, one-time exception: the merge that documents the policy
stays at `1.0.0` rather than becoming its own first data point, at the
user's request. Every merge after this one follows the policy as
written above.

First real application of that policy: a **breadcrumb** and a **back to
top** button, both shared shell chrome living outside every `#app-*`
container so they persist across all six tabs untouched by the
tab-switching `show(key)` function's `display: none` toggling.

The breadcrumb (`Cat Scan / <current tab>`) sits as a thin strip
directly below the sticky menu bar - not itself sticky, so it scrolls
away with the page rather than permanently eating vertical space. Its
label is read live from the just-activated tab button's own text
inside `show(key)`, the same "derive from the DOM, don't hardcode a
second map" pattern the vendor-grouping and vendor-filter work already
established for Other Events - a renamed tab can't drift the
breadcrumb out of sync with it.

The back-to-top button is a single global floating circle (bottom
right, `position: fixed`), toggled by a `window.scroll` listener past
a 400px threshold and calling `window.scrollTo({top:0})` on click
(respecting `prefers-reduced-motion`). One button covers every tab
because the whole page scrolls at the document level - individual
widgets with their own internal scroll (the Windows Events list panel,
combo-box panels, reference tables) are untouched and keep their own
scroll position; only the outer page resets. That distinction matters
here more than it looks: Windows Events' own default view barely
scrolls past the viewport at all (its list scrolls internally,
capped at `68vh`), while Threat Detection's card grid lays out
directly in page flow with no such cap - selecting a rich Windows
event detail or browsing Threat Detection's cards are exactly the
cases this button earns its keep on, and both were used to verify it
rather than the (barely-scrolling) Windows Events default view alone.

Verified: extracted and `node --check`'d the modified tab-switching
and new back-to-top script blocks together. Breadcrumb text confirmed
correct across all six tabs in sequence (Microsoft Events -> AWS
Events -> Linux Events -> Threat Detection -> Other Events -> Search ->
back to Microsoft Events). Back-to-top confirmed hidden at rest,
appearing only past the scroll threshold (tested on Threat Detection,
whose card grid runs to ~300,000px tall unscrolled - the button was
invisible testing against Windows Events' own near-viewport-height
default view before this was caught), returning scroll position to 0
on click, and hiding again once there. Both confirmed at 375px and in
both themes with zero console errors.

`1.1.0` (MINOR - a new shell-level feature, not a fix or data
correction) per the versioning policy two paragraphs up.

Microsoft Events' own Events page got a fourth toggle filter next to
Log/Category/ACSC-priority-logs-only: **Has reference link**, narrowing
to the 128 events (of 4,746) whose `reference` field actually contains
an `http(s)` URL - as opposed to the 4,242 with citation-only text
("ASD/ACSC ... (2025), Table 18") or the 376 with no reference at all.
Mirrors the ACSC toggle's exact pattern (`.acsc-toggle` class reused
verbatim, same `let flag = false` / click-listener / active-filter-chip
/ clear-all shape), scoped to Microsoft Events' own Events page only -
Linux Events carries an identical, separately-coded copy of this same
filter machinery untouched.

A filter that surfaces "has a reference link" only earns its keep if
the link is actually clickable once you get there, so the detail
view's Related section - previously plain escaped text even for the
72 entries whose entire `reference` value already was a bare URL - now
runs through a new `linkifyReference()` helper: escape first, then
wrap any `https?://[^\s<,;]+` substring in a real `<a target="_blank"
rel="noopener noreferrer">` link, leaving surrounding citation text
(including a trailing comma or closing parenthesis immediately after
the URL, as most of these have) untouched. Verified against both
shapes: a bare-URL reference and a long citation with an embedded URL
followed immediately by `, Appendix B, Table 18 (...)` - the link
stopped exactly at the URL, the rest rendered as plain text either
side of it.

Checking "Clear all" surfaced a real, pre-existing bug unrelated to
this filter but directly in its path: the button's generated markup
used a bare `id="clear-all"`, while the click-handler looked up
`win-clear-all` - two different ids that never matched, so the
listener never attached and the button did nothing (silently; it
still turned the removed chip's own flag off via the same event
delegation, so the bug was easy to miss with fewer filters active).
Linux Events carries the exact same bug under its own `id="clear-all"`
/ `lnx-clear-all` mismatch, untouched here - out of scope for a
Microsoft-Events-page request, left as a known issue for a future
pass. Fixed Microsoft Events' own copy by renaming the generated id to
match what the lookup already expected.

Verified: `node --check` on the full extracted script block. Toggling
the filter narrows 4,746 -> 128 and back; the active-filter chip
removes the filter on click; "Clear all" now genuinely resets every
active filter (Log/Category/ACSC/reference-link) and un-highlights
every toggle button, confirmed by count returning to 4,746 and the
button's `on` class actually clearing, neither of which held before
the id fix. Confirmed at 375px and in both themes with zero console
errors; Linux Events (a separate, untouched copy of this same code)
still loads cleanly.

`1.2.0` (MINOR - a new filter is a feature, not just the incidental
bug fix riding alongside it).

A fifth toggle group followed immediately: filtering by *which* ACSC
publication a reference cites, not just whether it cites one at all.
`reference` is free text, not a structured field, so there's no source
of truth to enumerate known publications from the way `allLogs`/`cats`
are derived straight from the data a few lines up - `ACSC_PUBLICATIONS`
is a small, hand-maintained `{key: title}` map, currently the two ASD's
ACSC documents cited anywhere in the catalogue as of today ("Detecting
and mitigating Active Directory compromises" and "Priority logs for
SIEM ingestion: Practitioner guidance"). Scoped deliberately narrow,
per the request: a future citation to a third publication needs one
more map entry and one more toggle button, not a redesign.

Two toggle buttons, `.acsc-toggle` reused again, but with different
combination semantics than the other four filters on this page: a
`selectedPublications` `Set` gives OR-within-this-group matching
(selecting both toggles shows events citing *either* - 114, confirmed
against the real 54/80/20-overlap/114-union numbers computed straight
from the data before writing a line of UI) while still AND-ing against
Log/Category/ACSC-priority/Has-reference-link and the search box, the
same two-level combination `selectedLogs`/`selectedCats` already use
for their own multi-select. Active-filter chips, removal, and Clear
all all extended to match - reusing the exact same pattern each of the
prior three filters already added to this same function, not a parallel
implementation.

Verified: `node --check`. Toggling each publication alone gives 54 and
80 respectively (matching the AD-compromise and Priority-logs PRs'
own real counts exactly); both together gives 114, not 174 - confirming
OR-within-group rather than accidentally summing overlapping matches;
deselecting or removing either leaves the other's filter intact; the
20-event overlap (entries like 4771, tagged by both prior PRs) show
both toggles' effects simultaneously when narrowed to either one.
Active-filter chip removal and Clear all confirmed to un-toggle the
correct button and reset the Set. Confirmed at 375px (four toggle
buttons wrap to a second/third row cleanly) and in both themes with
zero console errors; every other tab still loads cleanly.

`1.3.0` (MINOR - another new filter).

Two more additions to the same Events page: an **exact-term** checkbox
next to the search box, and a fix to how results were ordered at all.

Neither of the earlier filters touched search matching itself - `q`
was always a plain substring test against nine fields, so searching
"log" matched "Logon" and "catalog" right alongside genuine word
matches, and searching a numeric id like "4624" matched inside an
unrelated id like "24624" too (both real ids in the catalogue - not a
hypothetical). The checkbox, off by default so today's behavior is
unchanged, switches `matches()` to a `\bterm\b` word-boundary regex
instead of `.includes()` when checked - built from the same
already-lowercased `q` and already-escaped via a small `escapeRegex()`
helper (special regex characters in a typed query would otherwise
throw or match wrong), with a defensive fallback to the old substring
behavior if regex construction somehow fails.

Separately: the results list had never actually been sorted - `render()`
displayed `filtered()`'s rows in whatever order the underlying `events`
array happened to hold them (source-file order, e.g. 4205, 4343, 70, 72,
73...), not by event id at all. `filtered()` now sorts numerically
ascending before returning (`parseInt(a.event_id) - parseInt(b.event_id)`,
verified every event_id in the dataset is a plain numeric string first,
so a numeric subtraction is safe - a string sort would have put "10"
before "2"). Sorting inside `filtered()` itself, not `render()`, so the
one caller gets pre-sorted rows with no separate step to remember.

Verified: `node --check`. Default (unfiltered) list now runs low to
high starting from id 0. Searching "log" substring-matches 525 events;
the same query with Exact term checked narrows to 39, all genuine
whole-word "log" matches (sample-checked - "Event Log was Cleared",
"...confusing log timelines...", none of the "Logon"/"catalog"-only
false positives the substring search pulled in). Searching "4624"
exact-term returns only id 4624; the same query unchecked also returns
24624, confirming the fix targets a real, present ambiguity rather than
a hypothetical one. Confirmed at 375px and in both themes with zero
console errors; every other tab unaffected.

`1.3.1` (PATCH - a search refinement and a display-order fix on the
existing Events page, not a new catalogue/tab/capability).

Asked to confirm whether a pasted list of 37 `Microsoft-Windows-WebAuth`
events (IDs 1000-1406, the `AuthHost` browser-control provider used by
ADAL/legacy-auth web popups - navigation start/complete/redirect/
terminate, security-manager UrlAction decisions, meta-tag handling)
were already in the catalogue. They weren't: the only close match was
`Microsoft-Windows-WebAuthN` (note the trailing N) - the unrelated
FIDO2/Windows Hello passkey provider, which happens to reuse the same
1000-2400 ID range and has 100 entries already catalogued, but whose
event text never mentions "AuthHost" and shares zero actual overlap
with the pasted list. Confirmed with a `source ==
'Microsoft-Windows-WebAuth'` (exact match, not substring - `WebAuthN`
would have satisfied a naive `.includes('WebAuth')` check) query
against the parsed `DATA.events` array: zero hits before this change.

Added all 37 as new entries, following the exact schema this catalogue
already uses for other low-profile providers sourced from the same
Windows Server 2019 (1809, build 17763.1457) ETW manifest export
(`Microsoft-Windows-OtpCredentialProviderEvt`, `Microsoft-Windows-
WlanConn`, `Microsoft-Windows-TPM-WMI`, etc.): `category` mirrors
`source` verbatim (`Microsoft-Windows-WebAuth`, matching the default
this catalogue uses whenever a provider hasn't been given a
human-readable category), `subcategory` is the manifest's own Task
Category text (`Navigation Start`, `Navigation Terminate`, `Security
Manager`, `Meta Tag`, etc.), `log` is `Microsoft-Windows-WebAuth/
Operational` (the Channel column), `description` is the manifest's
own message text kept verbatim with its `{Field}` placeholders
unresolved (matching how this catalogue treats every other
manifest-derived entry - no invented example values), `sample_type`
is `template`, and `reference` is the same "ETW manifest export"
citation the sibling entries already use. `mitre_techniques`,
`acsc_priority_log`, `nist_800_53_au`, `group_policy_path`,
`opposite_event_id` and `cim_mapping` are left blank, again matching
the sibling entries - AuthHost is a legacy, largely undocumented
component with no public MITRE/NIST/GPO mapping to cite honestly.

First attempt at the splice landed in the wrong place: this file's
Windows-events script IIFE declares `const DATA = {"events": [...],
"audit_configuration": [...], ..., "cloud_actions": [...]}` - seventeen
top-level keys, "events" first and "cloud_actions" last - and the
insertion script located the new entries' target position by matching
the literal text immediately preceding the DATA statement's closing
`]};`, which is the end of `cloud_actions` (a completely different
array of cloud-provider action mappings), not the end of `events`.
The insert was syntactically valid JSON either way, so `node --check`
and a first parse both passed silently; the bug only surfaced when a
`source === 'Microsoft-Windows-WebAuth'` query against `DATA.events`
still returned zero results after the edit. Re-targeted the splice to
the actual `],"audit_configuration":` boundary that closes the
`events` array specifically, then re-verified byte-for-byte that the
new final `events` entry (id 1406) sits immediately before that
boundary and that `cloud_actions` was back to its original length
(5,148, unchanged).

Verified: `node --check`. Parsed `DATA.events` grew from 4,746 to
4,783 (all 37 new ids present, no duplicates). The app's own header
stat line updated accordingly, to "4,783 events - 190 logs - 192
categories" (one new log, one new category, both `Microsoft-Windows-
WebAuth`). Searching "WebAuth" (substring) now returns 137 rows - the
pre-existing 100 WebAuthN plus the new 37 WebAuth, both sources
visibly distinguishable by badge. Searching "AuthHost" - text unique
to the new entries - returns 36 rows, not 37: event 1042's message is
"Navigation cancelled by user.", the one entry in the set that doesn't
happen to contain the word "AuthHost", confirming the count reflects
real content rather than a copy-paste artifact. The 36/37 sorted
ascending by id with no gaps or duplicates; opening the first result's
detail view (id 1000) rendered cleanly. Confirmed at 375px and in both
themes with zero console errors; every other tab, and the pre-existing
WebAuthN entries, unaffected.

`1.3.2` (PATCH - new data rows added to the existing Events page/
catalogue, same provider-addition category as prior data-only PRs;
not a new catalogue, tab, or app-level capability).

Asked to check two more pasted event lists. `Microsoft-Windows-WebAuthN`
(100 events, ids 1000-2402, the FIDO2/Windows Hello CTAP/NGC/hybrid
provider) turned out to already be fully catalogued - every id in the
pasted list matched an existing entry exactly, no gaps either
direction, confirmed with a straight set-difference between the pasted
ids and `DATA.events` filtered to that source. No change needed there.

`Microsoft-Windows-TerminalServices-ServerUSBDevices` (20 events - ids
2-9 largely lacking a resolved message template in the manifest, plus
ids 32-44 covering USB-redirection driver load, device install/
redirect/remove, and virtual-channel connect/disconnect) was genuinely
missing: zero matches for that source, exact or substring. Added all
20, using the manifest-import schema again, with two wrinkles this
provider's manifest export surfaces that the WebAuth batch didn't:

- Task Category is blank for every one of these 20 events (unlike
  WebAuth, where every row had one), so `subcategory` is left empty
  and the `sample` text omits the "Task Category:" line entirely -
  matching how `Microsoft-Windows-TPM-WMI` (another Task-less
  manifest-derived provider already in the catalogue) is represented,
  rather than always including the line as WebAuth's entries do.
- Eight of the twenty rows (ids 2, 3, 4, 5, 6, 7, 8, 9) carry the
  literal text `{message}` as their Message column value -
  the manifest's own generic placeholder for "no resolvable template",
  not a real field reference. Rendered those the same way this
  catalogue already renders a true template-less event elsewhere
  (`Microsoft-Windows-WlanConn`, `Microsoft-Windows-OtpCredentialProviderEvt`):
  `"(Event from Microsoft-Windows-TerminalServices-ServerUSBDevices;
  no message template provided by the manifest)"`, rather than
  literally storing the placeholder token `{message}` as if it were
  real event text.
- Channel varies per event this time (`Debug`, `Analytic`, `Admin`,
  `Operational`, instead of a single `Operational` channel for the
  whole batch), so `log` is built per-row as `source/Channel` rather
  than one fixed string.

Learned from the previous PR's splice-target bug and located the
insertion point the same verified way this time: matched the unique
`],"audit_configuration":` boundary that closes the `events` array
specifically (not the DATA statement's outer closing bracket, which
belongs to `cloud_actions`), and confirmed `cloud_actions`'s length
was unchanged (5,148) both before writing and after.

Verified: `node --check`. `DATA.events` grew from 4,783 to 4,803 (20
new, unique ids, no duplicates) on top of the 4,783 the WebAuth PR
above had already landed at merge time. Header stat updated to "4,803
events - 194 logs - 193 categories" (four new log channels - one per
Channel value used - plus WebAuth's own log/category from the merge
above - and one new category). Searching
"ServerUSBDevices" returns exactly 20 rows, sorted ascending by id
(2, 3, 4...44) with no gaps or duplicates. Confirmed at 375px and in
both themes with zero console errors; every other tab, and the
untouched WebAuthN entries, unaffected.

This PR and the WebAuth one above were built in parallel off the same
`main` commit, so both independently bumped `1.3.1` -> `1.3.2`; by the
time this one's turn came to merge, WebAuth's `1.3.2` was already on
`main`, so resolving the conflict meant bumping this PR one step
further:

`1.3.2` -> `1.3.3` (PATCH - new data rows on the existing Events page;
not a new catalogue, tab, or app-level capability).

Asked to check a pasted list of 26 `Microsoft-Windows-Kernel-General`
rows (18 distinct event ids, some with several manifest "Version"
variants of the same id - e.g. id 1's five versions all describe a
system time change, just with progressively more fields). This source
was already partly catalogued, but unlike the two providers added in
the prior two PRs, it wasn't absent - four of its ids (1, 12, 13,
1017) were already there, as hand-curated "illustrative" entries with
real citations (NSA's Event Forwarding Guidance, ASD/ACSC's priority
logs guidance) rather than raw manifest text. Cross-checked the
pasted ids against `DATA.events` filtered to this source: ids 1, 12,
13 matched existing entries (id 1's five pasted versions all collapse
to the one existing "System Time Changed" row - this catalogue keeps
one row per event id for this source, not one per manifest version,
confirmed by the existing four having zero duplicate ids between
them); the other 18 ids (2-6, 11, 14-25) had no entry at all.

Added the 18 missing ids, keeping the pre-existing four untouched.
Followed the manifest-import "template" schema from the previous two
PRs rather than inventing "illustrative" framing or citations for
ids the four existing entries' NSA/ASD sources don't happen to cover
- more honest than fabricating a security narrative I can't verify.
Where a pasted row had several Version variants of one event id (18,
19, 23), used the most complete/highest-numbered version's message as
the single canonical description, same collapsing rule as id 1
above. A few provider-specific wrinkles this manifest export
surfaces:

- This source logs to the classic `System` channel (matching the log
  value all four pre-existing entries already use), not a dedicated
  `Applications and Services Logs` channel, so `log` is `"System"`
  for every new entry too - including the handful of rows (ids 14,
  17, 19, 23) where the manifest itself leaves the Channel column
  blank, treated here as inheriting this provider's one known
  destination rather than invented as a separate channel string.
- `category` uses the same hand-picked, human-readable categories the
  four pre-existing entries already established for this source
  (`System Integrity`, `Boot Events`) rather than defaulting to the
  raw source string the manifest-only providers in the prior two PRs
  used - registry/hive/licence-cache/time-integrity events under
  `System Integrity`, restart and boot-performance-telemetry events
  (ids 18, 19, 23) under `Boot Events`, both categories chosen to sit
  naturally alongside the sibling entries already filed there
  (id 1 is already `System Integrity`; ids 12/13 are already `Boot
  Events`).
- Ids 14, 17, 19 and 23 have an empty Message column in every version
  the manifest lists - rendered with the same "no message template
  provided by the manifest" filler used for the previous two PRs'
  template-less events, naming the Task where the manifest gives one
  (`BootPerformanceData` for 19, `VsmPerformanceData` for 23) and
  falling back to a generic "(Event from ...)" form for the two ids
  (14, 17) that have neither a Task nor a message - their only
  distinguishing detail is a Keyword
  (`KERNEL_GENERAL_SECURITY_ACCESSCHECK`, `KERNEL_GENERAL_TOKEN_SID_MANAGEMENT`)
  that doesn't have a field to hold it in this catalogue's schema.

Located the splice point the same verified way as both prior PRs -
matched the unique `],"audit_configuration":` boundary, confirmed
`cloud_actions` was unchanged (5,148) before and after.

Verified: `node --check`. `DATA.events` grew from 4,803 (already
reflecting the WebAuth and ServerUSBDevices PRs merged above) to
4,821 (18 new, unique ids; no duplicate event ids anywhere in this
source's now-22 entries). Header stat's log and category counts held
steady at 194 and 193 respectively - every new entry reuses a
`log`/`category` value this catalogue already had, unlike the two
PRs above which each introduced entirely new ones. Searching
"Kernel-General" returns all 22 entries (4 pre-existing + 18 new) sorted ascending by
id with no gaps or duplicates: 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15,
16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 1017. Confirmed at 375px and
in both themes with zero console errors; the four pre-existing
entries and every other tab unaffected.

This PR was built off the same pre-WebAuth `main` commit as the two
above, so it independently bumped `1.3.1` -> `1.3.2` too; by the time
its turn came to merge, `main` was already at `1.3.3` (from the two
prior merges), so resolving the conflict meant bumping one step
further:

`1.3.3` -> `1.3.4` (PATCH - new data rows filling gaps in a
partly-catalogued source; not a new catalogue, tab, or app-level
capability).

Asked to check a pasted list of 429 `Microsoft-Windows-Kernel-Power`
rows (349 distinct event ids, many with several manifest Version
variants - id 507 alone has 13). Zero entries for this source existed.
Given the scale - by far the largest single list pasted this session -
and that 317 of the 429 rows carry no message text at all (this
provider is an extremely verbose ETW power/sleep/thermal diagnostic
source, most of it internal telemetry rather than anything
security-relevant), flagged the size and asked whether to add
everything or only the rows with real message text before building
anything. Told to add only the ones with messages.

Filtered to the 112 rows with a non-empty Message column, then
collapsed Version variants down to one canonical row per event id -
same rule used for `Microsoft-Windows-Kernel-General` earlier in this
session - taking the highest-numbered version's row (message text,
level, channel and task together, not just the message in isolation,
since a few ids' later versions also correct the channel or task
alongside adding fields). That collapsing took 112 rows down to 72
distinct event ids. Followed the same manifest-import "template"
schema as the three PRs above: `category` defaults to the raw source
string (`Microsoft-Windows-Kernel-Power`, no existing human-curated
category to match here, unlike Kernel-General), `subcategory` is the
Task column (every one of the 72 canonical rows has one), `log` is
the raw Channel column value verbatim per row - not always prefixed
with the source, since the manifest itself sometimes gives a bare
channel name (`Thermal-Operational`, alongside `System`,
`Microsoft-Windows-Kernel-Power/Diagnostic` and
`Microsoft-Windows-Kernel-Power/Thermal-Diagnostic`) - `description`
keeps the manifest's message text verbatim with `{Field}` placeholders
unresolved, and `reference` is the same ETW manifest export citation.

Located the splice point the same verified way as every PR above:
matched the unique `],"audit_configuration":` boundary, confirmed
`cloud_actions` was unchanged (5,148) before and after.

Verified: `node --check`. `DATA.events` grew from 4,821 to 4,893 (72
new, unique ids, no duplicates within the new source). Header stat
updated to "4,893 events - 197 logs - 194 categories" (three new log
values - `System` was already in use by other providers, so only the
Diagnostic/Thermal-Diagnostic/Thermal-Operational channels count as
new - and one new category). Searching "Kernel-Power" returns 76
rows, not 72: four belong to an unrelated pre-existing source,
`EventLog / Kernel-Power / USER32` (a legacy classic-Event-Log
provider whose own event id 41 happens to collide with the new
provider's DirtyTransition id 41 - both real, distinct entries, not a
duplicate). Confirmed at 375px and in both themes with zero console
errors; every other tab, including that pre-existing unrelated
source, unaffected.

`1.3.4` -> `1.3.5` (PATCH - new data rows on the existing Events page;
not a new catalogue, tab, or app-level capability).

Given an AWS-supplied `.xlsx` (204 rows, one per AWS GuardDuty finding
type currently in the `Active` status - finding type, affected
resource, the foundational data source/feature that has to be enabled
to generate it, AWS's own severity rating, a summary, a detailed
description, and remediation guidance, all copied verbatim from AWS's
own "GuardDuty active finding types" documentation page) and asked to
add it as a new page inside the Threat Detection app, next to
Validations, called Native.

This is a different kind of addition from every one of this session's
prior PRs: those all added rows to the Windows Events catalogue's
existing `events` array and schema. This is a whole new page inside a
*different* merged app (Threat Detection, `#app-td`), holding a
*different* content type the existing schema has no field for (AWS's
own vendor documentation, not a detection rule or a validation
test-execution reference). So it gets its own array, its own facets,
and its own render pipeline - the same choice this app already made
once before for Validations (see `docs/validations.md` and the
"Validations is not a detection catalogue" intro banner on that page):
a parallel, self-contained search/filter-sidebar/card-grid/detail-overlay
pipeline living beside Detections' and Validations' own copies of the
same pattern, sharing only the generic CSS classes (`.card`,
`.filter-group`, `.kv-table`, etc.) and the one `#td-overlay`/
`#td-detail-panel` DOM pair all three pipelines open detail views into.

Threat Detection Library's own header badge (`v1.2.0`, next to the TD
logo) is left untouched. That badge tracks the vendored
`Threat-detection-library` project's own upstream version - this
repo's README explicitly documents `threat-detection/` as vendored in
"unchanged" (see Structure below) - and Native is a catscan-only
layer on top of it, present nowhere upstream, exactly like the filter
toggles and breadcrumb added to other merged apps earlier this session
never touched *their* source repos' versioning either. Only this
repo's own top-level `VERSION` moves.

Fields, mapped straight from the workbook's columns: `finding_type`
(e.g. `Impact:EC2/BitcoinDomainRequest.Reputation`), `threat_purpose`
(derived - not an original column - by splitting `finding_type` on its
first `:`, which is GuardDuty's own top-level grouping convention: 20
distinct values across the 204 rows, from `AttackSequence` (5) to
`Impact` (24)), `resource_type`, `foundational_data_source` (the
"Foundational data source / Feature" column), `severity` (kept
verbatim - AWS's own severity field is inconsistent across rows,
mixing clean values like `Critical`/`High`/`Medium`/`Low` with
variable ones like `High (variable)`, `Low (variable)`, `Variable`,
and `Varies depending on detected threat`; normalizing that away would
misrepresent what AWS actually publishes), `summary`,
`detailed_description`, `remediation` (the "Remediation
recommendations" column), `detail_data_source` (a "Detail page data
source / Feature" column, blank on 4 rows), and `detail_url` (the "AWS
detail page URL" column, present on every row). Two columns were
dropped: an entirely-blank spacer column between "AWS detail page URL"
and "Catalogue source" in the source workbook, and "Catalogue source"
itself, which only carries a value on the sheet's first row (the
overall page's own citation URL, not a per-finding field) - quoted
instead in the page's own intro banner. `id` is a `gd-` + slugified
`finding_type`, generated fresh (204 unique, verified against
collisions), since finding types don't ship with an id of their own.

Sidebar facets: Threat Purpose (20 options, sorted by count - `Impact`
top at 24), Resource Type (13 options - `Instance, EKS cluster, ECS
cluster, or container` top at 46), Severity (in AWS's own rough
severity order, only the 8 values actually present in the data - no
`High (variable)` or `Medium (variable)` badge colors invented beyond
reusing the closest clean tier's color, since AWS doesn't define a
distinct visual tier for the variable ones), and Foundational Data
Source (17 options - `Runtime Monitoring` top at 46). All four use the
exact same collapsible-group/clear-button/live-count sidebar component
Validations already built, not a new one.

Verified: `node --check`. Page loads with all 204 entries, the default
(unfiltered) view. Searching "cryptocurrency" returns 10 matches
across finding type, summary and detailed description text. Clicking
the Threat Purpose sidebar group open and selecting "Impact" narrows
to exactly 24 results (matching its sidebar count) and shows one
active filter chip; clearing it or re-clicking the same option
restores all 204. Opening a card's detail view renders its full
summary, detailed description, remediation, foundational data source,
and a working link to AWS's own detail page; Escape and the overlay
backdrop both close it cleanly, same as every other detail view in
this app. Confirmed at 375px and in both themes with zero console
errors; Detections, Heat Coverage, and Validations all unaffected -
their own view-tab switching, header-widget-hiding CSS, and shared
detail overlay state (`closeDetail()` now also resets
`nativeState.activeId`, alongside the pre-existing `state.activeId`
and `validationState.activeId`) all still work exactly as before.

`1.4.0` (MINOR - a whole new page/tab inside the Threat Detection app,
backed by an entirely new 204-entry dataset and its own search/filter/
detail pipeline; squarely the "new tab" case this repo's own
versioning policy reserves MINOR for, unlike this session's earlier
PATCH-level additions of rows to an existing page).

Two follow-up requests against the just-merged Native page. First:
give every entry a `platform` field valued `"AWS GuardDuty"`, with its
own sidebar filter - explicitly "with filtering for platforms" (plural),
naming the exact multi-value design Validations already uses for its
own `platform` facet (RHEL, FortiGate, Cisco SD-WAN, RHEL IdM/IPA,
Windows Endpoint all sharing one page, one facet). Implemented
`platform` as an array field (`["AWS GuardDuty"]`) rather than a plain
string for the same reason Validations does: today Native holds a
single native-detection source, but the field and facet are shaped so
a second one (a future non-GuardDuty native-detection catalogue) can
share this same page later without a schema change - the point of
asking for "filtering for platforms" at all when there is currently
only one. Added a Platform section to the sidebar (first, above Threat
Purpose), a Platform tag on every card and in the detail view's badge
row, `platform` into the search haystack, and a Platform filter chip -
mirroring every other facet's wiring exactly (`nativeState.platform`,
`nativeExpandedGroups.platform`, the `matchesNativeFilters` check, the
filter-count badge). Updated the intro banner's facet list to match.

Second: make Native's 204 entries reachable from the compendium-wide
Search tab (the box that already searches Microsoft Events, AWS
Events, Linux Events, Threat Detection, and Threat Validations at
once - see `window.__compHub`), under a new source labeled "Native
Detection". Threat Detection (`td`) and Threat Validations (`tv`)
already share one physical tab this way - two distinct search sources,
two distinct group labels and Sources filter chips, both jumping to
the same `#app-td` tab before their own `open()` switches to the right
sub-view - so Native Detection (`nd`) is a third instance of a pattern
this compendium-wide search already had, not a new one: added to the
`order`/`badgeClass`/`sourceFilter` maps, `TAB_TARGET.nd = 'td'` beside
the existing `TAB_TARGET.tv`, a `window.__compHub['nd']` entry whose
`open()` calls `switchView('native')` then `openNativeDetail(id)` (the
exact same shape as `tv`'s `switchView('validations')` +
`openValidationDetail`), a new source filter chip, a `.cs-badge-nd`
CSS class (reusing the same badge color `tv` already reuses from `td`,
since all three are one app's sub-views), and both places in the
Search tab's own copy that name the other sources by hand (the intro
paragraph, the filter chip row).

Verified: `node --check`. On the Native page, the new Platform section
renders first in the sidebar with one option, "AWS GuardDuty", count
204; selecting it keeps all 204 results (every entry matches, as
expected today) and shows a working "Platform: AWS GuardDuty" filter
chip. On the Search tab, searching "GuardDuty" returns 297 total
matches across three sources - AWS Events (91), Threat Detection (2),
and the new Native Detection (204, all of them, since GuardDuty's own
name appears throughout its finding descriptions) - each under its own
group label and `nd`-badged rows. Clicking a Native Detection result
row switches to the Threat Detection tab, switches that tab's own view
to Native, and opens the correct entry's detail overlay showing the
new "AWS GuardDuty" platform tag. Confirmed at 1500px in both themes
with zero console errors; the pre-existing `td`/`tv`/`win`/`aws`/`lnx`/
`other` search sources and their own filter chips are unaffected.

`1.4.1` (PATCH - a new filter facet on an already-existing page plus
wiring an already-existing page into an already-existing cross-
catalogue search feature; not a new catalogue, tab, or app-level
capability in its own right).

Given a Liquorice Allsorts-themed Rubik's cube image and asked to add
it next to the Cat Scan icon in the menu bar, at the same size.

The existing icon (a paw-print-behind-a-magnifying-glass, `.brand-mark`,
20x20px per its own CSS rule) is an inline SVG built from a handful of
`<ellipse>`/`<circle>`/`<line>` shapes - it can afford to be vector
because it's a simple flat-color mark. The cube image is a photoreal
3D render with soft shadows and gradients that no small set of SVG
primitives would reproduce faithfully, so it stays a raster image
rather than being redrawn as vector shapes.

This repo has no image asset files anywhere - every icon already in
the page (the favicon included) is either inline SVG or a base64 data
URI, keeping the merged page self-contained with no external asset
requests. Followed that same convention rather than introducing the
project's first separate image file: downscaled the source PNG (a
1254x1254 transparent-background render, 2.0MB) to 64x64 with Pillow's
Lanczos filter - large enough to stay crisp at up to 3.2x pixel density
on a 20px display box, small enough that its base64 encoding (~13KB)
barely registers against this page's overall size - and embedded it as
an `<img class="brand-mark">` immediately after the existing SVG, so it
picks up the exact same `width: 20px; height: 20px` rule with no new
CSS. `alt=""` and `aria-hidden="true"` match the existing icon's own
decorative treatment (the accessible name is the "Cat Scan" text next
to it, not either icon); a `title` attribute names the image for anyone
who hovers it, since neither icon carries a visible caption.

Verified: `node --check`. Both `.brand-mark` elements measure exactly
20x20px and sit side by side with the same 8px gap `.compendium-title`
already gives every child. The image decodes and paints correctly
(`naturalWidth > 0`, `complete: true`). Confirmed at 375px and in both
themes with zero console errors; every other icon and the version tag
unaffected.

`1.4.2` (PATCH - a purely cosmetic addition to the existing menu bar;
not a new catalogue, tab, or app-level capability).

Given a second image (a spiral "Q" mark in the same liquorice-allsorts
palette) and asked to replace the just-added cube icon with it. Same
treatment as before, this time cropped first: the source PNG (1254x1254,
transparent) had asymmetric padding around the mark itself (`getbbox()`
returned a 1131x1103 region offset from center, not the full canvas),
so cropped to that content box, re-padded to a square canvas around it
(centering the mark rather than resizing the off-center crop directly,
which would have skewed it), then downscaled to 64x64 with the same
Lanczos filter and re-encoded as base64 (~10KB). Swapped only the
`<img class="brand-mark">` element's `src` and `title` (now "Cat Scan
mark", since it no longer depicts a cube) - the surrounding markup,
CSS, and every other file this session's cube-icon PR touched are
untouched.

Verified: `node --check`. Both `.brand-mark` elements still measure
exactly 20x20px side by side. The image decodes and paints correctly.
Confirmed in both themes with zero console errors.

`1.4.3` (PATCH - swapping one already-added cosmetic image for
another; not a new catalogue, tab, or app-level capability).

Given an uploaded Microsoft Sentinel analytics-rule catalogue workbook
(2,529 rows, sourced from AnalyticsRules.Exchange's own downloadable
index, enriched from the corresponding Azure-Sentinel YAML files - its
own `About` sheet's stated totals: 2,529 unique rule IDs, 2,513 with a
KQL query, 35 deprecated, 813 High / 1,317 Medium / 272 Low / 101
Informational severity) and asked to add it to the Native page as a
second platform, "Microsoft Sentinel", alongside the existing AWS
GuardDuty data.

Sentinel's own 27-column schema (Rule ID, Rule name, Description,
Severity, Kind, Tactics, Techniques, Required connectors/data types,
query frequency/period, trigger operator/threshold, Entity types,
Version, Deprecated, Repository path, Catalogue URL, GitHub source
URL, and a full KQL query per rule) doesn't line up with GuardDuty's
narrower one field-for-field, so each entry was mapped onto the
existing Native shape where the concepts genuinely correspond, and the
shape was extended with a handful of new optional fields for the rest
rather than force-fitting Sentinel-only concepts (a MITRE ATT&CK
tactic/technique list, connector/data-type requirements, query cadence,
a full KQL query) into fields that meant something narrower for
GuardDuty:
- `threat_purpose` (the existing Platform-filterable facet) becomes the
  rule's primary MITRE ATT&CK tactic (first of its `Tactics` column,
  split on `;`); rules with no tactic listed fall back to
  "Uncategorized" (347 of 2,529 rows had no Tactics value).
- `resource_type` becomes the rule's primary entity type (first of its
  `Entity types` column); falls back to "Unspecified" (251 rows had none).
- `foundational_data_source` becomes its required data types (joined),
  falling back to required connectors, then "Unspecified" (265 and 148
  rows respectively had none of either, still leaving every row a value).
- `severity` is normalized to title case (High/Medium/Low/Informational -
  one source row read "HIGH" in all-caps, a plain data-entry
  inconsistency, not a distinct tier worth preserving verbatim the way
  GuardDuty's own "High (variable)" is); blank severities (26 rows)
  become "Unspecified". "Informational" and "Unspecified" were added to
  the existing severity ordering and badge-class maps (an `.informational`
  badge class already existed in the shared CSS, reused as-is).
- `summary` is the rule's first sentence (regex-extracted, falling back
  to a truncated lead-in when no clean sentence boundary is found);
  `detailed_description` is the full description - kept genuinely
  distinct so the detail view's teaser paragraph and its "Detailed
  Description" section don't just repeat each other verbatim, the way
  they would have if both had been set to the same full text. A stray
  leading `'` character on every `[Deprecated]`-prefixed rule's
  description (a source-workbook artifact, not intentional formatting)
  is stripped during cleanup.
- `detail_url` is the rule's AnalyticsRules.Exchange catalogue page
  (playing the same role GuardDuty's AWS docs URL already did); the
  kv-table row that names it was renamed from "AWS Detail Page" to the
  platform-neutral "Detail Page" now that a second platform uses it.
- `remediation` and `detail_data_source` (both GuardDuty-specific
  concepts with no Sentinel equivalent in this data) are left unset;
  the detail view already renders both conditionally, so Sentinel
  entries simply omit those sections rather than showing something
  contrived.
- New optional fields with no GuardDuty counterpart - `rule_kind`,
  `tactics`/`techniques` (full lists, not just the primary one used for
  filtering), `required_connectors`/`required_data_types`, `query_frequency`/
  `query_period`, `trigger_operator`/`trigger_threshold` (rendered as a
  plain-language "Alerts when the result count is greater than 0" line,
  operator codes like `gt`/`lt` spelled out), `rule_version`,
  `deprecated`, and `github_url` - are rendered as additional detail-view
  sections and kv-table rows, each gated on the field's presence so
  GuardDuty's 204 existing entries (which have none of them) render
  exactly as before. The full KQL query (present on 2,513 of 2,529
  rows) gets its own code block with a working "Copy" button, reusing
  the Detections pipeline's own `.code-block`/`.copy-btn` pattern
  (`data-copy` attribute read against the open entry's own field) rather
  than inventing a second implementation of the same idea. A MITRE
  ATT&CK section lists every tactic and technique the rule carries (not
  just the primary one used for the Threat Purpose filter), as its own
  tag row.

All 2,529 rows were kept, including the 35 marked deprecated in their
source YAML - the workbook's own scope note says this by design, and
demoting or filtering them would silently drop real catalogue history
a reader might specifically be looking for (the "Deprecated" kv-table
row surfaces this on each one, pointing at the source repository for a
possible replacement, rather than hiding it).

The `NATIVE` array (a single flat list backing the whole page, `id`
namespaced `sentinel-<rule ID>` alongside the existing `gd-<slug>`
GuardDuty entries so no cross-platform collision is possible) grew from
204 to 2,733 entries; the intro banner and two code comments describing
the Native page (previously written as if GuardDuty were its only
occupant) were reworded to describe both platforms' own conventions
side by side. No changes were needed to the Platform-facet, search-
integration, or sidebar/card-grid/filter-chip code added in the
previous two Native-page PRs - it was already built generic enough
(a `platform: []` array reused as-is, facet counts computed from
whatever values are actually present) to take a second platform with
no code changes of its own.

Verified: `node --check`. On the Native page, the Platform section now
shows two options - "AWS GuardDuty" (204) and "Microsoft Sentinel"
(2,529) - and the card grid renders all 2,733 entries with the correct
per-platform count in each case; selecting "Microsoft Sentinel" narrows
to exactly 2,529 results with a working filter chip. A Sentinel entry's
detail view shows its severity badge, platform/tactic/entity tags, a
MITRE ATT&CK tag row, a copyable KQL code block, and a fully-populated
kv-table (data source, connectors, rule kind, query cadence, trigger
condition, version, Detail Page, and GitHub Source links). A GuardDuty
entry's detail view is unchanged byte-for-byte in every section that
doesn't depend on the new optional fields, confirming the schema
extension is additive only. Searching "Sentinel" on the Search tab
returns Native Detection matches (capped at the existing 40-per-source
display limit) with no change to any other search source. Confirmed at
1500px and 375px in both themes with zero console or page errors.

`1.4.4` (PATCH - new data rows and optional schema fields on an
already-existing page, reusing its already-existing Platform facet;
not a new catalogue, tab, or app-level capability).

Asked to move the spiral-Q mark image to the far left of the menu bar,
then replace it with a third image (a rounded, striped liquorice-
allsorts-style block: pink/black/white/black/green). Two changes to
the same two `.brand-mark` elements: reordered the markup so the `<img>`
now comes before the `<svg>` paw-print-behind-a-magnifying-glass icon
(previously the other way around), then swapped that `<img>`'s `src`
and `title` for the new image, leaving the SVG icon itself untouched.

Same processing as the previous two image swaps: the source PNG
(1254x1254, transparent) again had asymmetric padding around the mark
(`getbbox()` returned a 1121x1139 region offset from center), so
cropped to that content box, re-padded to a square canvas centered on
it, then downscaled to 64x64 with Lanczos and re-encoded as base64
(~9.3KB). `title` updated to "Liquorice Allsorts mark" (it depicts a
stack of candy-striped blocks, not the Q-mark shape the previous title
named); `alt=""` and `aria-hidden="true"` carried over unchanged.

Verified: `node --check`. Both `.brand-mark` elements still measure
20x20px and sit side by side in the new order (image first, then the
SVG icon, then the "Cat Scan" wordmark). The image decodes and paints
correctly. Confirmed in both themes with zero console errors.

`1.4.5` (PATCH - reordering and swapping purely cosmetic menu bar
icons; not a new catalogue, tab, or app-level capability).

Asked to populate the Schema Explorer tab for FortiManager under Other
Events - the only one of Other Events' eight vendor tabs whose Schema
Explorer was still just an explanatory paragraph with nothing to
click through, unlike the other seven.

That paragraph existed for a real reason, stated in its own text:
FortiManager/FortiAnalyzer's Log Message Reference doesn't document
per-message-ID fields at all ("hundreds of message IDs across all
subtypes"), so there's no genuine per-subtype schema to enumerate the
way FortiGate's or Zscaler's Schema Explorer does - building one would
mean inventing data the source doesn't have, which this repo doesn't
do for any vendor. But the source does document one real, already-
loaded set of field data: 12 fields common to every FortiManager/
FortiAnalyzer event log line (`common_field_schema.fields` in
`other/data/fortimanager_log_schema.json`), already flattened into
`fmRows` for Log Types search and already rendered as a table under
Reference > Common fields - just never surfaced in the Schema Explorer
tab itself, leaving it inconsistent with every other vendor.

Populated it by reusing that same data rather than adding any new
source material: filtered `fmRows` down to its existing `isField` rows
into a flat, searchable, sortable table (Field / Example / Type /
Description - the same four columns Reference > Common fields and
Dell iDRAC's own Schema Explorer both already use), following the
precedent Dell iDRAC's Schema Explorer set for source material with no
per-category field list of its own: flatten what field data genuinely
exists into one browsable table, and clicking a row opens the exact
same detail modal its Log Types row already would (`fmOpenModal`,
unmodified - it already branched on `isField`). No type-rail sidebar,
unlike FortiGate/Infoblox/Dell iDRAC's Schema Explorers - those group
multiple distinct field sets, where FortiManager has exactly one. The
explanatory paragraph stays, trimmed to also describe the table now
below it, so the "why no per-subtype fields" context isn't lost.

Verified: `node --check`. All 12 common fields render in the new
table; searching narrows correctly (e.g. "session" matches only
`session_id`); clicking a row opens the correct field detail modal
("FortiManager common field" eyebrow, matching title); sorting by
Field toggles ascending/descending correctly. Confirmed FortiGate's
and Dell iDRAC's own Schema Explorers (the two other vendors whose
Schema Explorer this touches shared CSS with) still render their full
row counts unaffected (63 and 27 rows respectively). Confirmed at
1500px and 375px in both themes with zero console errors.

`1.4.6` (PATCH - making an already-loaded field dataset browsable in
a tab that already existed for every vendor including this one; not a
new catalogue, tab, or app-level capability).
Asked to do a full UI/design pass across every tab in both themes and
at both desktop and mobile width, then fix two of the findings: the
Search tab not following the theme toggle, and a code block/Copy
button overlap in Threat Detection's detail modal.

**Search tab theme bug.** On a first visit with no saved preference,
Search (and the shared menu bar/breadcrumb chrome around every tab)
stayed on the shell's dark default even when the OS/browser preferred
light - the theme toggle's own label correctly said "Light" in that
state, but the visual result didn't match it. Root cause: every one of
the five embedded apps (`#app-win`, `#app-aws`, `#app-lnx`, `#app-td`,
`#app-other`) already has its own three-state theme CSS - an explicit
`[data-theme="dark"]`/`[data-theme="light"]` pair plus a
`@media (prefers-color-scheme: dark)` fallback, guarded with `:not()`,
for the "no explicit choice yet" case - but the *shared shell* tokens
(`:root`/`body[data-theme="light"]`, which the menu bar, breadcrumb,
and Search page all draw from directly rather than through an
app-scoped token set) only had two of those three states: an
unconditional dark `:root` default and an explicit-light override.
There was no equivalent `@media (prefers-color-scheme: light)`
fallback, so "no explicit choice + OS prefers light" fell through to
the dark default everywhere the shell tokens are used. Fixed by adding
that missing state - `@media (prefers-color-scheme: light) { body:not([data-theme="dark"]) { ... } }`
- duplicating the existing light values, mirroring the exact guard
idiom already used by `#app-td`'s own theme CSS. No JS changes needed:
`shell-theme-toggle`'s existing script already does the right thing
(only setting `data-theme` on an explicit click, leaving it unset for
"follow system") - the gap was purely a missing CSS state.

**Code block / Copy button overlap.** In Threat Detection's detail
modal, the floating "Copy" button over an SPL query or CLI reference
block sat on a background only 8% opaque
(`rgba(255,255,255,0.08)`) over the code's own dark background, so
long lines of code visibly bled through underneath the button's own
label rather than being cleanly covered by it - worst on the SPL
query block, where the first line routinely runs the full width of
the panel. This isn't fixable by adding padding: `white-space: pre`
content doesn't reflow around padding, so a long line still reaches
the box's visible edge (and the button pinned there) regardless of
how much padding the block itself has. Fixed by making the button's
background fully opaque (`var(--code-bg)`, the code block's own
background, so it's indistinguishable from the surrounding block
rather than a separate visible seam) with a soft same-color
`box-shadow` fading in from its left edge, so text now cleanly
disappears behind an obviously-intentional floating control instead of
half-showing through a translucent one - the same pattern GitHub's and
VS Code's own code-block copy buttons use. Hover feedback moved from a
background change (which would have reintroduced the translucency,
and the bleed-through with it, on every hover) to a border/text-color
change instead, keeping the background opaque in every state. This is
shared CSS (`#app-td .copy-btn`), so it also fixes the same overlap on
the Native page's KQL query code block added earlier this session,
with no separate change needed there.

Verified: `node --check`. On a fresh browser profile (no saved theme)
with the OS set to prefer light, Search's background now resolves to
the correct light value (`#f6f3ec`) and the shared menu bar to white,
matching the toggle's "Light" label, with `body` correctly carrying no
explicit `data-theme` attribute (still following the OS, not pinned) -
confirmed OS-prefers-dark still correctly stays on the dark default
(no regression), and that an explicit toggle click still sets and
persists `data-theme` across a reload exactly as before. On the Copy
button, confirmed its computed background is now fully opaque,
`elementFromPoint` at its center resolves to the button itself (not
the text below it), and clicking it still copies the correct text to
the clipboard. Regression-checked Microsoft/AWS/Linux/Other
Events/Threat Detection's own render counts across both themes and
both 1500px/375px viewports - all unchanged, zero console errors
throughout.

`1.4.7` (PATCH - skips `1.4.6`, already claimed by a still-open,
not-yet-merged PR for the FortiManager Schema Explorer work earlier
this session, to avoid a guaranteed version collision between the two;
fixing a theming gap and a visual overlap bug on already-existing
pages, not a new catalogue, tab, or app-level capability).

Asked to fix three more findings from the same UI/design pass: the
Threat Detection library's own stats line ("4,017 detections (31
ESXi/Splunk SPL + ...)") showing on the Native tab even though Native
isn't this library's detection content at all; a Native card title
("AttackSequence:S3/CompromisedData") wrapping mid-syllable
("CompromisedD" / "ata"); and Microsoft Events' secondary tab row
(Events / Reference tables / Schema explorer / ...) clipping off-screen
on mobile with no indication more tabs exist.

**Stats line on Native.** `#td-stats-line` lives in one shared
`.lib-stats-wrap` above all four view containers, not inside any one
of them, so `switchView()` never touched its visibility - it always
showed, regardless of which tab was active. Accurate and useful
context on Detections, Heat Coverage, and Validations (all of this
library's own content), but Native is raw third-party vendor catalogue
data, so a detection count/ATT&CK-coverage line describing this
library's own writing doesn't describe what's on screen there. Hidden
it specifically on Native with `#app-td.native-active .lib-stats-wrap{ display: none; }`,
the same container-class pattern already used to hide the header's
search/filter widgets on Validations and Native.

**Native card title mid-word break.** `.card-title` had both
`overflow-wrap: break-word` and the older `word-break: break-word` -
redundant, so the latter (legacy, more aggressive alias) was removed,
but that alone didn't change anything: GuardDuty/Sentinel identifiers
like `AttackSequence:S3/CompromisedData` routinely run 15+ characters
with no spaces, and once a single unbroken run like `CompromisedData`
is itself wider than the card, `overflow-wrap`'s last-resort fallback
still has no better option than an arbitrary mid-character split.
Fixed properly by giving the renderer real break opportunities before
it ever needs that fallback: a `nativeSoftBreak()` helper inserts a
`<wbr>` after every `:`/`/`/`_`/`-` and at every camelCase
(lowercase-to-uppercase) transition, so `CompromisedData` now has a
legal break between `Compromised` and `Data` - a readable word
boundary - well before the fallback would ever need to guess. Applied
to both the card grid and the detail overlay's title (the same
underlying string, just at a different width); nowhere else in Native
or the wider Threat Detection app touches long enough unbroken
identifiers for this to matter, so scoped to just those two spots.

**Mobile tab-row clipping.** Windows Events' own secondary tab row
(`nav.tabs`) scrolls horizontally on narrow viewports rather than
wrapping (unlike Linux Events' equivalent row, which already wraps
onto multiple lines and was never affected by this) - and nothing
visually hinted that "Schema e[xplorer]" cut off at the screen edge
continued off-screen rather than just being the last tab. Added the
standard no-JS "scroll shadow" technique: two pairs of background
gradients, one pair that scrolls with the tab buttons themselves
(`background-attachment: local`, acting as a solid mask that slides
away from whichever edge has nothing left to reveal) layered over
another pair pinned to the row's own edges
(`background-attachment: scroll`, the actual visible shadow) - so a
faint shadow only ever appears on the edge that genuinely has more
tabs to scroll to, and disappears on its own once you've scrolled all
the way to that edge. No markup changes, no JS.

Verified: `node --check`. The stats line is confirmed visible on
Detections/Heat Coverage/Validations and hidden on Native, in both
themes. The GuardDuty card title in question now renders as
"AttackSequence:S3/Compromised" / "Data" across two lines instead of
splitting `CompromisedData` itself. Windows Events' mobile tab row
shows a right-edge shadow at rest, and shows shadows on both edges
once scrolled partway, in both themes; confirmed the row's
`scrollWidth` still genuinely exceeds its `clientWidth` (a real
overflow, not a cosmetic-only shadow). Regression-checked
Microsoft/AWS/Linux/Other Events/Threat Detection's own render counts
across both themes and both 1500px/375px viewports - all unchanged,
zero console errors throughout.

`1.4.8` (PATCH - hiding an irrelevant stats line on one existing tab,
a text-wrapping fix on existing card/detail titles, and a scroll
affordance on an existing tab row; not a new catalogue, tab, or
app-level capability).

Asked to recheck the app for further UI issues after the previous
round of fixes landed. A fresh pass across tabs not deeply checked
before (Schema Explorer, Pivot Explorer, Cloud logs, Cloud Actions
Explorer, an event detail pane, Validations, Other Events' Reference
tab and a second vendor, Search with an actual query typed, and mobile
views of AWS/Other Events/Search) turned up two more, both fixed:

**Wide data tables clip their last column, with no scroll hint, even
on desktop.** Confirmed in Microsoft Events' Schema Explorer (the
"Type" column cut off at 1500px) and its Cloud Actions Explorer (same,
"Resource Type") - both share one `.se-table-wrap` component, and both
already scroll (`overflow: auto`, `scrollWidth` genuinely exceeds
`clientWidth`), just with nothing showing a reader a column continues
off-screen. Same underlying problem the mobile tab-row fix in `1.4.8`
solved, just recurring in an actual data table and at full desktop
width, not only mobile. Applied the identical no-JS scroll-shadow
technique to `.se-table-wrap` instead of writing it a second time -
same layered `local`/`scroll`-attachment gradient pairs, just using
this component's own `--surface` token for the mask color. Verified it
keeps working correctly combined with this element's other axis of
scrolling too (it's vertically scrollable past 560px as well) - the
horizontal shadow still reads correctly at an arbitrary vertical
scroll position, confirmed by scrolling both axes and screenshotting.

**Threat Detection's own stats/coverage paragraph pushes real content
far down the screen on mobile.** Re-confirmed with a fresh screenshot:
before reaching a single detection card, a phone-width reader scrolls
past the compendium tabs, the breadcrumb, this app's own header and
search box, a Filters/Coverage/Export/theme row, a Companion
Tools/GitHub row, the four view-tabs, and then the full multi-line
stats paragraph - six-plus stacked blocks. The paragraph itself is
useful, verbatim, and unique to this library, so it's not going away -
but reworking the header chrome around it is the larger, still-open
reskin this session flagged and deliberately hasn't taken on. In the
meantime, clamped the paragraph itself to 2 lines with a `-webkit-line-clamp`
ellipsis, scoped to the same 880px breakpoint this app already uses
for its mobile filter drawer - unchanged (full paragraph, no clamp) on
anything wider. Cuts a meaningful chunk of the scroll distance to the
first real card without touching layout, header markup, or branding.

Verified: `node --check`. Schema Explorer and Cloud Actions Explorer
both show a right-edge shadow at rest and shadows on both edges once
scrolled partway, confirmed in both themes; the Cloud Actions
Explorer's own dark-theme rendering checked directly since it's a
separate instance of the same shared component. The Threat Detection
stats line measures a fixed 2-line height on a 390px viewport and its
full, unclamped multi-line height at 1500px (`-webkit-line-clamp:
none` there), confirmed by computed style, not just a visual read.
Regression-checked Microsoft/AWS/Linux/Other Events/Threat Detection's
own render counts across both themes and both 1500px/375px viewports -
all unchanged, zero console errors throughout.

`1.4.9` (PATCH - a scroll affordance on two already-existing wide
tables and a mobile-only clamp on an already-existing text block; not
a new catalogue, tab, or app-level capability).

Asked to recheck the app again. A fresh pass across tabs not yet
covered (Windows Events' Reference tables, Linux Events' Auditd Rules
and Fapolicyd sub-tabs and its own Reference tables, an AWS Events
detail modal, a Validations detail overlay, Native's own detail
overlay on mobile, and Zscaler's Schema Explorer under Other Events)
turned up one real, more serious bug, fixed here; two things that
looked like bugs at first turned out to be artifacts of the test
script itself, not the app, and are noted below for the record rather
than "fixed."

**Long identifiers in detection-logic prose were silently unreadable
on mobile, not just ugly.** Opening a Detections/Validations/Native
entry with a long unbroken technical identifier in its prose (e.g.
"...or the equivalent VmRemoveSnapshotEvent/VmRemoveAllSnapshotsEvent
from vCenter...") on a narrow viewport didn't wrap it and didn't
scroll to reveal it either - it was simply invisible past the edge,
with nothing on screen suggesting text was missing. Confirmed this
wasn't page-level horizontal scroll (`document.body.scrollWidth`
matched `window.innerWidth` exactly) - some ancestor clips overflow
rather than letting the page scroll, so unwrapped text past the edge
is just gone, not reachable by scrolling either. None of
`.detail-title`, `.detail-section p`/`ul`/`li`, or `.kv-table td` - the
entire text surface of a Threat Detection detail overlay - had
`overflow-wrap: break-word` anywhere, unlike `.card-title`, which
already did. Fixed by setting it once on `.detail-panel`, the shared
ancestor of both the header (title) and body (every section/list/
table cell) - inherited by all of it, and harmless for `.code-block`'s
own `white-space: pre` content, which doesn't wrap regardless of this
property's value.

**Not bugs, just test-script artifacts (recorded so a future recheck
doesn't re-flag the same false alarms):** an AWS Events detail modal
that appeared not to open on click was actually a race against the
async `fetch()` of `aws_iam_actions_expanded.csv` completing before
the synthetic click fired, not a real click-handler problem - a real
click on a real row opens it fine. A Validations detail overlay that
appeared to show Detections content instead was querying `.card`
without scoping to `#td-validations-card-grid`, and matched a
different, hidden card elsewhere in the DOM instead.

Verified: `node --check`. The specific paragraph in question now
measures within the detail panel's bounds instead of extending past it
(computed `overflow-wrap: break-word` confirmed inherited, not just
visually eyeballed), and wraps across two lines on a 390px viewport
instead of running off-screen; unchanged on a 1500px viewport, where
there was always room for it regardless. Confirmed the AWS Events and
Validations interactions above both work correctly once queried/timed
correctly, so no code changes were needed for either. Regression-
checked Microsoft/AWS/Linux/Other Events/Threat Detection's own render
counts across both themes and both 1500px/375px viewports - all
unchanged, zero console errors throughout.

`1.4.10` (PATCH - a text-wrapping fix across an already-existing
detail overlay's typography; not a new catalogue, tab, or app-level
capability).

Asked specifically to recheck Linux Events for improvements. A full
pass across it (Events, both Auditd Rules' and Fapolicyd's five
sub-tabs each, Reference tables, Companion Tools, both themes, mobile
width) held up well overall - better than Windows Events did before
this session's earlier fixes, even: its own mobile secondary tab row
already wraps onto two lines rather than clipping, and content with
frequent natural break points (commas, slashes) wraps cleanly without
tripping the silent-clipping bug fixed in `1.4.10`, confirmed against
a genuinely unbroken 200+ character fapolicyd MIME-type list.

One real finding, fixed here: **the Auditd Fields table overflows with
no scroll hint starting around 1280px width and narrower** - laptop
screens and tablets, not just phones. Confirmed empirically at five
widths (1500/1280/1100/900/390px): fits exactly at 1500px, genuinely
overflows (`scrollWidth` > `clientWidth`) at every width below that.
The table's own intro text already says "scroll the table right to
see it" - the author knew this needed scrolling, there just wasn't a
visual cue saying so, the same gap `.se-table-wrap` (Schema Explorer,
Cloud Actions Explorer) had before an earlier fix this session. This
table uses a different shared class, `.table-scroll` - also used by
Windows Events' own Reference-tables accordion for its expanded
tables, so the same fix benefits both apps from one change (well, two
copies of the same rule, since each app keeps its own scoped CSS
tokens rather than sharing a global stylesheet).

Applied the identical no-JS scroll-shadow technique already used
twice this session: layered `background-attachment: local`/`scroll`
gradient pairs, one added to `#app-lnx .table-scroll` and the
identical rule added to `#app-win .table-scroll`, each referencing
that app's own `--surface` token for the mask color.

Verified: `node --check`. Confirmed the Fields table's own `.table-scroll`
wrapper computes 4 background-image layers in both themes; screenshotted
it at rest (right-edge shadow, since the table is wider than the box)
and scrolled 300px right (shadow now on the left edge too, gone from
the right edge once the last column comes fully into view) - both
themes. Confirmed Windows Events' own Reference-tables `.table-scroll`
picked up the same 4 layers without needing to actually overflow in
this particular section to prove the CSS is live. Confirmed the
already-shipped `.se-table-wrap` fix and the mobile `nav.tabs` scroll
shadow are both unaffected by editing this nearby CSS. Regression-
checked Microsoft/AWS/Linux/Other Events/Threat Detection's own render
counts across both themes and both 1500px/375px viewports - all
unchanged, zero console errors throughout.

`1.4.11` (PATCH - a scroll affordance on an already-existing wide
table shared by two apps; not a new catalogue, tab, or app-level
capability).

Added a "Log file" field to Linux Events' detail panel, showing the
actual on-disk file each event's records land in - not previously
captured anywhere in this catalogue's data. Linux Events' existing
"Log" field (e.g. `audit/SYSCALL`) is auditd/journald's own
record-type name, not a filesystem path, so it doesn't answer "where
do I go find this on disk" the way it might look like it does at a
glance.

Small, curated lookup rather than derived or guessed, keyed by the
catalogue's 6 distinct `log` values: all four `audit/*` record types
(`SYSCALL`, `USER`, `DAEMON`, `MAC`) share one answer -
`/var/log/audit/audit.log` - since auditd writes every record type to
the same file regardless of type. `ssh/protocol` and
`systemd/journal` don't have one universal answer, so both are spelled
out rather than picking a side: `ssh/protocol` names both
`/var/log/secure` (RHEL/CentOS/Fedora) and `/var/log/auth.log`
(Debian/Ubuntu), since sshd logs via syslog's auth/authpriv facility
and the two distro families route that facility to different files;
`systemd/journal` explains it's a binary journal, not a flat text
file - `/var/log/journal/` if persistent or volatile in
`/run/log/journal/` otherwise, read with `journalctl`, and often also
forwarded to `/var/log/messages` (RHEL) or `/var/log/syslog` (Debian)
when rsyslog's `imjournal` module is active. Placed right after the
existing "Source" field in the detail panel's field grid, the natural
place for this kind of per-event provenance info to live.

Verified: `node --check`. Confirmed via Playwright by clicking through
all 77 events that every one shows a "Log file" value with the
expected text for its `log` category (zero missing), and that the
longer `ssh/protocol` and `systemd/journal` explanations wrap cleanly
within the field grid at both 1500px and 375px without overflowing or
clipping, in both themes. Regression-checked Microsoft Events'
own render count - unaffected, zero console errors throughout.

`1.4.12` (PATCH - a new field added to an already-existing detail
view; not a new catalogue, tab, or app-level capability).

Asked to add Microsoft Events coverage for eight specific `Log
name: System` sources: NETLOGON, Service Control Manager, LSA
(LsaSrv), Kerberos-Key-Distribution-Center, DistributedCOM,
DHCP-Server, Wininit, and Windows Remote Management. Checked existing
coverage first rather than assuming a blank slate: Service Control
Manager already had 15 well-chosen rows (the classic 7000/7001/7009/
7011/7022/7023/7024/7026/7031/7032/7034/7035/7036/7040/7045 range) and
needed nothing further; NETLOGON had only the two Zerologon-hardening
events (5827/5828); the other six had zero rows under `log: System`
specifically - DHCP-Server and Windows Remote Management both already
had substantial coverage, but under their modern
`Microsoft-Windows-DHCP-Server` and `Microsoft-Windows-WinRM/
Operational` channels respectively, a genuinely different `log` value
from the classic System-log messages these two sources also still
emit.

Researched each real event ID via web search rather than from memory,
cross-checking multiple independent sources per event (Microsoft
Learn/TechNet, Microsoft Q&A, and long-standing community references
like Uwe Gradenegger's and syfuhs.net's KDC write-ups) the same way
this catalogue's own README describes its existing NSA/Microsoft
cross-checking passes - full citations are in each new row's
`reference` field. One deliberate exclusion caught during research:
Kerberos Event ID 4 (KRB_AP_ERR_MODIFIED) turned up repeatedly
alongside the Kerberos-Key-Distribution-Center events, but its real
source is `Microsoft-Windows-Security-Kerberos`, not
`Kerberos-Key-Distribution-Center` - left out rather than folded in
under the wrong source.

Added 20 new events: NETLOGON 5719/5722/5723/5805 (secure-channel
setup/authentication failures - 5723 and 5805 specifically about
failed authentication got MITRE T1110, Brute Force; 5719/5722 are
connectivity/config signals, left unmapped); LSA (LsaSrv) 40960/40961
(Kerberos negotiation failures); Kerberos-Key-Distribution-Center 11/
21/27/29 (duplicate SPN, invalid smart-card certificate - T1649,
Steal or Forge Authentication Certificates - missing key, and no
suitable KDC certificate); DistributedCOM 10016/10028/10029 (DCOM
permission denied - explicitly noted as usually benign/by-design per
Microsoft's own guidance, not per-event-alertable -, communication
failure, and server registration timeout); DHCP-Server 1035/1036/1046
(missing DHCP Users/Administrators groups at startup, and the server
determining it isn't authorized and stopping - flagged as a possible
rogue-DHCP-server signal, not just AD connectivity trouble);
Wininit 11 (AppInit_DLLs - MITRE T1546.010, Event Triggered Execution:
AppInit DLLs, and the one new event marked as an ACSC priority log);
and Windows Remote Management 10148/10149/10154 (WinRM listener
started/stopped - 10148 tagged T1021.006, Remote Services: Windows
Remote Management, and also marked ACSC priority given it's the
signal that a host has become remotely reachable - and SPN
registration failure).

Deliberately conservative on the `mitre_techniques`,
`acsc_priority_log`, and `nist_800_53_au` fields: only assigned where
there's a genuinely clean, hard-to-dispute fit (5 of the 20 new rows
got a MITRE technique; 2 got the ACSC flag; none got a NIST 800-53 AU
control, matching how sparingly that field is already used elsewhere
in this catalogue, e.g. on Service Control Manager's own 15 rows).
Everything else - the majority of this batch - is left unmapped
rather than stretched to fit, consistent with this catalogue's own
stated practice of leaving purely diagnostic/operational events
unmapped.

Both catalogue-normalized fields (`source: DHCP-Server`, matching this
catalogue's own existing label for the other DHCP-Server rows) and the
literal historical Event Viewer strings (`Source: DhcpServer` inside
the illustrative sample text) are represented - deliberately not the
same string in both places, so filtering/searching stays consistent
with the rest of the catalogue while the sample text stays true to
what a real admin would actually see logged.

Applied to all three places this catalogue's Windows Events data
lives: the vendored `windows/data/events.csv`/`events.json` (4,737 ->
4,757 rows) and the embedded `DATA.events` array in `index.html`
(4,893 -> 4,913 events; footer count corrected to match, having been
stale at 4,746 already before this change).

Verified: `node --check`. Confirmed via a direct parse of the served
page's embedded `DATA.events` (rather than the search UI, which is
unreliable here since Windows commonly reuses the same numeric event
ID across unrelated providers - e.g. searching "40961" alone also
matches an unrelated PowerShell event) that all 20 new rows exist
exactly once each, with the correct `log`/`source`/event ID
combination and a populated description. Spot-checked three detail
panels (5805, 1046, 10154) by screenshot - clean rendering, correct
field grid, sample text, and field schema, consistent with the rest
of the app. Confirmed the Log filter picks up the new
Kerberos-Key-Distribution-Center source. Regression-checked across
both themes and both 1500px/375px viewports, plus Linux Events'
unaffected 77-event count - zero console errors throughout.

`1.4.13` (PATCH - 20 additional events added to an already-existing
catalogue's data set; not a new catalogue, tab, or app-level
capability).

Added a first cross-catalogue gap-analysis pass, scoped narrowly on
purpose: how many of Threat Detection's own `required_log_source`
references line up with a Microsoft Events log channel. Not fuzzy
matching - a small hand-curated alias table built by comparing
Threat Detection's 4,017 detections (spread across 13 separate
`<script>` JSON blocks plus a 14th, differently-embedded ESXi family)
against Microsoft Events' own 197 distinct `log` values, matching
only where the correspondence was clear (Security/System channels,
PowerShell/Sysmon/DHCP-Server/GroupPolicy/DNS-Server/WinRM/
TerminalServices). Linux/AWS/Other Events matching, Event-ID-level
precision, and any automated fuzzy matching are all explicitly out of
scope for this pass.

Surfaced two ways: Microsoft Events' own Log filter now shows a small
detection-count badge next to any log channel with a match (e.g.
"9 det" next to PowerShell/Operational), and Threat Detection's Heat
Coverage page gained a "Data source coverage (Microsoft Events)"
section with matched-vs-total stat tiles and a top-10 list of the
most-referenced sources this pass didn't match, worded explicitly as
"no Microsoft Events match in this pass" rather than "uncatalogued",
since several of them (Dell iDRAC, HPE OneView) are in fact catalogued
elsewhere, under Other Events, just not checked against in this pass.

Both catalogues run in separate script closures with no shared scope
and no guaranteed run order, so rather than deriving the numbers live
at runtime, they're computed once offline against the current data and
embedded as two small static objects (`WIN_LOG_DETECTION_COVERAGE`,
`TD_DATASRC_COVERAGE`) - the same precomputed-and-embedded pattern
`aws_iam_actions.json` already uses elsewhere in this app.

Verified: `node --check`. Confirmed via Playwright that the Heat
Coverage stat tiles render the exact expected values, the gap list
renders all 10 entries, and the Microsoft Events Log filter shows the
new badge when searched down to a matched log channel (PowerShell) -
zero console errors in either check. Screenshots of both confirmed
clean layout with no overlap against the existing `.opt-count` badge
or the existing Heat Coverage matrix.

`1.4.14` (PATCH - a read-only coverage insight surfaced on two
already-existing pages; not a new catalogue, tab, or app-level
capability).

Added an Export button to Microsoft Events, mirroring Threat
Detection's own existing `#td-export-btn` (same "Export current
results as JSON" behavior, same Blob-download-and-toast mechanics) -
this app was the one catalogue tab that didn't already have one.
Placed at the end of the search-row toolbar, next to the existing
filter controls it exports the output of. Downloads exactly what
`filtered()` currently returns - honoring search text, the Log/
Category selections, and the ACSC/reference-link/publication toggles,
not the full 4,746-event catalogue - as
`microsoft-events-export.json`. A small `#win-toast` component was
added for the confirmation message ("Exported N events"), since this
app didn't have Threat Detection's toast component to reuse; styled
with this app's own `--ink`/`--bg` tokens rather than Threat
Detection's `--text`/`--bg`, consistent with each app keeping its own
scoped CSS tokens.

Verified: `node --check`. Confirmed via Playwright that searching down
to a subset (218 PowerShell-related events) and clicking Export
downloads a JSON file named `microsoft-events-export.json` containing
exactly those 218 events (not the full catalogue), and that the toast
reads "Exported 218 events". Regression-checked across both themes and
both 1500px/375px viewports - all 4,893 events still render, the
Export button stays visible and correctly placed at every size, zero
console errors throughout.

Before this shipped, extended the same Export control with a field
picker and a CSV option, since a fixed "every field, JSON only" export
doesn't suit every downstream use (a quick spreadsheet import of a few
columns vs. a full re-import of every field). The plain button became
a combobox - the same `.combo`/`.combo-panel` pattern already used for
the Log/Category filters right next to it - opening a panel with a
JSON/CSV format toggle and a checklist of this catalogue's 18 exportable
fields (Event ID, Log, Source, Category, Subcategory, Description,
ACSC priority log, Reference, How to collect, MITRE ATT&CK techniques,
AD compromise techniques, NIST 800-53, Splunk CIM mapping, Group
Policy path, Opposite event ID, Sample log text, Sample type, Field
schema), all selected by default so the export is unchanged unless a
field is deselected. "All"/"None" buttons in the panel footer match
the existing Log/Category combos' own footer pattern; the footer note
between them tracks the live "N of 18 fields" count. CSV output is
hand-rolled (comma/quote/newline-safe cell escaping, `\r\n` line
endings) rather than pulling in a library, matching the general
lightweight-dependency posture of this vendored, offline-first app.

Verified: `node --check`. Confirmed via Playwright that deselecting to
a 3-field subset (Event ID, Log, Description), filtering to the same
218 PowerShell-related events, and exporting as CSV downloads
`microsoft-events-export.csv` with exactly that 3-column header, 218
data rows, and a toast reading "Exported 218 events · 3 fields · CSV";
that re-selecting all 18 fields and switching to JSON downloads
`microsoft-events-export.json` with all 18 keys present; and that the
export panel opens, closes on an outside click, and stays fully
on-screen (no horizontal overflow) at 375px width. Regression-checked
across both themes and both 1500px/375px viewports - zero console
errors throughout.

`1.4.15` (PATCH - a field/format picker added to an export control
shipped in this same version; not a new catalogue, tab, or app-level
capability).

Given an uploaded `bash-history-siem.md` guide (PROMPT_COMMAND +
syslog for real-time, timestamped, system-wide Bash history capture;
auditd as a "stronger, harder to bypass" complementary layer; Bash
4.4+'s own `syslog_history` builtin; a hardening/comparison table;
forwarding to a SIEM via rsyslog UDP/TCP/TLS or Filebeat/Auditbeat)
and asked where in Linux Events it best belongs. Checked first rather
than assuming: none of the three existing content shapes fit it. The
per-event `audit_configuration` config cards are one card per
subcategory, a couple of sentences pointing at one `auditctl` rule -
too terse for a multi-method guide, and wrong anyway, since the
guide's own recommended approach isn't auditd at all (PROMPT_COMMAND
is the primary method, auditd only the complementary "stronger
option"). The `auditd_man_pages`/`fapolicyd_man_pages` shape (`{command,
purpose, sections, notes}`, rendered as titled reference sections) is
structurally the right fit, but both existing instances of it live
*inside* the Auditd Rules and Fapolicyd tabs specifically, scoped to
those subsystems' own commands - and this guide's own primary method
being Bash-native, not that either subsystem. A raw `logger -t
"bash-history"` tag also isn't a real vendor-assigned identifier the
way `audit/*` type codes or systemd `MESSAGE_ID`s are, so it couldn't
become an `events.csv` row without breaking this catalogue's own
"real, verifiable identifiers only" rule for what counts as a
catalogued event.

Added a new top-level "Command Logging" tab, sibling to Events/Auditd
Rules/Fapolicyd/Reference tables/Companion Tools, reusing the man-page
shape and its existing list/detail rendering (`auditdCmdSectionsHtml`
is called directly - no new rendering code, just a second list/detail
pair and a new `command_logging_guides` DATA array) rather than
inventing a new content model for one document. The guide's own
sections became eight titled reference blocks (Recommended approach,
rsyslog configuration, example log line, the auditd option, the
Bash 4.4+ builtin, hardening notes, a quick test, and a method-
comparison table), transcribed rather than summarized so the exact
commands/config stay copy-pasteable.

Verified: `node --check`. Confirmed via Playwright that the new tab
button exists, activates its panel, lists the one guide with a correct
section count, and that its detail view renders all eight sections
plus Notes/Source with no code-block overflow at either 1500px or
375px, in both themes. Confirmed search matches on content inside a
section (e.g. "syslog_history") and shows the correct empty state for
a non-matching query. Regression-checked Linux Events' own 77-event
list and Microsoft Events' 4,913-event list - both unaffected, zero
console errors throughout.

`1.5.0` (MINOR - a whole new tab inside Linux Events; squarely the
"new tab" case this repo's own versioning policy reserves MINOR for).

Given a second pasted table of candidate Microsoft Events System-log
event IDs for the same seven sources as `1.4.13` (NETLOGON, LSA
(LsaSrv), Kerberos-Key-Distribution-Center, DistributedCOM,
DHCP-Server, Wininit, Windows Remote Management) and asked to add
them. Verified every one independently rather than transcribing the
table as given - it turned out to need real correction, not just
citation. Two categories of problem surfaced:

**Wrong source/log entirely**, so excluded rather than added: three
Wininit rows (12, 13, 1074) are documented under Kernel-General and
User32 respectively, not Wininit, matching this repo's own earlier
exclusion of 1074 for the same reason; four Windows Remote Management
rows (6, 91, 169, 142) belong to the `Microsoft-Windows-WinRM/
Operational` channel already covered by this catalogue's other 166
rows, not the classic System log; a DHCP-Server 1000 turned out to be
an Application-log crash record for `dhcpssvc.dll`, not a System-log
service event; a DistributedCOM 10009 is the pre-Server-2012 event ID
for the exact same message already covered under 10028, not a
distinct event; and a Kerberos-Key-Distribution-Center 26 couldn't be
corroborated distinctly enough from event 14 across sources to trust
(both are described almost identically across secondary write-ups) -
left out rather than guessed.

**Two already-merged rows turned out to be mislabeled**, caught while
cross-checking the table's claims against the same primary sources:
Kerberos-Key-Distribution-Center 27's sample text was actually event
14's message (both are "did not have a suitable key" wording,
differing only in AS vs. TGS phrasing and whether etypes are listed -
an easy mix-up, and exactly the kind of error this second pass was
supposed to catch); DistributedCOM 10029's sample text was actually
event 10010's ("did not register with DCOM within timeout" vs.
10029's real "timed out waiting for a service to stop" meaning).
Both corrected in place rather than left standing alongside the new,
correctly-labeled rows for the same event family.

Added 24 new events across six sources (Service Control Manager
again needed nothing, unchanged from the last pass): NETLOGON 5781/
2114 (DNS registration failure, legacy service-startup failure); LSA
(LsaSrv) 5000/6037/6038/6155/40970 (security-package exception, SPN/
loopback-check warning, NTLM-in-use detection, Credential Guard
package-signature warning, and a January 2022-hardening Kerberos-to-
NTLM downgrade block); Kerberos-Key-Distribution-Center 7/14/16/35/
37/42/45 (SAM request failure, the AS/TGS "no key intersection" pair,
the CVE-2021-42287 PAC-hardening pair, weak/RC4 keys, and the CVE-
2025-26647 NTAuth-store certificate check); DistributedCOM 10006/
10010/10015/10036/10037/10038 (an activation HRESULT error, the
correctly-relabeled registration timeout, a Remote Launch permission
denial, and the KB5004442/CVE-2021-26414 authentication-hardening
trio); and DHCP-Server 1001/1002/1003/1004 (the four-stage Service
Controller/global-parameters/registry-parameters/database startup
sequence).

MITRE mapping stayed as selective as last time, applied only where a
CVE or attack technique is directly named in the sourcing rather than
inferred: T1558 on the two PAC-hardening events (CVE-2021-42287 is
specifically about Kerberos ticket/PAC forgery), T1558.003 on the
weak-RC4-keys event (the precise condition that makes an account
Kerberoastable), T1649 on the NTAuth-store event (matching the
existing event 21's precedent for certificate-based auth abuse), and
T1557 on the three DCOM authentication-hardening events (CVE-2021-
26414 is an NTLM-relay-via-DCOM vulnerability). Twelve of the 24 got
no mapping at all, left blank rather than stretched.

Applied to all three places this catalogue's Windows Events data
lives: `windows/data/events.csv`/`events.json` (4,757 -> 4,781 rows,
including the 2 corrected in place) and the embedded `DATA.events`
array in `index.html` (4,913 -> 4,937 events; footer count corrected
to match).

Verified: `node --check`. Confirmed via a direct parse of the served
page's embedded `DATA.events` that all 24 new rows exist exactly once
each with the correct `log`/`source`/event ID and a populated
description; that all ten excluded candidates (the three Wininit, four
WinRM, DHCP 1000, Kerberos 26, DCOM 10009) are correctly absent under
these sources; and that both corrected rows now carry their real
message text. Screenshotted three detail panels (the corrected KDC 27,
the new Kerberoasting-relevant KDC 42, and the corrected DCOM 10029) -
clean rendering, MITRE tags visible where set. Regression-checked
across both themes and both 1500px/375px viewports, plus Linux
Events' unaffected 77-event count - zero console errors throughout.

`1.5.1` (PATCH - 24 additional events plus 2 corrections to an
already-existing catalogue's data set; not a new catalogue, tab, or
app-level capability).

Given an owner-supplied reference CSV of Microsoft-Windows-DHCP-Server
event IDs - 148 rows spanning six channels (Operational, Admin,
System, DNS, Audit, Filter) - and asked to reconcile it against this
catalogue's existing DHCP-Server coverage. Cross-checking first: the
CSV's own "Admin" channel turned out to independently corroborate the
catalogue's pre-existing classic-System-log DHCP-Server rows (20291/
20292 among them) - identical message text under a channel label the
CSV assigns on its own, strong confirmation those rows were already
correct. That check also surfaced a real gap: the bulk of the CSV's
Operational-channel family (plus the remaining Admin, System, DNS,
Audit, and Filter rows) had no equivalent in the catalogue at all,
since prior passes had only ever added the classic-System-log side of
DHCP-Server. Presented the choice between a small Admin-channel-only
addition and the full Operational-family catch-up; asked for the
fuller option.

Parsed the CSV directly rather than retyping it, to keep the mapping
mechanical instead of hand-transcribed. Two existing conventions
governed where each row landed: seven Admin-channel rows (1000, 1007-
1011, 1056) describe service lifecycle events - startup, shutdown,
cleanup - matching the numbering scheme of the catalogue's existing
classic-System-log DHCP-Server bucket (`log="System"`), so they went
there, each given its own correct level and subcategory rather than a
uniform "Error"/"startup" label (1008-1010 are shutdown-path events,
1011 is a routine runtime NACK, not an error). Everything else -
Operational, the remaining Admin rows, System, DNS, Audit, and Filter
- landed in the catalogue's other existing DHCP-Server bucket
(`log="Microsoft-Windows-DHCP-Server"`), which the data already
collapses across channels rather than fragmenting by channel (an
existing-row precedent confirmed before following it); the per-row
channel is preserved instead in each new row's illustrative sample
text `Log Name:` line, which does vary by channel. Twenty-two
already-covered Operational-bucket event IDs and the seven
already-covered classic-System-log ones were skipped rather than
duplicated.

Matched two more existing field conventions for this event family
exactly: `description` keeps the message template's `%N` tokens as
literal "xxx" placeholders (as the pre-existing rows do), while
`sample` gets a realistic, context-aware substitution - built via a
rule table keyed to the phrase immediately preceding each placeholder
(a scope name, a MAC address, a lease duration, a failover partner,
and so on) rather than a single generic filler, so the illustrative
text reads the way a real event would.

Added 134 new rows: 127 to the `Microsoft-Windows-DHCP-Server`
Operational-family bucket (covering NAP policy events, MAC-address
filtering/allow-deny lists, failover-relationship state changes,
DNS-registration failures, stateless-client inventory, superscope and
multicast-scope lifecycle events, and PBA policy-condition changes,
among others) and 7 to the classic-System-log bucket (service
startup/shutdown lifecycle). Applied to all three places this
catalogue's Windows Events data lives: `windows/data/events.csv`/
`events.json` (4,781 -> 4,915 rows) and the embedded `DATA.events`
array in `index.html` (4,937 -> 5,071 events; footer count corrected
to match).

Verified: `node --check`. Confirmed via a direct parse of the served
page's embedded `DATA.events` that both new buckets are duplicate-free
internally, that the total event count matches, and spot-checked nine
specific event IDs (NAP, MAC filtering, failover, and classic-System-
log entries among them) for the correct log/description/subcategory.
Screenshotted four detail panels (a NAP event, a Filter-channel event,
a DNS-channel event, and a classic-System-log startup event) - clean
rendering, channel-correct `Log Name:`/`Level:` lines in each sample.
Regression-checked across both themes and both 1500px/375px
viewports, plus Linux Events' unaffected 77-event count - zero
console errors throughout.

`1.5.2` (PATCH - 134 additional events extending an already-existing
catalogue's data set, plus a bucket/channel-mapping reconciliation
against an authoritative reference; not a new catalogue, tab, or
app-level capability).

Given an owner-supplied reference CSV of Microsoft-Windows-DNS-Server-
Service event IDs - 233 rows across three channels (DNS Server, Audit,
Analytical) - and asked to reconcile it against this catalogue's
existing DNS-Server-side coverage. That coverage turned out to be
almost entirely absent: prior work had only ever covered the DNS
*client* side (163 rows across `Microsoft-Windows-DNS-Client` and
related logs) plus a thin 11-row sliver of the server's own Analytical
channel - the classic "DNS Server" log and the newer Audit channel had
no coverage at all.

The CSV itself split into two very different buckets. The 66 Audit-
channel rows and 7 new Analytical rows (DNS-over-HTTPS lookup events,
597-603) carried real, specific message-table text - clean, mechanical
additions matching this catalogue's established CSV-to-row conventions.
But 127 of the 154 "DNS Server"-channel rows had only generic
category-level filler ("Configuration related event.", "AD integration
related error.", etc.) with no real message text at all. Presented the
choice between a quick pass (skip the 127) and a fuller pass (research
each one's real wording individually); asked for the fuller option.

Dispatched four parallel research passes - one per event-ID group (AD
Integration; Zone Data/Transfer/Root Hints; and two roughly-equal
splits of the remaining Configuration/Service Status events) - each
independently searching for the real Windows message-table text rather
than trusting the CSV's filler, consistent with this catalogue's
standing verification discipline. 117 of the 127 came back with a
real, sourced message; the other 10 were excluded rather than guessed,
either because no verifiable text could be found at all, or (one case)
because the only text found was close enough to a sibling event's own
confirmed wording that publishing it risked misattributing the wrong
event's message. One of the four passes found strong primary sourcing
for its entire group - a mirrored WS2008R2 provider-manifest XML
extracted directly from `dns.exe`'s own resource strings - which also
caught a real accuracy problem in the vendor CSV: 15 of its 26 "AD
Integration"-category events are marked Error in the CSV but are
actually Warning or Informational in the DNS server's own manifest;
the corrected, real severities were used instead of the CSV's claim.

Two more existing conventions carried over unchanged from the prior
DHCP-Server-Operational pass: `description` keeps `%N` tokens as
literal "xxx" placeholders, while `sample` gets a realistic,
context-aware substitution built from a rule table keyed to each
placeholder's preceding phrase - extended here with DNS-specific
labels (zone name, RDATA, TTL, directory partition, registry
parameter, and so on) and a couple of ordering fixes so a value chosen
for one placeholder in a message doesn't get reused verbatim for a
different placeholder in the same message.

Added 215 new rows in total: 66 Audit-channel, 17 Analytical (7 new
DoH events; the pre-existing 10-row sliver untouched), and 132 to the
classic "DNS Server" log (25 with real CSV text, 107 from the
independent research pass). Category is `f"DNS Server {csv_category}"`,
matching this catalogue's own existing precedent (row 6001's category
was already literally "DNS Server Zone Transfer" before this batch).
Applied to all three places this catalogue's Windows Events data
lives: `windows/data/events.csv`/`events.json` (5,013 -> 5,130 rows)
and the embedded `DATA.events` array in `index.html` (5,169 -> 5,286
events; footer count corrected to match).

Verified: `node --check`. Confirmed via a direct parse of the served
page's embedded `DATA.events` that the 226 total DNS-Server-Service
rows across all four log buckets are duplicate-free, and spot-checked
seven event IDs including the corrected-severity 4013 (confirmed
`Level: Warning`, not the CSV's claimed Error) and one of the fuller-
pass's zone-transfer events. Screenshotted four detail panels (an AD
Integration event, a DoH Analytical event, an Audit zone-update event
with a multi-placeholder sample, and a classic-log Configuration
event) - clean rendering in all four. Regression-checked across both
themes and both 1500px/375px viewports, plus Linux Events' unaffected
77-event count - zero console errors throughout.

(Separately, this pass surfaced a pre-existing data-sync gap unrelated
to DNS: 128 (log, event_id) pairs exist in `index.html`'s embedded
`DATA.events` with no matching row in `windows/data/events.csv`/
`events.json`, predating this session's work. Left as-is - out of
scope for this batch - and flagged for a future pass.)

`1.5.3` (PATCH - 215 additional events extending an already-existing
catalogue's data set; not a new catalogue, tab, or app-level
capability).

Given three more owner-supplied reference CSVs in one pass - Certificate
Services (60 rows), Kerberos (27 rows), and Group Policy (61 rows) - and
asked to reconcile each against the existing catalogue. Checked every
candidate's exact `(log, source, event_id)` combination against the
existing data before touching anything, rather than assuming an upload
implied a gap: this turned out to be mostly a verification pass, not a
data-addition one.

**Group Policy**: 60 of 61 rows already existed exactly as given. The
one gap, event 5000, could not be safely filled - this source's
existing rows all cite "a full Windows Server 2019 ETW event manifest
export" as their reference, a stronger sourcing claim than a plausible
guess should be added under, and no independent source reproduced
event 5000's real text - left out.

**Kerberos**: the seven Security-log audit events (4768-4773, 4820)
and nine of the twenty `Kerberos-Key-Distribution-Center` (System log)
events were already covered from two earlier passes (`1.4.13`,
`1.5.1`). Of the eleven remaining, independently verified nine as
genuine, distinct events (smart-card/PKINIT certificate availability,
S4U2Self access checks, KB5014754-era weak-certificate-mapping
warnings) and excluded two (24, 28) whose only available text was
generic filler with no independently-verifiable real wording. Event
26 needed particular care - the existing catalogue's own event 27
description already named 26 as "its AS-side counterpart," so this
was as much a confirmation of already-referenced-but-missing data as
a fresh addition; sourced and added as the genuine AS-side sibling to
27's TGS-side text, not confused with adjacent near-duplicate events
14/16/27 the way an earlier pass had to correct.

**Certificate Services**: all 33 Security-log audit events (4868-4900)
were already covered. The CSV's other 27 rows, however, revealed a
real gap: `Microsoft-Windows-CertificationAuthority` (the CA role's
own Application-log events, as opposed to the Security-log audit
trail) had exactly one existing row before this pass. Of the 27,
excluded event 90 (already covered by an existing row whose text
disagrees with both this CSV and independent web sourcing - a
three-way conflict not safely resolved here, so the standing entry
was left untouched rather than second-guessed) and three CA-key-
archival events (1006-1008) whose only search results kept
resurfacing an unrelated event family under a different source,
suggesting a numbering mismatch in the CSV rather than a real gap.
The remaining 23 were added; one (75, "Related CRL publication
failure" in the CSV) was reconstructed by direct analogy to three
already-confirmed siblings (65/66/74) rather than published as
filler, since its exact structural counterpart among those three
could be identified with confidence.

Matched this source's own existing convention rather than the CSV's
literal "Application" channel label: the catalogue's one pre-existing
`Microsoft-Windows-CertificationAuthority` row already used that same
string as its `log` value (not `Application`), so the new rows follow
suit to keep this source's data internally consistent.

Added 32 new rows total: 23 to `Microsoft-Windows-CertificationAuthority`
and 9 to `Kerberos-Key-Distribution-Center`. Applied to all three
places this catalogue's Windows Events data lives: `windows/data/
events.csv`/`events.json` (4,915 -> 4,947 rows) and the embedded
`DATA.events` array in `index.html` (5,071 -> 5,103 events; footer
count corrected to match).

Verified: `node --check`. Confirmed via a direct data-level diff
(not a text diff) between the pre- and post-batch `events.json` that
zero existing rows were missing or modified and exactly 32 were added,
and that both new sources' rows are internally duplicate-free.
Screenshotted three detail panels (a CertificationAuthority upgrade-
failure event, and two Kerberos-KDC PKINIT-certificate events) - clean
rendering. Regression-checked across both themes and both 1500px/
375px viewports, plus Linux Events' unaffected 77-event count - zero
console errors throughout.

`1.5.3` (PATCH - 32 additional events extending two already-existing
catalogue sources; not a new catalogue, tab, or app-level capability).

This batch and the DNS-Server-Service batch above were developed in
parallel on separate branches from the same `1.5.2` base, each
independently bumping to `1.5.3`; merging both together to resolve
that collision (concatenating each branch's own new rows onto the
common base in `events.csv`/`events.json`/`index.html`'s `DATA.events`,
rather than a line-level text merge, since both appended near the
same file locations) bumped once more to `1.5.4`.

`1.5.4` (PATCH - no new data of its own; resolves the parallel-branch
version collision between the two `1.5.3` batches above).

Asked where an owner-supplied 93-row CSV of RHEL log file locations
(paths like `/var/log/secure`, `/var/log/audit/audit.log`, plus a
handful of `journalctl -u <unit>` commands and one environment
variable for services with no flat log file) would best fit in Linux
Events. Recommended the Reference tables tab as a new standalone table
- the same shape as its existing `ssh_disconnect_codes`/`errno_codes`/
etc. tables, a static lookup rather than an event record, so it
doesn't belong in the main `events.csv` (strictly keyed by numeric/
UUID event ID) - and flagged two data-quality issues to fix before
publishing: literal duplicate rows re-citing an already-listed path,
and several rows that aren't plain files (a directory, a binary
accounting file, a journalctl-only service, an env var) mixed in
without saying so. Asked to go ahead and build it.

Cleaned up the source CSV mechanically rather than transcribing it:
merged 3 rows that just re-cited an already-listed path under a
second heading (`/var/log/maillog`, `/var/log/chrony/`,
`/var/log/anaconda/`) into their first occurrence; reconstructed 5
rows whose description contained an unquoted comma, which had
silently broken a naive CSV parse into extra columns (e.g. "Main
system log (general messages from kernel, daemons, etc.)" splitting
into 5 fields instead of 3 - caught by checking every row's actual
field count against the header rather than trusting `csv.DictReader`
to fail loudly, which it doesn't); and added a `type` column (`file`,
`directory`, `binary`, `glob`, `journal-unit`, `env-var`) so the
genuinely different kinds of location aren't all presented as plain
files. Kept the real near-duplicates as separate rows on purpose:
`/var/log/messages` appears four times (bare, plus "(dhcpd entries)",
"(named entries)", "(realmd entries)") because that's a true fact
about the shared classic syslog file - four unrelated subsystems'
lines land in it - not a repeated path.

Added `linux/data/reference/log_file_locations.csv`/`.json` (90 rows
after the merge), wired into `index.html` as the Reference tables
tab's 10th accordion table (`REF_TABLES` entry, static accordion
markup, and the underlying `DATA.log_file_locations` array), matching
every other reference table's search/jump-nav/badge-count behavior
exactly rather than needing any UI code of its own.

Verified: `node --check`. Confirmed via Playwright that the new table
renders all 90 rows, its jump-nav badge updates as filtered, and the
tab's shared global search finds matches inside it (e.g. "chrony"
correctly narrows to 5 rows). Regression-checked across both themes
and both 1500px/375px viewports, plus Windows Events' and Linux
Events' own unaffected counts - zero console errors throughout.

`1.5.5` (PATCH - one new reference table in an already-existing
catalogue; not a new catalogue, tab, or app-level capability).

Asked to add a link to `Splunk Pipeline Explorer` (a companion tool by
the same author, at `adamliq.github.io/Splunk-pipeline-explorer`) to
Linux Events' Companion Tools tab. The page itself wasn't reachable
(network egress blocked for that domain) and no description turned up
via search - rather than write one from a guess at what a tool named
"pipeline explorer" might do, asked for a one-line description; got
"Follow data from source acquisition to searchable buckets." Added as
a third row to `linux/data/reference/companion_tools.csv`/`.json` and
the embedded `DATA.companion_tools` in `index.html`, matching the
existing two entries' exact shape (`name`/`description`/`url`).

Verified: `node --check`. Confirmed via Playwright that the Companion
Tools tab renders all three cards with no layout issues, screenshotted
for visual confirmation - zero console errors.

`1.5.6` (PATCH - one new companion-tools link; not a new catalogue,
tab, or app-level capability).

Asked to update Companion Tools to note that the Windows Event
Catalogue, Threat Detection Library, and Linux Event Catalogue - the
three source repos this compendium was merged from - have moved into
Cat Scan. Replaced the existing `Winevent-catalogue` row (which still
pointed out to the old standalone repo) and added two more, one per
source repo, each linking back to `github.com/adamliq/catscan` and
naming the tab that repo's content now lives under (Microsoft Events,
Threat Detection, Linux Events respectively), rather than a repo URL
that no longer reflects where the content actually is. The two
genuinely external Splunk tool links were left unchanged. Applied to
`linux/data/reference/companion_tools.csv`/`.json` (now 5 rows) and
the embedded `DATA.companion_tools` in `index.html`.

Verified: `node --check`. Confirmed via Playwright that the Companion
Tools tab renders all five cards with correct text and links,
screenshotted for visual confirmation - zero console errors.

`1.5.7` (PATCH - three companion-tools entries updated/added to point
at this merged project instead of the superseded standalone repos; not
a new catalogue, tab, or app-level capability).

Asked to move the RHEL log file locations table out of the Reference
tables accordion into its own top-level tab next to Command Logging,
and to add a second owner-supplied list of IdM/FreeIPA-specific log
locations, deconflicted against the existing 90 rows rather than
appended blind.

Of the 12 candidate IdM rows, 6 were paths already covered (the httpd
access/error logs, the `dirsrv` glob trio, `krb5kdc.log`/
`kadmind.log`, `/var/log/sssd/`, `/var/log/messages`) - skipped as new
rows, with 3 of those existing rows' descriptions enriched with the
genuinely new IdM-specific context the list added (that Apache also
serves the Web UI and XML-RPC/JSON-RPC API; that `/var/log/messages`
also carries some DNS/PKI subsystem messages in an IdM deployment)
rather than silently dropped. The remaining 7 were real additions: a
new `IdM / FreeIPA` category for the three `ipa-*-install.log` files,
the per-user `~/.ipa/log/cli.log`, and Custodia's log directory; a new
`PKI / Certificate System` category for `/var/log/pki/pki-tomcat/`;
and a `System`-category row for `/etc/logrotate.d/` (the rotation-
policy config directory, not a log location itself - noted as such
rather than miscategorized as one).

Moved the table's UI out of the Reference tables accordion (now back
down to 9 tables) into its own top-level **Log File Locations** tab,
positioned right after Command Logging: a single search box over a
`buildTable()`-rendered table, reusing the exact same rendering
helper the accordion version used, just without the accordion
wrapper, badge, or shared cross-table search. In the same pass, fixed
two pre-existing documentation gaps this touched directly: the "five
tabs" web-lookup count had been stale since the Command Logging tab
was added, and Command Logging itself had never gotten a tab
description in this README at all.

Verified: a full page syntax check. Confirmed via Playwright that the
new tab renders all 97 rows in the right position in the tab bar, its
own search works (e.g. "IdM" correctly narrows to 11 matches across
the new rows and the enriched/already-IdM-flagged existing ones), and
that the table is fully gone from the Reference tables accordion
(`#lnx-sec-log-files` no longer exists). Screenshotted the new tab.
Regression-checked across both themes and both 1500px/375px
viewports, plus Windows Events' and Linux Events' own main-catalogue
counts - zero console errors throughout.

`1.5.9` (PATCH - moved one reference table to its own tab and added
IdM/FreeIPA log locations to it; not a new catalogue or app-level
capability. Deliberately skips `1.5.8`: this branch and the build-
script/CI/data-reconciliation batch documented in a separate PR both
branch from this same `1.5.7`, and picking a version one step further
ahead avoids repeating the `1.5.2`/`1.5.3` collision from earlier in
this project's history, even though the two PRs will likely still
need an ordinary merge-conflict resolution where they touch the same
lines of this file).

Added the Ansible Automation Platform (AWX/Tower) side of the Log
File Locations table, from an owner-supplied component-level
breakdown of `/var/log/tower/` and `/var/log/supervisor/`.
Deconflicted rather than appended blind: 4 of the 14 supplied rows
were paths already in the table (`tower.log`, `callback_receiver.log`,
`dispatcher.log`, `job_lifecycle.log`) and had their descriptions
enriched with the specific component names the new list supplied
(Automation Controller, Callback Receiver, Dispatcher, Job Lifecycle)
rather than duplicated as new rows. The other 10 were genuinely new
`Ansible AAP` rows: 7 more files under `/var/log/tower/`
(`management_playbooks.log`, `task_system.log`, `rsyslog.err`,
`wsrelay.log`, `rsyslog_configurer.log`, `cache_clear.log`,
`tower_rbac_migrations.log`) and 3 under `/var/log/supervisor/`
(`awx-callback-receiver.log`, `awx-daphne.log`, and a `glob`-typed
`awx-*.log` for the remaining supervisord-managed service logs).
Kept the table's existing four-column schema rather than adding a
"Component" column for the source table's per-file component names -
those are folded into each row's `description` prose instead, so
every row across the whole table stays structurally uniform. Table
is now 107 rows (up from 97).

Verified: a full page syntax check. Re-synced `index.html`'s embedded
copy from `linux/data/reference/log_file_locations.json` and
confirmed via Playwright that the Log File Locations tab renders all
107 rows, that a "tower" search correctly narrows to the 12 rows
under `/var/log/tower/` (including the enriched originals) and an
"awx" search to the 4 supervisor-managed rows, and that the enriched
descriptions render with the new component names. Regression-checked
across both themes and both 1500px/375px viewports, plus Windows
Events' and Linux Events' own main-catalogue counts - zero console
errors throughout.

`1.5.10` (PATCH - added Ansible Automation Platform log file
locations to the Log File Locations tab; a data addition and
deconfliction to an existing reference table, not a new capability).

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
  SD-WAN devices), `data/cisco_sdwan_logging_reference.json` (a
  comprehensive Cisco Catalyst SD-WAN logging reference — local log
  files, syslog formats, two severity scales, per-module syslog
  messages, alarms/events, audit logs — rather than a single log-type
  catalog), and `data/idrac_syslog_schema.json` (a Dell iDRAC remote
  syslog schema covering iDRAC8/9/10 — alert categories, message ID
  prefixes, transport/envelope details, and the Redfish message
  registry's own field schema, with the source's own `verified` flag
  on each alert category rather than one compiled confidence rating).
  No
  build tooling here, unlike `aws/`: all eight JSON files are used
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
`other/data/cisco_ios_xe_logging_reference.json`,
`other/data/cisco_sdwan_logging_reference.json`, or
`other/data/idrac_syslog_schema.json`), then regenerate
`index.html`. Adding a genuinely new vendor follows the pattern
FortiManager, Juniper EX-series, DDI Infoblox, Zscaler, Cisco IOS XE,
Cisco SD-WAN, and Dell iDRAC each set inside `build_app_other()` (not a
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
