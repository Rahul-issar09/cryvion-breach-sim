"""Generate a self-contained HTML project explainer (diagrams embedded as base64).
Open in a browser -> Print -> Save as PDF."""
import os, base64

HERE = os.path.dirname(__file__)
FIG = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "Project_Explainer.html")


def img(name):
    p = os.path.join(FIG, name)
    if not os.path.exists(p):
        return ""
    b = base64.b64encode(open(p, "rb").read()).decode()
    return f'<img src="data:image/png;base64,{b}" alt="{name}"/>'


CSS = """
:root{--blue:#1f6feb;--ink:#1b2733;--muted:#5b6b7b;--line:#dfe6ee;--bg:#f6f9fc;}
*{box-sizing:border-box;}
body{font-family:'Segoe UI',Calibri,Arial,sans-serif;color:var(--ink);line-height:1.55;
  max-width:900px;margin:0 auto;padding:32px 28px;background:#fff;}
h1{font-size:26px;margin:0 0 4px;color:var(--ink);}
h2{font-size:20px;margin:30px 0 10px;padding-bottom:6px;border-bottom:3px solid var(--blue);color:#0d3a72;}
h3{font-size:16px;margin:18px 0 6px;color:#0d3a72;}
h4{font-size:14px;margin:12px 0 4px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}
p,li{font-size:13.5px;}
.subtitle{color:var(--muted);font-size:14px;margin:0 0 14px;}
.lead{font-size:15px;background:var(--bg);border-left:4px solid var(--blue);padding:12px 16px;border-radius:6px;}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:12.5px;}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top;}
th{background:#eef4fb;color:#0d3a72;}
tr:nth-child(even) td{background:#fafcfe;}
code{background:#eef2f6;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace;font-size:12px;color:#b3261e;}
pre{background:#0f172a;color:#e2e8f0;padding:12px 14px;border-radius:8px;overflow-x:auto;font-size:12px;line-height:1.4;}
pre code{background:none;color:inherit;padding:0;}
img{max-width:100%;display:block;margin:14px auto;border:1px solid var(--line);border-radius:8px;}
.box{border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0;background:#fff;}
.analogy{background:#fff8e6;border-left:4px solid #f0a500;}
.key{background:#eaf7ee;border-left:4px solid #1e9e54;}
.warn{background:#fdeaea;border-left:4px solid #d64545;}
.qa{background:#f3f0fc;border-left:4px solid #7c4dff;padding:10px 14px;border-radius:6px;margin:10px 0;}
.qa .q{font-weight:700;color:#4a2fb5;}
.toc{columns:2;font-size:13px;background:var(--bg);border-radius:8px;padding:14px 20px;}
.toc a{color:#0d3a72;text-decoration:none;}
.pill{display:inline-block;background:#eef4fb;color:#0d3a72;border-radius:20px;padding:2px 10px;font-size:11px;margin:2px 3px;}
.muted{color:var(--muted);}
@media print{
  body{max-width:none;padding:0;font-size:12px;}
  h2{page-break-after:avoid;}
  table,pre,img,.box,.qa{page-break-inside:avoid;}
  .toc{columns:2;}
  a{color:inherit;text-decoration:none;}
}
"""

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Cryvion Breach Lifecycle — Project Explainer</title>
<style>{css}</style></head><body>

<h1>End-to-End Breach Lifecycle Simulation in Containerized Environments</h1>
<p class="subtitle">Cryvion Networks &middot; Project 4 &middot; Cyber Group 2 &middot; A complete explainer — read this and you can confidently explain the project to anyone.</p>

<div class="lead"><b>One-line pitch:</b> We built a fake company entirely out of Docker containers, hacked it end-to-end with a realistic multi-stage attack, caught every stage with a SIEM, investigated it like forensic examiners, then re-built it securely and proved the <i>same</i> attack no longer works.</div>

<h4>How to use this document</h4>
<p>Read top to bottom once for understanding. Then use the <b>Cheat Sheet</b> (end) to revise, and the <b>Viva Q&amp;A</b> to rehearse answers. Each concept has a plain-English explanation and, where useful, an everyday analogy.</p>

