# Watchtower

Watchtower is a lightweight home-lab security monitor running on a Raspberry Pi — total hardware cost less than the nearest SIEM license renewal.

I’m setting up a small self-hosted environment and want better visibility into DNS and network activity without manually reviewing raw logs. Most home networks have more devices than anyone remembers connecting. Mine is no exception. Watchtower watches the DNS traffic so I don’t have to.

The project is also a way for me to explore practical AI-assisted SOC automation: structured alert triage, guardrails, evaluation, and simple incident documentation.

---

## Why I’m building this

I have production experience building SOAR playbooks, Python integrations and SOC automation. Watchtower applies the same automation mindset to my own home infrastructure — where the SOC team is me and the SIEM is a JSONL file.

The goal is intentionally small:

> Can I build a useful mini-SOC-style monitor for my own network that uses an LLM safely and measurably, rather than just sending logs to a chatbot and hoping for the best?

The parts I care most about are:

- structured outputs instead of free-text LLM responses
- guardrails around model output
- labelled evaluation examples
- MITRE ATT&CK mapping where relevant
- lightweight alerting and incident summaries

---

## MVP

```text
Pi-hole logs
  -> ingest and normalise
  -> Gemini structured triage
  -> guardrails
  -> threat intel enrichment
  -> phone alert
  -> JSONL output
```

Watchtower currently:

- parses Pi-hole DNS query logs into structured events
- triages each event with Gemini 2.5 Flash for structured JSON classification
- validates model output (schema enforcement, hallucinated-domain detection)
- enriches suspicious or malicious domains against URLhaus threat intel
- pushes phone alerts via ntfy.sh for suspicious and malicious verdicts
- evaluates results against a labelled set of benign, suspicious, and malicious examples
- writes all events to append-only JSONL with full guardrail and enrichment context

---

## Current status

- ✅ Raspberry Pi is running (SSH, Tailscale)
- ✅ Pi-hole log parser (`src/ingest.py`)
- ✅ Gemini structured triage (`src/triage.py`) — 86% accuracy on 7-event eval set
- ✅ Post-triage guardrails: schema validation + hallucinated-domain detection
- ✅ Centralised config (`src/config.py`)
- ✅ Pipeline orchestrator (`main.py`) — ingest → triage → guardrails → enrich → alert → JSONL, with rate limiting
- ✅ Evaluation harness with baseline and Gemini modes (`eval/`)
- ✅ Threat intel enrichment (URLhaus domain reputation)
- ✅ ntfy.sh phone alerts
- ✅ Pi-hole installed and configured on the Pi
- ✅ Pipeline tested against real Pi-hole log data (manual run)
- 🎯 Next: live tail mode — pipeline runs manually, not continuously

---

## Running it

```bash
git clone https://github.com/lukenorr/watchtower.git
cd watchtower
pip install -r requirements.txt
cp .env.example .env   # add your Gemini, URLhaus, and ntfy credentials
```

Run the pipeline against a Pi-hole format log file:

```bash
echo "Jun 27 20:15:00 dnsmasq[123]: query[A] example.com from 192.168.1.42" > sample.log
python main.py --log-file sample.log
```

Results are written to `logs/run-<timestamp>.jsonl`. Suspicious or malicious verdicts trigger a phone push via your ntfy topic.

Run the evaluation harness:

```bash
python eval/eval.py                 # rules-based baseline
python eval/eval.py --mode gemini   # LLM triage + guardrails + ATT&CK scoring
```

---

## Example output

The triage output is structured JSON, not free-text:

```json
{
  "domain": "suspicious-longstring.example.com",
  "verdict": "suspicious",
  "severity": "medium",
  "confidence": 0.78,
  "reasoning": "The queried domain contains a long encoded-looking subdomain, which may indicate DNS tunnelling or staged exfiltration.",
  "mitre_attack": ["T1048"]
}
```

---

## Guardrails

Watchtower is advisory-only. It will not automatically block, isolate or modify anything on my network. (My dad would not appreciate his internet being cut off by a bug.)

Built:

- validate expected fields, types, bounds, and allowed values from the LLM
- detect hallucinated domains that don't appear in the original event
- fail safely if the LLM API is unavailable (returns unknown/low/0.0)
- skip benign events before enrichment (save API quota, don't query google.com against a malware blocklist)

Planned:

- rate-limit repeated alerts to avoid notification fatigue

---

## Evaluation

The repo includes a small labelled evaluation set for DNS events.

The evaluation harness measures:

- verdict accuracy
- false positives / false negatives
- MITRE ATT&CK mapping accuracy (gemini mode)
- whether the LLM returns valid structured output

Initial examples include benign DNS lookups (things I actually visit), suspicious long-subdomain activity, and C2-like DNS examples (things I hope my devices don't visit).

---

## Roadmap

### Done
- [x] Raspberry Pi running (SSH, Tailscale)
- [x] Initial repository created
- [x] Pi-hole DNS log parser
- [x] Centralised config
- [x] Gemini structured triage
- [x] Post-triage guardrails (schema + hallucination detection)
- [x] Pipeline orchestrator (ingest → triage → guardrails → JSONL)
- [x] Evaluation harness (baseline + Gemini modes)
- [x] Labelled evaluation examples (7 events, ATT&CK-mapped)
- [x] Threat intel enrichment (URLhaus for domains; AbuseIPDB/GreyNoise deferred for auth.log IP events)
- [x] ntfy phone alerts
- [x] Install and configure Pi-hole
- [x] Initial deployment to Pi (tested against real logs)

### In progress

- [ ] Live tail mode (continuous monitoring)

### Next

- [ ] Markdown incident summaries
- [ ] Post-enrichment guardrails (verdict re-evaluation)
- [ ] Pre-alert guardrails (severity gate, rate limiting)
- [ ] Raspberry Pi deployment (systemd service)

### Post-MVP
- [ ] Pydantic data models
- [ ] pytest test suite
- [ ] LLM provider abstraction (Protocol/ABC)
