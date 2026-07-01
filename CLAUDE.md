# Watchtower — Project Guide

## Purpose

Watchtower is a lightweight home-lab security monitor (mini-SOC). It ingests Pi-hole DNS logs, triages events with an LLM, enriches suspicious findings against threat-intel APIs, and alerts via phone push — all running on a Raspberry Pi.

The system is **advisory-only**: it surfaces threats for human decision, never auto-blocks DNS. This is both a safety property and a deliberate design choice that demonstrates responsible AI integration.

## Project Philosophy

Watchtower is intentionally designed as a small, well-engineered system rather than a feature-rich platform. Architectural clarity, maintainability, and thoughtful use of AI are prioritised over feature count. Every component should have a clear responsibility and exist for a justifiable reason. The goal is to build one thing well, not many things adequately.

**Scope** is intentionally narrow. Ship a polished MVP, then stop. Features beyond the definition of done are out of scope until the MVP is complete and evaluated.

## Architecture

```
Logs → Ingestion → Normalisation → LLM Triage → Guardrails (cross-cutting) → Threat Enrichment → Incident Report → Phone Notification
                                                                                    ↓
                                                                            Evaluation Harness
```

Guardrails are **cross-cutting**, not a single pipeline stage. They apply at three points:

1. **Post-triage:** schema validation, hallucinated-domain detection
2. **Post-enrichment:** verdict re-evaluation against threat-intel data
3. **Pre-alert:** severity gate (never auto-act on critical), rate limiting

Full architecture documentation lives in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md). Key design decisions and their rationale are recorded in [docs/ENGINEERING_JOURNAL.md](../docs/ENGINEERING_JOURNAL.md).

### Tech stack

| Concern | Choice | Notes |
| --- | --- | --- |
| Language | Python 3 | Standard library first |
| LLM | Gemini 2.5 Flash | Free tier, fast iteration. Should eventually abstract behind a Protocol/ABC so swapping providers is a config change. |
| Hardware | Raspberry Pi (Raspberry Pi OS) | 1–4 GB RAM — design accordingly |
| Threat intel | AbuseIPDB + GreyNoise | Free tiers, not yet implemented |
| Alerting | ntfy.sh | Push to phone, not yet implemented |
| Storage | JSONL | Zero dependencies, human-readable, append-only |
| Deployment | systemd or cron loop | Not yet implemented |

## Engineering Standards

These standards guide all code and design decisions. The full version lives in [docs/ENGINEERING_PRINCIPLES.md](../docs/ENGINEERING_PRINCIPLES.md).

### Optimise for

1. **Clean code over clever code.** Write code a tired teammate can understand at 2am.
2. **Small modules with one responsibility.** If you can't describe a module in a single sentence, split it.
3. **Readability over abstraction.** Don't add an abstraction until the duplication is genuinely painful.
4. **Simplicity over unnecessary features.** Every feature must earn its place against the definition of done.
5. **Maintainability over rapid hacks.** Code quality is itself a deliverable.

### Avoid

- Premature optimisation — make it correct, then make it fast (only if needed)
- Unnecessary frameworks — standard library first, small dependencies second
- Overengineering — this runs on a Raspberry Pi, not a Kubernetes cluster
- Scope creep — the #1 risk to shipping the MVP

### Design decision-making

When weighing architectural choices, prefer designs that are simpler, more maintainable, and easier to reason about. Question assumptions — including decisions already in the plan or in existing code. If an earlier choice becomes suboptimal after new information, revisit it. Intellectual honesty and constructive disagreement are engineering virtues, not interpersonal failings.

## Repository Structure

```text
watchtower/
├── src/
│   ├── ingest.py       # Pi-hole log parsing
│   ├── triage.py       # Gemini LLM triage
│   ├── guardrails.py   # Cross-cutting validation (not yet implemented)
│   ├── enrich.py       # Threat intel enrichment (not yet implemented)
│   └── alert.py        # Incident reporting + phone alerts (not yet implemented)
├── eval/
│   ├── eval.py         # Evaluation runner (baseline + gemini modes)
│   └── labelled_events.jsonl  # 7 labelled eval events
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ENGINEERING_JOURNAL.md  # Design decisions and rationale — read this first
│   ├── ENGINEERING_PRINCIPLES.md
│   └── PROJECT_BRIEF.md
├── logs/
└── .claude/
    └── CLAUDE.md       # This file (committed)
```

## Development Workflow

1. **Read the docs first.** Before making changes, review `docs/ENGINEERING_JOURNAL.md` for current status and recent decisions.
2. **Keep it small.** Prefer small, incremental changes over large rewrites.
3. **Document decisions.** Record significant architectural or engineering decisions in `docs/ENGINEERING_JOURNAL.md` with a short rationale.
4. **Maintain evaluation integrity.** The eval harness (`eval/eval.py`) should pass before and after changes to the triage pipeline.
5. **Respect the scope.** Refer to `docs/PROJECT_BRIEF.md` for the definition of done. Features not in the brief wait until after MVP.

## Documentation Conventions

- Architecture decisions go in `docs/ENGINEERING_JOURNAL.md` with date and rationale
- Component-level documentation lives in the relevant source file as docstrings
- The README is the public-facing project overview — keep it current with actual progress
- This CLAUDE.md is committed and public — keep it professional and project-focused
