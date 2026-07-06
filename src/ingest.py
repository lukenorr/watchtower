import re
import json
from datetime import datetime

def parse_pihole_line(line):
    """
    Parse a Pi-hole log line into the event schema dict.

    INPUT: raw event log from Pi-hole
    OUTPUT: parsed dict
    """

    # example Pi-hole log line:
    # "Jul  6 22:47:46 dnsmasq[1429725]: query[A] google.com from 127.0.0.1"
    pattern = r'^(?P<timestamp>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+dnsmasq\[\d+\]:\s+query\[(?P<query_type>\w+)\]\s+(?P<domain>[\w\.-]+)\s+from\s+(?P<client_ip>\d+\.\d+\.\d+\.\d+)'
    match = re.match(pattern, line)
    if not match:
        return None

    # add year to the timestamp (not captured by pi-hole)
    timestamp_str = match.group('timestamp')
    timestamp = datetime.strptime(timestamp_str + " 2026", "%b %d %H:%M:%S %Y")  # placeholder 2026 — make smarter later
    iso_ts = timestamp.isoformat()

    return {
        "timestamp" : iso_ts,
        "source" : "pihole",
        "log_type" : "dns_query",
        "domain" : match.group('domain'),
        "client_ip" : match.group('client_ip'),
        "query_type" : match.group('query_type'),
        "raw_log" : line.strip(),
    }

# smoke test
if __name__ == "__main__":
    test_lines = [
        "Jun 27 20:15:00 dnsmasq[123]: query[A] example.com from 192.168.1.42",
        "Jun 27 20:15:01 dnsmasq[123]: query[AAAA] google.com from 10.0.0.5",
    ]
    for line in test_lines:
        parsed = parse_pihole_line(line)
        print(json.dumps(parsed, indent=2))