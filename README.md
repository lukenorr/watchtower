# Watchtower

Watchtower is a lightweight home-lab security monitor for my Raspberry Pi and home network.

I’m setting up a small self-hosted environment and want better visibility into DNS and network activity without manually reviewing raw logs. The first version focuses on Pi-hole DNS logs: ingesting them, normalising them into structured events, triaging notable activity with an LLM, and evaluating the results against labelled examples.

The project is also a way for me to explore practical AI-assisted SOC automation: structured alert triage, guardrails, evaluation, and simple incident documentation.

---

## Why I’m building this

I have production experience building SOAR playbooks, Python integrations and SOC automation. Watchtower applies the same automation mindset to my own home infrastructure.

The goal is intentionally small:

> Can I build a useful mini-SOC-style monitor for my own network that uses an LLM safely and measurably, rather than just sending logs to a chatbot?

The parts I care most about are:

- structured outputs instead of free-text LLM responses
- guardrails around model output
- labelled evaluation examples
- MITRE ATT&CK mapping where relevant
- lightweight alerting and incident summaries

---

## Planned MVP

```text
Pi-hole logs
  -> ingest and normalise
  -> Gemini structured triage
  -> guardrails
  -> incident summary / alert
  -> evaluation harness
```

The first working version will:

- parse Pi-hole DNS query logs
- normalise raw log lines into a common event format
- use Gemini for structured JSON triage
- validate the model output
- flag suspicious or malicious DNS activity
- evaluate results against labelled benign, suspicious and malicious examples
- generate simple markdown incident summaries

---

## Current status

- Raspberry Pi is running
- SSH and Tailscale access are working
- Repository structure is created
- Initial labelled evaluation examples are started
- Pi-hole setup, DNS ingestion and LLM triage are next

---

## Example target output

The intended triage output is structured JSON, not free-text:

```json
{
  "verdict": "suspicious",
  "severity": "medium",
  "category": "possible_dns_exfiltration",
  "confidence": 0.78,
  "reasoning": "The queried domain contains a long encoded-looking subdomain, which may indicate DNS tunnelling or staged exfiltration.",
  "recommended_action": "Review DNS query volume from the client host and check for repeated similar queries.",
  "mitre_attack": ["T1048"],
  "indicators": ["example-suspicious-domain.test"]
}
```

---

## Guardrails I want to build in

Watchtower is advisory-only. It will not automatically block, isolate or modify anything on my network.

Planned guardrails:

- require valid structured JSON from the LLM
- validate expected fields and severity values
- flag indicators that were not present in the original event
- fail safely if the LLM API is unavailable
- rate-limit repeated alerts to avoid noise

---

## Evaluation

The repo includes a small labelled evaluation set for DNS events.

The evaluation harness will measure:

- verdict accuracy
- false positives / false negatives
- MITRE ATT&CK mapping accuracy
- whether the LLM returns valid structured output

Initial examples include benign DNS lookups, suspicious long-subdomain activity, and C2-like DNS examples.

---

## Roadmap

- [x] Raspberry Pi running
- [x] SSH and Tailscale access working
- [x] Initial repository created
- [x] Initial labelled evaluation examples
- [ ] Install and configure Pi-hole
- [ ] Build Pi-hole DNS log parser
- [ ] Add Gemini structured triage
- [ ] Add output validation and guardrails
- [ ] Add evaluation script
- [ ] Generate markdown incident summaries
- [ ] Run against live Pi-hole logs
- [ ] Add ntfy phone alerts