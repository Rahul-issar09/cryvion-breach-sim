"""
Cryvion Networks — "CryvionPortal" customer portal.

!!! INTENTIONALLY VULNERABLE — for the controlled breach-simulation lab only. !!!

Planted weaknesses (each maps to a MITRE ATT&CK technique exercised by the attack chain):
  - SQL injection in /login (auth bypass)            -> T1190
  - SQL injection in /dashboard?q= (UNION data theft)-> T1190 / T1005
  - Weak, plaintext-stored credentials               -> T1552
  - OS command injection in /admin/diagnostics       -> T1059
  - Unrestricted file upload in /upload              -> T1505 (web shell)
  - DB creds exposed in env + on-disk config file    -> T1552.001
Do NOT deploy this anywhere reachable from the internet.
"""
import os
import re
import logging
import subprocess

import pymysql
from flask import Flask, request, session, redirect, url_for, send_from_directory

APP_PORT = int(os.environ.get("APP_PORT", "8080"))
# Hardened build sets APP_SECURE=1 -> parameterized queries + no shell exec.
SECURE = os.environ.get("APP_SECURE", "0") == "1"
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "insecure-dev-secret")

# --- Security event logging (consumed by the Wazuh agent for SIEM detection) ---
os.makedirs("/var/log/cryvion", exist_ok=True)
_seclog = logging.getLogger("cryvion-sec")
_seclog.setLevel(logging.INFO)
_h = logging.FileHandler("/var/log/cryvion/security.log")
# No leading timestamp: Wazuh's syslog pre-decoder mis-parses it; the SIEM
# timestamps each event on receipt. Line must start with the CRYVION_SEC token.
_h.setFormatter(logging.Formatter("CRYVION_SEC %(message)s"))
_seclog.addHandler(_h)

_SQLI_RE = re.compile(r"('|--|\bUNION\b|\bSELECT\b|\bOR\b\s+\d|#)", re.IGNORECASE)
_CMDI_RE = re.compile(r"[;&|`]|\$\(")


def sec(event, detail, ip):
    """Emit a structured security event for the SIEM."""
    detail = str(detail).replace('"', "'")[:200]
    _seclog.info('event=%s detail="%s" src=%s' % (event, detail, ip))


