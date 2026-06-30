import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.ingest import parse_pihole_line

def load_labelled_events(path):
    """load all events from json; return list of dicts"""
    events = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events

def baseline_triage(event):
    """test the eval pipeline with simple rules-based traige"""
    domain = event.get("domain", "").lower()

    # check for known malicious or suspicious patterns
    for d in domain: 
        for token in ["evil", "malware", "baddomain", "c2"]:
            if d == token: 
                return "malicious"
    if len(domain.split(".")[0]) > 20:
        # DNS tunnelling indicator
        return "suspicous"
    return "benign"

def main():
    # load the labelled events
    labelled_path = ROOT / "eval" / "labelled_events.jsonl"
    rows = load_labelled_events(labelled_path)

    total = len(rows)
    correct = 0

    for row in rows:
        # parse raw log into clean events dict
        parsed = parse_pihole_line(row["raw_log"])
        if not parsed:
            print(f"SKIP: could not parse: {row['raw_log'][:60]}...")
            continue

        # run the baseline triage
        predicted = baseline_triage(parsed)

        # compare
        actual = row["label"]
        if predicted == actual:
            correct += 1

        print(f"{parsed['domain']}: expected = {actual} predicted = {predicted}")

    print("Watchtower evaluation")
    print(f"Events processed: {total}")
    print(f"Events correct: {correct}")
    print(f"Verdict accuracy: {correct}/{total} ({correct / total:.0%})")

if __name__ == "__main__":
    main()