import requests

SITES = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""

    return "https://" + host + "/" + path.lstrip("/")


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""

    return url.startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        response = requests.get(url, timeout=5)
        print("Status:", response.status_code)
    
        print("Content-Type:", response.headers.get("Content-Type"))
    except requests.exceptions.RequestException as e:
    
        print("Eroare:", type(e).__name__)


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:

        return {"status": None, "error": "timeout"}
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": type(e).__name__}


    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    return {
        "status": response.status_code,
        "content_type": content_type,
        "length": len(response.content),  # dimensiunea în octeți
        "server": response.headers.get("Server", "unknown"),  # "unknown" dacă lipsește
    }


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""

    results = []
    for url in SITES:
        info = check_site(url)
        info["url"] = url
        results.append(info)


    working = [r for r in results if r["status"] == 200]

    working.sort(key=lambda r: r["length"], reverse=True)

    for r in working:
        print(f"{r['url']:<45} -> {r['status']}, {r['length']} octeți")

  
    failed = len(results) - len(working)
    print(f"Reușite: {len(working)} | Eșuate: {failed}")


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        return {"status": None, "error": type(e).__name__}

    present = []
    missing = []
   
    for header in SECURITY_HEADERS:
        if header in response.headers:
            present.append(header)
        else:
            missing.append(header)

  
    score = len(present) * 100 // len(SECURITY_HEADERS)
    return {"present": present, "missing": missing, "score": score}


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    status = None 
    error = None   
    made = 0      

    for _ in range(attempts):
        made += 1  
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            error = type(e).__name__
            continue 

        status = response.status_code
        if status < 500:
            break 

    result = {"status": status, "attempts": made}

    if status is None:
        result["error"] = error
    return result
