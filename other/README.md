# other/

Data for the **Other Events** tab in the top-level `index.html` — event
and log-type references for vendors outside the Microsoft/AWS/Linux/
Threat-Detection catalogues. Unlike those four, this isn't one schema:
each vendor keeps whatever shape its own documentation actually has
(FortiGate's log reference looks nothing like AWS's flat IAM-action
catalog, and the next vendor added here won't necessarily look like
either) rather than being forced into a common row shape. What *is*
shared across vendors is the visual language — rail + toolbar + table +
detail modal, a Log Types/Reference mode toggle where a vendor has
material that doesn't belong in a table (enable instructions, severity
levels, a common-fields glossary) — each vendor's own CSS/JS in
`index.html`, not literally shared classes across the `#app-win`/
`#app-aws`/etc. boundary the way `windows/`'s own Cloud Actions Explorer
reuses Schema explorer's classes (each top-level app here is its own
scoped CSS/JS island, same as AWS Events already is).

Only one vendor tab exists so far, so the vendor picker in the header is
a single always-active pill rather than a real selector — that's added
when a second vendor actually arrives, not built ahead of the need.

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
  against a specific build). Same runtime-fetch trade-off as AWS Events
  and Threat Detection's Heat Coverage tab: needs the page served over
  http(s), not opened as a local `file://`.

  Beyond the 40 per-subtype rows, the file also carries reference
  material that doesn't belong repeated on every row — 8 severity
  levels, 26 fields common to every log line, and the logging
  prerequisites paragraph — rendered in the tab's own Reference view
  rather than the per-subtype detail modal.

There's no build tool here (unlike `aws/tools/build_aws_json.py`) since
the JSON is used as delivered, not derived from another file in this
repo.