<h2 id="toc">Contents</h2>
<div class="toc">
1. <a href="#pitch">The 30-second &amp; 2-minute pitch</a><br>
2. <a href="#problem">The problem we solve</a><br>
3. <a href="#concepts">Key concepts (so you can explain the jargon)</a><br>
4. <a href="#arch">The lab architecture</a><br>
5. <a href="#attack">The attack, stage by stage</a><br>
6. <a href="#how">How the key attacks actually work</a><br>
7. <a href="#detect">Detection — the SOC view</a><br>
8. <a href="#forensics">Forensics — the investigation</a><br>
9. <a href="#ir">Incident response</a><br>
10. <a href="#harden">The fix — hardened re-architecture</a><br>
11. <a href="#cicd">DevSecOps CI/CD</a><br>
12. <a href="#results">Results &amp; metrics</a><br>
13. <a href="#viva">Viva / defence Q&amp;A</a><br>
14. <a href="#limits">Limitations &amp; future work</a><br>
15. <a href="#cheat">One-page cheat sheet</a><br>
</div>

<h2 id="pitch">1. The 30-second &amp; 2-minute pitch</h2>
<h3>30 seconds</h3>
<p>"Modern companies run their apps in containers. That's flexible but it widens the attack surface. We built a small but realistic containerized enterprise, ran a full multi-stage breach against it — from scanning to stealing customer data — detected every stage with a SIEM mapped to MITRE ATT&amp;CK, investigated it forensically, and then re-architected it with Zero-Trust hardening. Running the exact same attack against the hardened version blocked everything."</p>
<h3>2 minutes (the story arc)</h3>
<p>We play a security consulting team for a fictional company, <b>Cryvion Networks</b>. We do all six roles a real security team does: <b>attacker, SOC analyst, forensic examiner, incident responder, security architect, and CISO</b>. First we build the company out of Docker containers — a web portal, a database of customer data, an internal server, and a monitoring system. Then we attack it through nine stages, each one a real technique tagged to the MITRE ATT&amp;CK framework. Our SIEM (Wazuh) detects the attack and tags each alert with its technique. We then run an automated forensic collector that reconstructs a timeline and lists indicators of compromise. Finally — the important part — we fix every weakness: a web firewall, network segmentation, least-privilege containers, secrets management, and a DevSecOps pipeline. We re-run the identical attack and it fails completely. The headline is <b>"same attack, two architectures, opposite outcomes."</b></p>

<h2 id="problem">2. The problem we solve</h2>
<p>Enterprises increasingly run on containers and DevSecOps pipelines. This improves speed but expands the attack surface to brute-force, web exploitation, container compromise, lateral movement, and data exfiltration. Many organisations lack a <b>safe, realistic place to practise</b> detecting and responding to such attacks, so their defences go untested until a real incident hits. Our project is exactly that place: a reproducible lab where a breach can be executed, detected, investigated, and prevented.</p>

<h2 id="concepts">3. Key concepts (so you can explain the jargon)</h2>
<table>
<tr><th>Term</th><th>Plain meaning</th><th>Analogy</th></tr>
<tr><td><b>Container / Docker</b></td><td>A lightweight package holding an app + everything it needs, sharing the host's OS kernel.</td><td>A shipping container: standardised, portable, stackable.</td></tr>
<tr><td><b>MITRE ATT&amp;CK</b></td><td>A catalogue of real attacker techniques, each with an ID (e.g., T1190).</td><td>A "dictionary of hacker moves" everyone agrees on.</td></tr>
<tr><td><b>Cyber Kill Chain</b></td><td>The stages of an intrusion, recon &rarr; actions on objectives.</td><td>The steps of a heist: case the place &rarr; break in &rarr; grab the loot.</td></tr>
<tr><td><b>SIEM</b></td><td>Software that collects logs from everywhere and raises alerts. We use Wazuh.</td><td>A central security-camera control room.</td></tr>
<tr><td><b>FIM</b></td><td>File Integrity Monitoring — alerts when important files change.</td><td>A tamper seal on a door.</td></tr>
<tr><td><b>WAF</b></td><td>Web Application Firewall — inspects web traffic and blocks malicious requests. We use ModSecurity + OWASP CRS.</td><td>A bouncer reading every request at the door.</td></tr>
<tr><td><b>Zero Trust</b></td><td>Never trust by default; only allow the exact connections needed.</td><td>Key-card doors on every room, not one key to the whole building.</td></tr>
<tr><td><b>IOC</b></td><td>Indicator of Compromise — evidence an attack happened (a bad IP, a file hash).</td><td>Fingerprints at a crime scene.</td></tr>
<tr><td><b>NIST SP 800-61</b></td><td>The standard incident-response lifecycle (Prepare, Detect, Contain, Eradicate, Recover, Learn).</td><td>The fire-drill procedure for a cyber incident.</td></tr>
</table>

