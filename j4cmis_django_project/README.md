# J4CMIS — Justice for Children Management Information System

Django + Postgres implementation of the J4C MIS `J4C-MIS-Project-Summary.md`.

This scaffold was originally built from `erd.drawio`, which turned out to
be an older, superseded version (civil cases removed, 2-way case type, a
non-blocking global rule not in v4, and an invented 8-role permission
model). It was rebuilt from the SRS text itself once that was found. See
"Known divergence, now resolved" below.

## What's here

- `cases/models.py` — all 27 use cases' data requirements (FR-01 to FR-58)
  as Django models: Login/UserProfile, Child, Guardian, Case (with
  auto-generated Case Number and a CaseStatusHistory audit trail for
  FR-54/FR-57), Arrest, Classification (PF24/PF48), Social Inquiry Report,
  Victim Impact Assessment, Diversion Plan + monitoring updates, Referral
  Institution Progress, Child-Friendly Space, DPP/RSA Routing, Court
  Proceeding, Remand Placement, Document, Age Determination, Chain-Linked
  Activity + action points, Rehabilitation + progress reviews,
  Resettlement + follow-ups, Community Service, Legal Representation +
  documents, Training, Breastfeeding Mother + Accompanying Child, Suspect
  Parade, Facility Inspection.
- `cases/admin.py` — full admin registration for every model, so the
  system is usable for data entry immediately.
- `cases/views.py` — dashboard view with **region scoping enforced**
  (NFR-06: Regional Coordinators see only their region; National
  Coordinator / System Admin see everything).
- `cases/management/commands/bootstrap_roles.py` — creates the **exact
  three v4 roles** (System Administrator, National Coordinator, Regional
  Coordinator — FR-06), not an invented role list.
- `config/settings/` — split base/dev/prod settings, on-prem architecture
  (Django + Postgres + nginx, single box, per the separate Tayo
  conversation on infrastructure — that part of the plan is unaffected by
  the ERD/SRS mismatch).
- `DEPLOYMENT.md` — server setup, gunicorn + systemd, nginx, backups.

## Known divergence, now resolved

`erd.drawio` (the file first shared) is the pre-v4 "change-log applied"
version: it removes civil cases, uses a 2-value case type
(victim/juvenile_accused) instead of v4's 3-value case category (Child
Victim or Witness / Juvenile Accused / Vulnerable), and does not reflect
UC-26 (Legal Representation) or UC-27 (Victim Impact Assessment) as
separate tracked entities. `J4C-MIS-Project-Summary.md`, already in this
project folder, states v4 is the confirmed source of truth. This build
follows the SRS text (v2.2, v4-aligned) instead of the ERD.

**The ERD file itself was not updated** — if you use it for other
purposes (e.g. handing to another vendor), it should be regenerated from
this models.py or from the SRS directly so it doesn't silently reintroduce
the older, superseded rules.

## Design decisions worth knowing about

- **Case category** is `child_victim_or_witness | juvenile_accused |
  vulnerable` (FR-07), not victim/juvenile_accused.
- **Civil cases are in scope** (`Classification.offence_category` includes
  `civil`, FR-15).
- **Age range is 0–17**, never blocks submission — `Child.age_out_of_range`
  is set automatically on save (FR-12) and flagged, not rejected.
- **Case Number auto-generates** on first save as `J4C-<year>-<pk>`
  (FR-11) — the exact format isn't specified in the SRS beyond "unique,"
  so this is a placeholder convention. Confirm the format JLOS actually
  wants before go-live.
- **CaseStatusHistory** auto-records an entry on every Case creation and
  is meant to be appended to on every status change (FR-54, FR-57,
  NFR-09) — the view/admin layer needs a hook to append on every status
  transition, not just creation; only creation is wired up so far.
- **Region scoping** (NFR-06) is enforced in `cases/views.py` via
  `UserProfile.region`, not via Django Groups — Groups only control CRUD
  breadth, not row-level visibility. Any new view that lists cases must
  call `_scope_to_region()` or reimplement the same filter.
- **Multi-select fields described in prose** (e.g. UC-18 "participants and
  organisations," UC-26 "support provided," UC-21 "target institutions")
  are modeled as `TextField`/`CharField` free text rather than
  many-to-many tables, to keep v1 shippable. If reporting later needs to
  filter/count by individual value (e.g. "how many sessions targeted
  Police vs Judiciary"), these should become proper M2M relations —
  flagging this now rather than guessing which ones matter most.
- **UC-25 Community Service** detail is carried forward from v3 per SRS
  Section 8 item 10 ("v4 lists it in contents only... will be re-checked
  when v4 finalises it") — re-verify against v4 once JLOS finalises that
  section.

## Local development

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_roles
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the dashboard, `/admin/` for full CRUD.

## Production deployment

See `DEPLOYMENT.md`.

## Verified working (this scaffold, not just written)

- `python manage.py check` — 0 issues.
- `python manage.py makemigrations` — generates cleanly for all v4
  entities (39 models total), no circular-dependency or FK errors.
- `python manage.py migrate` against a live SQLite DB — every table
  created successfully.
- `bootstrap_roles` — creates exactly 3 groups (System Administrator,
  National Coordinator, Regional Coordinator) with role-scoped
  permissions — confirmed no stray roles from the earlier build remain.
- Confirmed via Django's test client, all HTTP 200: dashboard (`/`),
  admin index (`/admin/`), admin case list, admin Legal Representation
  list, admin Facility Inspection list.
- Confirmed on a real insert: `Case.case_number` auto-generates, a
  `CaseStatusHistory` row is created automatically, and
  `Child.age_out_of_range` correctly flips to `True` for an age outside
  0–17 (tested with age 25).

## What still needs your input

- **Cross-check against the 38 UI mockups in `ui/`** — I have not yet
  opened these. The SRS text describes fields in prose; the actual Visily
  mockups may show field groupings, dropdown option wording, or
  screen-splits (e.g. UC-02 is six separate screens: main, guardian,
  context, list, review, review-submit) that this single-form-per-model
  scaffold doesn't yet reflect. Share which screens matter most and I'll
  build matching Django form/template flows instead of relying on the
  generic admin.
- **CaseStatusHistory on every transition** — currently only fires on
  case creation; needs wiring into whichever views/serializers change
  `Case.status` going forward.
- **Case Number format** — confirmed only as "unique" in the SRS; the
  `J4C-<year>-<pk>` convention here is a placeholder pending JLOS
  confirmation.
- **API integration layer** (FR-52: ECCMIS, PROCAMIS, NIRA, Child
  Wellbeing IMS, ODPP) — not built. This scaffold has the DB fields
  (`DPPRouting.synced_from_dpp_api`) but no actual API client/endpoints
  yet.
- **Public portal** (FR-53) — not built; needs a separate read-only,
  aggregated-data-only view, deliberately excluding identifiable child
  data.
- **Reporting/analytics exports** (UC-15, UC-16, FR-36/37/58, PDF/Excel
  export) — not built; the dashboard here is a minimal internal view, not
  the reporting module.
- **Government server specs, Postgres provisioning, secrets** — see
  DEPLOYMENT.md, same open items as before (OS confirmation, managed vs
  on-box Postgres, real `.env` values, domain/HTTPS).
