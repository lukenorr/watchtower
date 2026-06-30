import json
from src.ingest import parse_pihole_line

with open('eval/labelled_events.jsonl', 'r') as f:
    first_line = f.readline()

# get an event
event = json.loads(first_line)
raw_log = event["raw_log"]
print("raw log line:")
print(raw_log)

# run the parser
parsed = parse_pihole_line(raw_log)
print("parsed event:")
print(parsed)