<h2 id="arch">4. The lab architecture</h2>
<p>The whole "company" is Docker containers split across network zones that mimic real enterprise segmentation. Crucially, the web application is <b>dual-homed</b> — connected to both the public DMZ and the internal network. That single design flaw is what lets one web compromise reach the internal systems.</p>
{fig_vuln}
<table>
<tr><th>Container</th><th>Role</th></tr>
<tr><td><code>web-app</code> (Flask)</td><td>Public customer portal; the attacker's entry point. Intentionally vulnerable.</td></tr>
<tr><td><code>db</code> (MySQL)</td><td>Holds fake customer PII (names, SSNs, card numbers) — the "crown jewels".</td></tr>
<tr><td><code>internal-svc</code> (SSH)</td><td>Internal backup server; the lateral-movement target.</td></tr>
<tr><td><code>attacker</code></td><td>The adversary's machine, deliberately limited to the DMZ.</td></tr>
<tr><td><code>Wazuh</code> stack</td><td>The SIEM watching every container.</td></tr>
</table>
<div class="box key"><b>Why it matters:</b> the attacker can reach <i>only</i> the web app directly. Everything deeper (database, internal server) must be reached <i>through</i> the compromised web app — which is exactly how real lateral movement works, and what we later block with segmentation.</div>

<h2 id="attack">5. The attack, stage by stage</h2>
<p>One script (<code>run-attack.sh</code>) runs the whole chain. Each stage is a real technique mapped to MITRE ATT&amp;CK.</p>
{fig_attack}
<table>
<tr><th>#</th><th>Stage</th><th>What happens</th><th>MITRE</th></tr>
<tr><td>1</td><td>Reconnaissance</td><td><code>nmap</code> scans and fingerprints the web app.</td><td>T1595</td></tr>
<tr><td>2</td><td>Initial Access</td><td>Hydra brute-forces login (cracks <code>admin/admin123</code>); SQL injection bypasses the login.</td><td>T1110 / T1190</td></tr>
<tr><td>3</td><td>Execution</td><td>Command injection gives a <b>root</b> shell inside the web container; a web shell is uploaded.</td><td>T1059 / T1505</td></tr>
<tr><td>4</td><td>Persistence</td><td>A backdoor admin user, a cron job, and an SSH key are planted.</td><td>T1136/T1053/T1098</td></tr>
<tr><td>5</td><td>Privilege Esc.</td><td>The mounted Docker socket is found — a route to take over the host.</td><td>T1611</td></tr>
<tr><td>6</td><td>Credential Access</td><td>Database and SSH passwords are read from a config file and environment.</td><td>T1552</td></tr>
<tr><td>7</td><td>Lateral Movement</td><td>Using a reused password, the attacker pivots over SSH to the internal server.</td><td>T1021 / T1078</td></tr>
<tr><td>8</td><td>Collection</td><td>Customer PII and an internal backup (with a flag) are stolen.</td><td>T1005</td></tr>
<tr><td>9</td><td>Exfiltration</td><td>Stolen data is sent to the attacker's server over HTTP, plus a DNS-tunnelling demo.</td><td>T1041 / T1048</td></tr>
</table>

<h2 id="how">6. How the key attacks actually work</h2>
<h3>SQL Injection (T1190)</h3>
<p>The login query is built by gluing user input into SQL text:</p>
<pre><code>"SELECT * FROM users WHERE username='%s' AND password='%s'" % (u, p)</code></pre>
<p>If the attacker types the username <code>admin' -- -</code>, the query becomes <code>... WHERE username='admin' -- -' AND password='...'</code>. The <code>--</code> turns the rest into a comment, so the password check disappears and they log in as admin <b>without a password</b>.</p>
<div class="box analogy"><b>Analogy:</b> it's like a form that says "tell me your name", and you write your name <i>plus</i> "and ignore the password question" — and the clerk obediently does.</div>

