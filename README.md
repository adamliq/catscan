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
any of the above — starting with FortiGate's 40 log types (see
[`other/`](other/README.md)) and built to hold more vendors over time,
each keeping its own schema shape rather than a forced common one.

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
entry (detections and validations), and FortiGate log types at once,
grouped by source with up to 40 results per source. A **Sources** filter
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
Action Explorer's own detail modal for AWS Events, the FortiGate log-type
detail modal for Other Events) to actually show it there — so results
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
[`aws/`](aws/README.md); Other Events in [`other/data/fortigate_log_reference.json`](other/README.md),
compiled from FortiOS's own documentation). This page only merges the
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
**Other Events** tab fetches `fortigate_log_reference.json` (from
`other/data/`, see below — a modest ~46&nbsp;KB on its own, but fetched
rather than embedded for consistency with the other two runtime-loaded
tabs and because Other Events is meant to grow more vendor files over
time). All three degrade gracefully under `file://` (browsers block
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
`aws/data/aws_iam_actions.json` and Other Events
`other/data/fortigate_log_reference.json` (see Structure), and only
builds its stats tiles, rail list, and search table — and registers
itself on `window.__compHub` for the shell Search pill — once that
resolves; each tab shows a loading message (and, under `file://`, an
explanatory error) until then, the same pattern Threat Detection's own
Heat Coverage tab already used for its runtime fetches.

**Other Events** is built to hold more than one vendor over time, so its
header carries a vendor picker — right now a single always-active
"FortiGate" pill, since a real selector isn't worth building for one
option; it becomes a real picker when a second vendor arrives, not ahead
of that need. FortiGate's own data has a shape no other tab's does — 40
log types (grouped `traffic`/`event`/`utm`) each with CLI/GUI instructions
for turning it on, an example raw log line, and its own field list, plus
material that doesn't belong repeated per row (8 severity levels, 26
fields common to every log line) — so on top of the familiar rail +
toolbar + table + detail-modal shell every other tab here uses, it adds a
second **Log Types / Reference** mode toggle (visually modeled on Schema
explorer's own Search/Explore toggle) to hold that shared material
separately instead of repeating it in every row's modal. This is the
shape the tab's own generic parts (container, theme wiring,
`window.__compHub` registration, rail/toolbar/table CSS) are meant to
carry forward for a second vendor without a rewrite; the parts specific
to *reading* a vendor's data — flattening FortiGate's `types` →
`subtypes` nesting into rows, rendering its enable/example/fields modal
sections — are written for FortiGate's own shape and are exactly what a
second vendor's own (likely differently-shaped) data would need its own
version of, rather than trying to force a one-size-fits-all row schema
ahead of seeing what a second vendor's data actually looks like.

(Also fixed while adding this tab: `.compendium-tabs` had no
`flex-wrap`, so six tabs no longer fit one row on narrow/mobile
viewports — the row silently overflowed and, worse, clicking a tab
scrolled to it, dragging the whole page into an unwanted page-level
horizontal scroll rather than the tab row just wrapping onto a second
line the way `.compendium-menu` itself already does. One-line fix,
verified by clicking Other Events at a 375px viewport and confirming the
page no longer scrolls sideways.)

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
tab — 3,670 operations across six Microsoft cloud audit/log schemas
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
search/service-filter/sort/detail-modal, the Other Events Log Types table
(all 40 FortiGate rows, its type-rail filter, and its own Log Types/
Reference toggle — severity levels, common fields, and sources all
rendering correctly), cross-catalogue search finding and opening both an
AWS action and a FortiGate log type, and repeated tab-switching in every
direction) to confirm none of the five apps — or, here, none of two
sub-tabs *within* the same app — leaks into or interferes with the
others.

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
  it — both idempotent, safe to re-run after either input changes.

  This enrichment isn't just a standalone data file anymore — Cloud
  Actions Explorer's own detail view shows it directly (provider/
  resource-type display names, API versions, region count, the four
  `supports_*` capability flags, and a same-resource-type "other
  operations here" cross-reference computed from the tab's own already-
  embedded data) on whichever of its 1,868 matched rows you open, one
  more reason to keep it and `MicrosoftCloud_Schema.json` in sync:
  Winevent-catalogue's own `index.html` embeds this exact enriched
  array, copied over each time it's regenerated the normal way (see
  Winevent-catalogue's own README for how that embedding works).

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
- `other/` — data for the Other Events tab: `data/fortigate_log_reference.json`
  (fetched by `index.html` at runtime; compiled from FortiOS's own
  documentation, kept exactly as compiled rather than reshaped — see its
  own `README.md`). No build tooling here, unlike `aws/`: the JSON is used
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
same way. To extend Other Events, either update
`other/data/fortigate_log_reference.json` in place (for FortiGate) or add
a new vendor's own data file, both followed by regenerating `index.html`;
a genuinely new vendor also needs its own small `build_app_*`-style
addition to the merge script's `main()` (own container id, own rail/
toolbar/table CSS, own data-shape-specific rendering) — see `other/`'s own
README for why that part isn't generic across vendors.
