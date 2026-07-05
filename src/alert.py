import urllib.request

from config import NTFY_TOPIC

ALERT_FORMAT = """
Watchtower: suspicious activity
Domain: {domain}
Verdict: {verdict} | Severity: {severity}
Threats: {enrichment}
"""

NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_ntfy(event):
    """
    POST event details to ntfy.sh API to create an alert
    INPUT: event dict
    OUTPUT: alert status dict
    """
    alert_body = ALERT_FORMAT.format(domain=event["domain"], verdict=event["verdict"], severity=event["severity"], enrichment=", ".join(event.get("enrichment", {}).get("urlhaus", {}).get("threats", ["unknown"])))
    # api expects raw body
    data = alert_body.encode()
    req = urllib.request.Request(url=NTFY_URL, data=data, headers={"Title": "Watchtower: suspicious activity"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
            return {"status" : "sent"}
    except Exception as e:
        return {"status" : "error", "message" : str(e)}
    
if __name__ == "__main__":
    # simulate an enriched event from the pipeline
    test_event = {
        "domain" : "evil-c2.malware.test",
        "verdict" : "malicious",
        "severity" : "high",
        "enrichment" : {
            "urlhaus" : {
                "status" : "hit",
                "threats" : ["malware_download", "emotet"],
                "tags" : ["exe", "Heodo"],
                "url_count" : 3
            }
        }
    }
    result = send_ntfy(test_event)
    assert result["status"] == "sent", f"expect sent, got {result}"
    print(f"Alert sent: {result['status']}")
    print("All alert smoke tests passed.")