<h3>OS Command Injection &rarr; RCE (T1059)</h3>
<p>A "network diagnostics" page runs <code>ping</code> on whatever host you give it, using a shell:</p>
<pre><code>subprocess.run("ping -c 1 " + host, shell=True)</code></pre>
<p>If <code>host</code> = <code>127.0.0.1; id</code>, the shell runs <code>ping ...</code> <b>then</b> <code>id</code> — so the attacker runs any command they want, as root. That's Remote Code Execution.</p>

<h3>Lateral Movement (T1021)</h3>
<p>The attacker can't reach the internal server directly. But from the root shell on the web container, they reuse the password they found and SSH inward: <code>sshpass -p Password1 ssh svc-backup@internal-svc</code>. The pivot succeeds because (a) the web app is on the internal network and (b) the same password was reused. Both are fixed in the hardened build.</p>

<h2 id="detect">7. Detection — the SOC view</h2>
<p>The SIEM turns the attack into alerts. The web app writes security events to a log; Wazuh agents ship logs and watch files; the manager classifies events with <b>custom rules tagged to MITRE</b>.</p>
{fig_detect}
<table>
<tr><th>Attack</th><th>How it's caught</th><th>MITRE</th></tr>
<tr><td>Brute force</td><td>Rule on repeated failed logins + a correlation rule when many cluster.</td><td>T1110</td></tr>
<tr><td>SQL injection</td><td>Custom rule on the SQLi security event.</td><td>T1190</td></tr>
<tr><td>Command injection</td><td>Custom rule on the RCE event.</td><td>T1059</td></tr>
<tr><td>Web shell upload</td><td>Upload rule + File Integrity Monitoring on the upload folder.</td><td>T1505</td></tr>
<tr><td>Persistence</td><td>FIM flags changes to <code>/etc/passwd</code>, cron, SSH keys.</td><td>T1053</td></tr>
<tr><td>Lateral movement</td><td>Built-in SSH rule detects the login on the internal host.</td><td>T1021/T1078</td></tr>
</table>
<p>Six distinct ATT&amp;CK techniques are detected. We also export an <b>ATT&amp;CK Navigator layer</b> that colours the whole campaign on one screen.</p>

<h2 id="forensics">8. Forensics — the investigation</h2>
<p>An automated collector (<code>collect.sh</code>) gathers evidence from the compromised containers and the SIEM. The standout insight: because a container image is <b>immutable</b>, the command <code>docker diff</code> shows <i>exactly</i> what the attacker added — the backdoor user, the cron job, the SSH key, the web shell — with no noise.</p>
<div class="box key"><b>Talking point:</b> "Container forensics is cleaner than traditional forensics, because the clean image is a perfect baseline to diff against."</div>
<p>It also builds a <b>timeline</b> from SIEM alerts and lists <b>IOCs</b>: the web-shell's SHA-256 hash, the attacker IP, the C2 endpoint, and the backdoor account.</p>

<h2 id="ir">9. Incident response (NIST SP 800-61)</h2>
<table>
<tr><th>Phase</th><th>What we do in the lab</th></tr>
<tr><td>Preparation</td><td>SIEM deployed, segmentation defined, collector ready.</td></tr>
<tr><td>Detection &amp; Analysis</td><td>ATT&amp;CK-tagged alerts + reconstructed timeline.</td></tr>
<tr><td>Containment</td><td><code>docker network disconnect</code> + <code>docker pause</code> the compromised container.</td></tr>
<tr><td>Eradication</td><td>Remove persistence; rebuild from the clean image; rotate credentials.</td></tr>
<tr><td>Recovery</td><td>Redeploy onto the hardened architecture.</td></tr>
<tr><td>Lessons Learned</td><td>Feed root causes into the hardened design and CI pipeline.</td></tr>
</table>