def db():
    """New DB connection per request (creds pulled from env — also leaked on disk)."""
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("MYSQL_USER", "webapp"),
        password=os.environ.get("MYSQL_PASSWORD", "webapp123"),
        database=os.environ.get("MYSQL_DATABASE", "cryvion"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


PAGE = """<!doctype html><html><head><title>CryvionPortal</title>
<style>body{{font-family:sans-serif;max-width:880px;margin:2rem auto;padding:0 1rem}}
nav a{{margin-right:1rem}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:4px 8px}}
.err{{color:#b00}} .box{{background:#f6f6f6;padding:1rem;border-radius:6px}}</style></head>
<body><h2>🔐 CryvionPortal <small>(internal customer portal)</small></h2>
<nav><a href="/">Home</a><a href="/dashboard">Dashboard</a><a href="/upload">Upload</a>
<a href="/admin/diagnostics">Admin Diagnostics</a>{logout}</nav><hr>{body}</body></html>"""


def render(body):
    logout = ' <a href="/logout">Logout (%s)</a>' % session["user"] if "user" in session else ""
    return PAGE.format(body=body, logout=logout)


@app.route("/")
def home():
    who = ("Logged in as <b>%s</b> (role: %s)." % (session["user"], session.get("role"))
           if "user" in session else "Not logged in.")
    return render(f"<p>Welcome to the Cryvion customer portal.</p><p class=box>{who}</p>"
                  '<p><a href="/login">Login</a></p>')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        ip = request.remote_addr
        if _SQLI_RE.search(u) or _SQLI_RE.search(p):
            sec("SQLI", "login:%s" % u, ip)
        q = "(parameterized)"
        try:
            conn = db()
            with conn.cursor() as cur:
                if SECURE:
                    # FIX: parameterized query — no SQL injection
                    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
                else:
                    # VULN: string-concatenated SQL -> injection / auth bypass (T1190)
                    q = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (u, p)
                    cur.execute(q)
                row = cur.fetchone()
        except Exception as e:
            return render(f'<p class=err>DB error: {e}</p><pre>{q}</pre>')
        if row:
            session["user"] = row["username"]
            session["role"] = row["role"]
            sec("LOGIN_SUCCESS", u, ip)
            return redirect(url_for("dashboard"))
        sec("LOGIN_FAILED", u, ip)
        return render('<p class=err>Invalid credentials.</p>' + login_form())
    return render(login_form())


def login_form():
    return ('<form method=post><p>Username <input name=username></p>'
            '<p>Password <input name=password type=password></p>'
            '<button>Login</button></form>')


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    q = request.args.get("q", "")
    if q and _SQLI_RE.search(q):
        sec("SQLI", "dashboard:%s" % q, request.remote_addr)
    sql = "(parameterized)"
    try:
        conn = db()
        with conn.cursor() as cur:
            if SECURE:
                # FIX: parameterized LIKE — no UNION injection
                cur.execute("SELECT id,name,email,ssn,credit_card,balance FROM customers WHERE name LIKE %s", ("%" + q + "%",))
            else:
                # VULN: string-concatenated LIKE -> UNION-based injection (T1005 data theft)
                sql = "SELECT id,name,email,ssn,credit_card,balance FROM customers WHERE name LIKE '%%%s%%'" % q
                cur.execute(sql)
            rows = cur.fetchall()
    except Exception as e:
        return render(f'<p class=err>Query error: {e}</p><pre>{sql}</pre>')
    head = "<tr>" + "".join(f"<th>{c}</th>" for c in (rows[0].keys() if rows else
            ["id", "name", "email", "ssn", "credit_card", "balance"])) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>" for r in rows)
    return render(f'<h3>Customer Records</h3>'
                  f'<form><input name=q value="{q}" placeholder="search name"> <button>Search</button></form>'
                  f'<table>{head}{body}</table>')


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            return render('<p class=err>No file.</p>')
        # VULN: no extension / content-type / size validation (T1505 web shell)
        sec("UPLOAD", f.filename, request.remote_addr)
        dest = os.path.join(UPLOAD_DIR, f.filename)
        f.save(dest)
        return render(f'<p>Stored at <code>/uploads/{f.filename}</code>.</p>'
                      f'<a href="/uploads/{f.filename}">view</a>')
    return render('<h3>Upload report</h3><form method=post enctype=multipart/form-data>'
                  '<input type=file name=file> <button>Upload</button></form>')


@app.route("/uploads/<path:name>")
def serve_upload(name):
    return send_from_directory(UPLOAD_DIR, name)


@app.route("/admin/diagnostics")
def diagnostics():
    # "Admin-only" network tool. Weak gate; role is trivially obtained via SQLi/brute.
    if session.get("role") != "admin":
        return render('<p class=err>Admin only.</p>')
    host = request.args.get("host", "")
    out = ""
    if host:
        if _CMDI_RE.search(host):
            sec("RCE", host, request.remote_addr)
        try:
            if SECURE:
                # FIX: no shell; reject anything that isn't a bare hostname/IP
                if not re.fullmatch(r"[A-Za-z0-9.\-]+", host):
                    out = "rejected: invalid host"
                else:
                    out = subprocess.run(["ping", "-c", "1", host],
                                         capture_output=True, text=True, timeout=15).stdout
            else:
                # VULN: shell=True with user input -> OS command injection / RCE (T1059)
                out = subprocess.run("ping -c 1 " + host, shell=True,
                                     capture_output=True, text=True, timeout=15).stdout
        except Exception as e:
            out = str(e)
    return render('<h3>Network Diagnostics</h3>'
                  f'<form><input name=host value="{host}" placeholder="host to ping"> '
                  f'<button>Run</button></form><pre class=box>{out}</pre>')


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # debug=True is itself a weakness (Werkzeug console) in the vulnerable build;
    # the hardened build sets FLASK_DEBUG=0.
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=APP_PORT, debug=debug)
