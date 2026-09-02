# Events_Other

Raw reference data that doesn't belong to any of the three merged
catalogues (Windows, Linux, Threat Detection) — kept here for now rather
than left out of the repo, without being wired into `index.html`.

- `aws_iam_actions_expanded.csv` — 21,159 rows, one per AWS IAM
  action across 455 services (`service`, `action`, `AWS Service`,
  `Description`, `Resource type (console)`, `resources.type`). Where an
  action has a corresponding CloudTrail event, `eventType`,
  `eventCategory`, and `eventName` are also populated (5,254 of the
  21,159 rows).

Not read by `index.html` and not part of the Windows/Linux/Threat
Detection lookup tools — this is a holding area for source data, the same
way `windows/`, `linux/`, and `threat-detection/` hold each catalogue's
raw data.
