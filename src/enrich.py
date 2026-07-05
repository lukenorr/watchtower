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
       


