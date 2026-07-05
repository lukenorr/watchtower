import json
import urllib.request
import urllib.parse

from config import URLHAUS_API_KEY

URLHAUS_HOST_URL = "https://urlhaus-api.abuse.ch/v1/host/"

def check_urlhaus(domain):
    """
    POSTs the domain to URLHaus for enrichment
    INPUT: domain string
    OUTPUT: dict with hit, clean, or error
    """
    # build POST body: dict -> form-encoded string -> bytes
    data = urllib.parse.urlencode({"host": domain}).encode()
    req = urllib.request.Request(url=URLHAUS_HOST_URL, data=data, headers={"Auth-Key": URLHAUS_API_KEY})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
          body = resp.read().decode()
          response = json.loads(body)
    except Exception as e:
       return {"status" : "error", "message": str(e)}
       
    query_status = response["query_status"]
       
    if query_status == "ok":
        # only keep unique values
        threats = set()
        tags = set()
        for url in response["urls"]:
            threats.add(url["threat"])
            for tag in url["tags"]:
                tags.add(tag)
        return {"status": "hit", "url_count": len(response["urls"]), "threats": list(threats), "tags": list(tags)}
    elif query_status == "no_results":
        return {"status": "clean"}
    else:
        return {"status": "error", "message": f"unexpected query_status: {query_status}"}
       
def enrich_event(event):
    """
    Gates enrichment on event verdict and nests URLhaus results.
    Benign events pass through unmodified.
    INPUT: event dict (must have 'verdict' and 'domain' keys)
    OUTPUT: same event dict, possibly with 'enrichment' key added
    """
    if event["verdict"] not in ("suspicious", "malicious"):
        return event
    result = check_urlhaus(event["domain"])
    event["enrichment"] = {"urlhaus": result}
    return event

if __name__ == "__main__":
    # Test 1: benign event skips enrichment entirely (no API call)
    benign = {"verdict": "benign", "domain": "evil-c2.malware.test"}
    result = enrich_event(benign)
    assert "enrichment" not in result, f"benign should skip, got {result.get('enrichment')}"
    print("Test 1 passed: benign skipped")

    # Test 2: suspicious event gets enriched (will return 'clean' for google.com)
    suspicious = {"verdict": "suspicious", "domain": "google.com"}
    result = enrich_event(suspicious)
    assert "enrichment" in result, "suspicious should have enrichment"
    assert "urlhaus" in result["enrichment"], "enrichment should nest under 'urlhaus'"
    print(f"Test 2 passed: enrichment status = {result['enrichment']['urlhaus']['status']}")

    print("All enrich smoke tests passed.")
    