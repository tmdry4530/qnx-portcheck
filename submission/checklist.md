# QNX Global Hackathon submission checklist: qnx-portcheck

Sources (fetched with curl, HTTP 200, 2026-11-15 12:29 KST):
- Official rules: https://qnx.devpost.com/rules
- Overview ("What to Submit"): https://qnx.devpost.com/

Submission repository: tmdry4530/qnx-portcheck. It was switched to public on 2026-11-21. A gitleaks secret scan was run before the switch (0 leaks). Unauthenticated `git ls-remote` confirmed public access on 2026-11-22.

Nothing has been joined, submitted or uploaded. All Devpost, YouTube and visibility steps are left for the user.

## Key dates (rules section 1, converted from Eastern Time to KST; EST = UTC-5)

| Event | Official (ET) | KST |
|---|---|---|
| Registration and submission opens | 2026-11-02 11:00 am | 2026-11-03 01:00 |
| **Submission deadline** | **2026-12-15 2:00 pm** | **2026-12-16 04:00** |
| Judging and public voting | 2027-01-15 10:00 am – 2027-01-29 5:00 pm | 2027-01-16 00:00 – 2027-01-30 07:00 |
| Winners announced (approx.) | 2027-02-04 2:00 pm | 2027-02-05 04:00 |

Internal target (expansion plan): code freeze 2026-12-11 18:00 KST, submit 2026-12-13.

## Required items

Status values: done / placeholder / missing / needs user.

