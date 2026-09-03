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
data export rather than merged from an external source repo.

## Web lookup

`index.html` is a single, self-contained page (no build step, one runtime
fetch — see below) — open it directly in a browser. A menu bar at the top
switches between **Microsoft Events**, **AWS Events**, **Linux Events**,
**Threat Detection**, and **Search**; Microsoft Events, Linux Events, and
Threat Detection are the exact lookup tool from their source repo (search,
filters, detail views, reference tables, and so on), running independently
side by side on the same page. AWS Events is this repo's own Action
Explorer, built to match that same look and feel (see below). Your
last-chosen tab is remembered (`localStorage`) across visits.

All four catalogue tabs cap their page width the same way —
`max-width: min(1600px, 94vw)` — so every tab fills a wide screen instead
of sitting in a narrow column with unused margin either side; on anything
narrower than ~1700px the `94vw` term takes over and the page just fills
the viewport as before.

A **light/dark toggle** at the right of the menu bar switches the whole
page — the menu bar and Search pill, plus all four embedded apps — between
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
the same hue. AWS Events is new rather than merged from an existing app,
so its own palette (a blue accent, distinct from the other three tabs'
amber/teal/red) was checked the same way from the start instead of
retrofitted.

**Search** is a fifth, shell-only pill: a single box that searches
Windows events, AWS IAM actions, Linux events, and every Threat Detection
entry (detections and validations) at once, grouped by source with up to
40 results per source. A **Sources** filter row toggles Microsoft
Events/AWS Events/Linux Events/Threat Detection in or out of the results,
and a **Threat Detection type** row (only meaningful when that source is
on) separately toggles Detections and Validations — both default to
everything on. It's a thin layer on top of the four apps, not a fifth
schema — each app exposes a small `{items, open}` index (id, title, a
short meta line, and a lowercased haystack of its own already-existing
fields) on `window.__compHub` for this to search over; clicking a result
switches to that catalogue's own tab and calls back into its own existing
selection/detail-opening code (`jumpToEvent`-style for Windows/Linux,
`openDetail`/`openValidationDetail` for Threat Detection, opening the
Action Explorer's own detail modal for AWS Events) to actually show it
there — so results render exactly like they do from that app's own
search, because they *are* that app's own render path. AWS Events
registers itself on `window.__compHub` only once its data has finished
loading (see below), so a search fired in the instant before that finishes
just won't have AWS results yet.

The four catalogues are **not** merged at the data level: they keep their
own ID schemes, column schemas, and reference tables exactly as authored
(Microsoft Events, Linux Events, and Threat Detection in their source
repos — see each repo's README for the full field reference; AWS Events in
[`Events_Other/aws_iam_actions_expanded.csv`](Events_Other/README.md), via
[`aws/`](aws/README.md)). This page only merges the *presentation* — one
URL, one menu — not the underlying schemas.

Two tabs fetch their data at runtime instead of embedding it inline, so
this page isn't fully "no external requests": the Threat Detection tab's
**Heat Coverage** sub-tab fetches its eleven `mitre-attack-*.json` files
(from `threat-detection/data/`, see below), and the **AWS Events** tab
fetches its one `aws_iam_actions.json` file (from `aws/data/`, see below;
21,164 actions makes for a 6.5&nbsp;MB file, too large to comfortably
embed inline the way the other three catalogues' data is). Both degrade
gracefully under `file://` (browsers block `fetch()` of local files) with
an explanatory message — Heat Coverage the same way the source repo
already did, AWS Events the same way Heat Coverage does; serve the repo
over http(s) (GitHub Pages, `python3 -m http.server`, etc.) for those two
spots specifically. Everything else, including the other 4,017 detections
and every non-Heat-Coverage tab, works identically either way.

### How the merge was built

Three of the four catalogues arrive as source `index.html` files that
embed their app (styles, markup, data) in one file, and reuse a lot of the
same generic naming (`.panel`, `.card`, `.tab`, ids like
`search`/`list`/`detail`/`tabs`, etc.) — Winevent-catalogue and
linuxevent-catalogue deliberately share UI conventions, and
Threat-detection-library independently converges on the same common
patterns. Concatenating them naively would collide: matching CSS selectors
would bleed across apps, and shared `id="..."` values would make
`getElementById` return the wrong app's element. AWS Events is the fourth
— see its own paragraph below — but it's built directly into this repo
following the same conventions, so it participates in everything else
described here (the shared container-scoping pattern, the shared theme
toggle, `window.__compHub`) exactly like the other three.

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
  all four app containers at once, so Windows/Linux/AWS's existing (but,
  before this toggle existed, unreachable-without-changing-your-OS-theme)
  `:root[data-theme="…"]` CSS and Threat Detection's own become live
  together. Its click handler is the one place this repo reaches back into
  Threat-detection-library's own code: `td-theme-toggle`'s listener now
  tries `document.getElementById('shell-theme-toggle').click()` first
  (falling back to its original self-contained logic if that element is
  ever absent), so either button drives all four apps and stays
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

**AWS Events**, unlike the other three, has no source repo to namespace —
it's written directly under the `#app-aws` container id, so its markup,
`<style>` block, and script follow the same conventions the namespacing
step above produces for the others (own IIFE, own CSS custom properties
scoped to `#app-aws`/`#app-aws[data-theme="dark"]`, every query scoped to
its own container) rather than needing to be transformed into them. Its
data isn't embedded like Windows/Linux/Threat Detection's core catalogues
are, either: on load it `fetch()`es `aws/data/aws_iam_actions.json` (see
Structure), and only builds its stats tiles, service list, and search
table — and registers itself on `window.__compHub` for the shell Search
pill — once that resolves; the tab shows a loading message (and, under
`file://`, an explanatory error) until then, the same pattern Threat
Detection's own Heat Coverage tab already used for its runtime fetches.

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

Every app's script, and the merged file as a whole, was verified with
`node --check` and exercised end-to-end in headless Chromium (search,
filters, detail views, reference tables, combo boxes, the auditd/
fapolicyd subpanels, the Windows schema-explorer field modal, the Windows
Cloud Actions Explorer's own search/service-filter/sort/detail-modal
(independent of Schema explorer's), cross-link jump buttons, dark-mode
theming, the Threat Detection Heat Coverage matrix and Validations tab,
the AWS Events Action Explorer's own search/service-filter/sort/detail-
modal, cross-catalogue search finding and opening an AWS action, and
repeated tab-switching in every direction) to confirm none of the four
apps — or, here, none of two sub-tabs *within* the same app — leaks into
or interferes with the others.

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

These directories are kept for anyone who wants the raw data (e.g. to load
into Splunk, or to extend a catalogue — see each source repo's README for
how). `index.html` doesn't read from `windows/` or `linux/` at runtime
(each of those apps' data is already embedded in the page); it does read
from `threat-detection/data/` for the Heat Coverage fetches, and from
`aws/data/` for the AWS Events tab, both described above.

## Source repos

- [`Winevent-catalogue`](https://github.com/adamliq/Winevent-catalogue)
- [`linuxevent-catalogue`](https://github.com/adamliq/linuxevent-catalogue)
- [`Threat-detection-library`](https://github.com/adamliq/Threat-detection-library)

AWS Events has no separate source repo — it's maintained directly in this
one (see `Events_Other/` and `aws/` above).

To extend Microsoft Events, Linux Events, or Threat Detection, edit the
source repo the normal way, then regenerate this repo's `index.html` from
its updated `index.html` export. To extend AWS Events, update
`Events_Other/aws_iam_actions_expanded.csv`, run
`python3 aws/tools/build_aws_json.py`, then regenerate `index.html` the
same way.