<h2 id="harden">10. The fix — hardened re-architecture</h2>
<p>Every root cause gets a control, and lateral movement is contained by network segmentation. The web tier sits behind a WAF and can reach <i>only</i> the database; the internal server is isolated; containers run as non-root with no extra privileges; the Docker socket is removed; passwords come from Docker secrets; and the application code itself is fixed (parameterised queries, no shell execution).</p>
{fig_hardened}
<table>
<tr><th>Weakness (before)</th><th>Fix (after)</th></tr>
<tr><td>SQLi / command injection in code</td><td>Parameterised queries, no-shell exec, + WAF (defence-in-depth)</td></tr>
<tr><td>Flat, dual-homed network</td><td>Zero-Trust micro-segmentation (4 isolated networks)</td></tr>
<tr><td>Container runs as root, all capabilities</td><td>Non-root, <code>cap_drop ALL</code>, <code>no-new-privileges</code>, read-only filesystem</td></tr>
<tr><td>Host Docker socket mounted</td><td>Socket removed (no breakout)</td></tr>
<tr><td>Plaintext / reused credentials</td><td>Docker secrets; key-only SSH</td></tr>
<tr><td>No release security gates</td><td>DevSecOps CI pipeline</td></tr>
</table>

<h2 id="cicd">11. DevSecOps CI/CD</h2>
<p>A pipeline adds automated security gates so an insecure image or config can't be shipped. Each gate fails the build on serious findings.</p>
{fig_cicd}
<p><span class="pill">Hadolint — Dockerfile lint</span><span class="pill">Semgrep — code (SAST)</span><span class="pill">Checkov — config (IaC)</span><span class="pill">Trivy — image CVEs</span><span class="pill">OWASP ZAP — running app (DAST)</span></p>

<h2 id="results">12. Results &amp; metrics</h2>
<table>
<tr><th>Objective</th><th>Vulnerable</th><th>Hardened</th></tr>
<tr><td>SQLi auth bypass</td><td>Succeeds</td><td>Blocked ("Invalid credentials")</td></tr>
<tr><td>SQLi data theft</td><td>Dumps PII</td><td>Blocked (param query + WAF 403)</td></tr>
<tr><td>Command injection / RCE</td><td>Root shell</td><td>Blocked (empty result + WAF 403)</td></tr>
<tr><td>PII exfiltration</td><td>5 SSNs stolen</td><td>Blocked (0 bytes)</td></tr>
<tr><td>Credential harvest</td><td>Config dumped</td><td>Blocked (file removed)</td></tr>
<tr><td>Lateral movement</td><td>Pivot succeeds</td><td>Blocked (segmentation)</td></tr>
<tr><td>Container breakout</td><td>Socket present</td><td>No socket found</td></tr>
</table>
<p><b>Headline numbers:</b> 15 ATT&amp;CK techniques across 9 tactics exercised; 6 techniques detected with high-fidelity alerts; <b>8 of 8</b> damaging objectives blocked after hardening.</p>