| # | Requirement (rule wording, shortened) | Where it comes from | Status | Notes |
|---|---|---|---|---|
| 1 | Register: click "Join Hackathon"; create or log in to a Devpost account | Rules section 4 | **needs user** | Use the existing Devpost account (no new sign-up). COO must confirm the account interpretation first (see 20261115-expansion.md). |
| 2 | Eligibility: 18+; not resident in an excluded or sanctioned country; not a sponsor/Devpost employee or relative | Rules section 3 | **needs user** | South Korea is not on the listed exclusions; the entrant must confirm age and conflicts. If entering as a team, one Representative submits. |
| 3 | Project newly created Nov 2 – Dec 15, 2026 | Rules section 4, New & Existing | done | First commit `b068fe8` on 2026-11-15 11:57 KST. |
| 4 | Working project that runs on or targets QNX 8.0; host-based tools that build, test or analyze software for QNX 8.0 are allowed | Rules section 4, What to Create | done | Host tool (`scan`, `scaffold`, `lint-buildfile`). |
| 5 | Select one category | Rules section 4, Categories / Submission Requirements | needs user (on form) | **Developer Tooling & Host Tools**. |
| 6 | URL of a **public** code repository (GitHub/GitLab/Bitbucket) with all source code, assets and instructions | Submission Requirements | done | tmdry4530/qnx-portcheck was switched to public on 2026-11-21. Unauthenticated git ls-remote confirmed public access on 2026-11-22. |
| 7 | Open-source license file, detectable in the repo's About section | Submission Requirements | done | `LICENSE` (Apache-2.0 text) is in the repo root. Unauthenticated GET of https://github.com/tmdry4530/qnx-portcheck on 2026-11-22 returned HTTP 200. The About section shows the Apache-2.0 license, and "No description, website, or topics provided." |
| 8 | Repo must show the project "genuinely builds for or runs on QNX 8.0, not merely that QNX 8.0 is named in the README" | Submission Requirements | partial (host tool; not built with SDP or run on a target) | Host tool targeting QNX 8.0: see `docs/QNX80-EVIDENCE.md` (8.0-cited scan rules, qnx-ports-style `qnx/build/` scaffold, mkifs lint). Nothing has been built with the QNX SDP or run on a QNX target. |
| 9 | Build and run instructions stating QNX version, target (hardware or QEMU) and toolchain | Submission Requirements | done (with caveat) | README: QNX 8.0; host tool on Python >= 3.10; scaffolds target `nto-aarch64-le` / `nto-x86_64-o` and need QNX SDP 8.0 `qcc`, which was not used; no QNX target or QEMU run. |
| 10 | Text description of features and functionality | Submission Requirements | placeholder — `[VIDEO_URL]` still needs filling | Draft in `submission/devpost-en.md`. Evaluation numbers are taken only from `eval/RESULTS.md`, with the fresh split (15 projects) as the headline. |
| 11 | Evidence of QNX use: identify relevant files, functions and output | Evidence of QNX use | done | Section "How QNX is used" in `submission/devpost-en.md` lists files and functions. |
| 12 | Demo video: under 3 minutes; shows the project working on the device it was built for; **public on YouTube**; link on the form; no third-party trademarks or copyrighted music without permission | Submission Requirements | approved per Grok Bot, pending upload | Draft at demo/render/demo.mp4 (captions, no face or voice of the user). Grok Bot reported on 2026-11-15 that the user approved a **public** upload to the @gomang211 YouTube channel at 13:45 KST; Grok Bot uploads after code freeze (2026-12-11 18:00 KST) and QA. For a host tool, the "device" is the Linux host; footage cannot show a QNX target. Avoid logos and third-party music. |
| 13 | English materials (or English translations) | Language Requirements | done | README, tutorial and devpost copy are in English. |
| 14 | Free, unrestricted access for testing until judging ends (2027-01-29 5 pm ET / 2027-01-30 07:00 KST) | Testing | needs user | Keep the repo public and unchanged in license through 2027-01-30 KST. |
| 15 | Bonus, Best Codelab/Tutorial: URL of a tutorial written during the Submission Period about a task on or for QNX 8.0 | Submission Requirements / section 6 Bonus | placeholder | `docs/tutorial-port-linux-daemon-to-qnx8.md` exists (written 2026-11-15). Unauthenticated GET of https://github.com/tmdry4530/qnx-portcheck/blob/main/docs/tutorial-port-linux-daemon-to-qnx8.md on 2026-11-22 returned HTTP 200. Its own status box says the scan step and any target run were not verified. |
| 16 | Original work; open-source components used under their licenses; no IP violations | Submission ownership / Intellectual Property | done (review) | Third-party content: `tests/fixtures/buildfiles/eclipse-score/*` copied unmodified from eclipse-score/reference_integration at `f9156c2…`, with its Apache-2.0 LICENSE and NOTICE. Scaffold templates follow qnx-ports/build-files (no upstream license file); per `docs/scaffold-sources.md` no upstream prose is copied. Code written with Codex CLI under team direction. |
| 17 | Not developed with financial or preferential support from the Sponsor or Devpost | Financial or Preferential Support | done | None received. |
| 18 | Evaluation numbers referenced in README and description | Internal plan (not a rule) | done (README, devpost) | Filled from the REAL run in `eval/RESULTS.md` (scanner 5118669, harness 7df6c14): headline is the fresh split (15 projects); tune and seen-during-tuning numbers shown for comparison; SDL-excluded build recall labelled post-hoc. The demo scene template (`demo/`) still has its own `[EVAL_NUMBERS]` placeholder, filled at render time. |
| 19 | Submit on the "Enter a Submission" page before the deadline (drafts allowed; no edits after the deadline) | Rules sections 4 and 5 | **needs user** | Deadline 2026-12-16 04:00 KST. |
| 20 | Winner verification and tax forms (affidavit; W-8BEN for non-US residents) within 10 business days | Rules section 8 | needs user (only if winning) | Not a submission blocker. |

## Not required for this category
- Upstream project URL and PR URL: required only for Open-Source Contribution & Ports.
- "New repository, not a fork" rule: written for Open-Source Contribution & Ports; this repo is new anyway.

## Notes from the rules worth flagging
- The rules link free QNX SDP 8.0 access through QNX Everywhere (https://qnx.software/en/developers/get-started/qnx-everywhere).
  Getting it needs a new myQNX account, which our constraints forbid, so we did not use it.
- Judging criterion "Technological Implementation" asks whether the project "genuinely builds for or runs on QNX".
  Without SDP or target evidence, this is the main scoring risk for a host tool.
