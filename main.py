import argparse
import sys
from pathlib import Path
import time
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[0]
sys.path.append(str(ROOT / "src"))

from ingest import parse_pihole_line
from triage import gemini_triage_event
from guardrails import validate_schema, validate_domain
from enrich import enrich_event
from alert import send_ntfy

def main():
    parser = argparse.ArgumentParser(description="Watchtower pipeline")
    parser.add_argument("--log-file", required=True, help="path to Pi-hole log file")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = ROOT / "logs" / f"run-{timestamp}.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # read the log file
    with open(args.log_file, "r") as f:
        # append output
        with open(output_path, "a") as a:
            # loop through events
            for line in f:
                # ingest - parse events
                parsed = parse_pihole_line(line)
                if parsed is None:
                    print("None returned when parsing")
                    continue
                if not isinstance(parsed, dict):
                    print("parsed is not dictionary")
                    continue
                
                print(f"parsed domain: {parsed['domain']}")

                # triage - triage event with gemini
                try:
                    triaged = gemini_triage_event(parsed)
                except Exception as e:
                    print(f"Gemini API error: {e}")
                    continue
                print(f"triage verdict: {triaged['verdict']}")
                # avoid burning the gemini limit
                time.sleep(12)

                # guardrails - validate schema and domain
                guardrail_errors = validate_schema(triaged) + validate_domain(triaged, parsed)
                if guardrail_errors:
                    for error in guardrail_errors:
                        print(f"guardrail: {error}")
                else:
                    # enrichment - run domain through URLhaus
                    enrich_event(triaged)

                    # alert - push notification for suspicious or malicious
                    if triaged["verdict"] in ("suspicious", "malicious"):
                        alert_result = send_ntfy(triaged)
                        print(f"alert: {alert_result['status']}")

                # write results
                result = {
                    **parsed,
                    **triaged,
                    "guardrail_errors" : guardrail_errors
                }
                a.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    main()