<h2 id="viva">13. Viva / defence Q&amp;A</h2>
<div class="qa"><span class="q">Q: In one line, what is your project?</span><br>A safe, reproducible Docker lab that runs a full multi-stage breach, detects it with a MITRE-mapped SIEM, investigates it forensically, and proves a hardened re-architecture blocks the same attack.</div>
<div class="qa"><span class="q">Q: Why containers specifically?</span><br>Because enterprises are moving to containerised, DevSecOps infrastructure, which expands the attack surface (root containers, the Docker socket, flat networks). Studying breaches in that exact context is the gap we fill.</div>
<div class="qa"><span class="q">Q: How does the SQL injection bypass login?</span><br>The query concatenates user input. Entering <code>admin' -- -</code> comments out the password check, so it returns the admin row without a valid password.</div>
<div class="qa"><span class="q">Q: How did the attacker get from the web app to the internal server?</span><br>Two flaws: the web app was on the internal network (flat segmentation) and a service password was reused. From the root shell on the web app, the attacker SSH'd inward with the reused password. We fix both with micro-segmentation and key-only SSH.</div>
<div class="qa"><span class="q">Q: What is the Docker socket risk?</span><br>Mounting <code>/var/run/docker.sock</code> into a container lets code inside it control Docker on the host — effectively full host takeover. The hardened build removes it.</div>
<div class="qa"><span class="q">Q: How does your SIEM know it's an attack, not normal traffic?</span><br>The app emits structured security events; a custom Wazuh decoder parses them and rules classify them (e.g., a SQLi event &rarr; rule 100110, tagged T1190). File-integrity and SSH rules cover the rest.</div>
<div class="qa"><span class="q">Q: Is the WAF enough on its own?</span><br>No — a WAF is a <i>compensating</i> control. We also fixed the code (parameterised queries, no shell). The WAF is defence-in-depth, and SAST in CI enforces the code fix going forward.</div>
<div class="qa"><span class="q">Q: How do you prove the hardening works?</span><br>We re-run the <i>identical</i> attack script against the hardened stack. The damaging stages produce empty results (0-byte loot), the WAF returns 403, the pivot fails, and the socket is gone — while legitimate traffic still works.</div>
<div class="qa"><span class="q">Q: What's the biggest limitation?</span><br>No network IDS, so pure network-layer reconnaissance and exfiltration aren't detected at the network tier. We document adding Suricata as future work — being honest about this strengthens credibility.</div>
<div class="qa"><span class="q">Q: What did you personally learn / what was hard?</span><br>Real engineering: tuning the SIEM's memory to fit the host, matching agent/manager versions, getting container logs into the SIEM (containers log to files, not journald), and making a non-root, read-only container actually run. These show hands-on depth.</div>

<h2 id="limits">14. Limitations &amp; future work</h2>
<ul>
<li><b>No network IDS</b> &rarr; add Suricata to detect recon and network exfiltration.</li>
<li><b>Single host, small scale</b> &rarr; extend to Kubernetes for orchestration-level attacks.</li>
<li><b>Weak-password policy</b> mitigated by WAF/code, not by lockout/MFA &rarr; add an auth policy.</li>
<li>Add runtime syscall monitoring (Falco) for deeper container visibility.</li>
</ul>

<h2 id="cheat">15. One-page cheat sheet</h2>
<div class="box">
<p><b>What:</b> Containerised breach lab — attack, detect, investigate, harden, prove.</p>
<p><b>Roles:</b> attacker &rarr; SOC analyst &rarr; forensic examiner &rarr; incident responder &rarr; security architect &rarr; CISO.</p>
<p><b>Stack:</b> Docker, Flask app, MySQL, OpenSSH, Wazuh SIEM, ModSecurity WAF, Trivy/Hadolint/Checkov/ZAP.</p>
<p><b>Attack (9):</b> recon &rarr; brute&nbsp;force/SQLi &rarr; RCE &rarr; persistence &rarr; priv-esc &rarr; cred access &rarr; lateral &rarr; collection &rarr; exfiltration.</p>
<p><b>Frameworks:</b> MITRE ATT&amp;CK (mapping), Cyber Kill Chain (stages), NIST 800-61 (response), Zero Trust (hardening).</p>
<p><b>Detected:</b> T1021, T1059, T1078, T1110, T1190, T1505 + FIM.</p>
<p><b>Hardening:</b> WAF + micro-segmentation + non-root/cap-drop/read-only + no socket + secrets + fixed code + CI gates.</p>
<p><b>Result:</b> same attack &rarr; vulnerable = full breach; hardened = 8/8 objectives blocked.</p>
<p><b>One sentence:</b> "We weaponised, detected, investigated, and then defeated a realistic multi-stage container breach — proving that Zero-Trust hardening plus detection engineering turns a total compromise into a non-event."</p>
</div>

<p class="muted" style="margin-top:24px;text-align:center;">Generated for the Cryvion Networks major project &middot; open in a browser and use Print &rarr; Save as PDF.</p>

</body></html>
"""

html = HTML.format(
    css=CSS,
    fig_vuln=img("fig4_1_vuln_arch.png"),
    fig_attack=img("fig4_2_attack_chain.png"),
    fig_detect=img("fig4_3_detection.png"),
    fig_hardened=img("fig4_4_hardened.png"),
    fig_cicd=img("fig4_5_devsecops.png"),
)
open(OUT, "w", encoding="utf-8").write(html)
print("WROTE", OUT, "(", round(len(html) / 1024), "KB )")
