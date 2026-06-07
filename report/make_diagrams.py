"""Generate the report diagrams (PNG) for the Cryvion breach-sim major project."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

# palette
RED, BLUE, ORANGE, PURPLE, GREEN, TEAL, GREY = (
    "#e74c3c", "#2e86de", "#e67e22", "#8e44ad", "#27ae60", "#16a085", "#34495e")


def box(ax, x, y, w, h, text, fc, ec="#2c3e50", tc="white", fs=10, bold=True):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.6",
                 linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=3))
    ax.text(x, y, text, ha="center", va="center", color=tc,
            fontsize=fs, fontweight="bold" if bold else "normal", zorder=4)


def zone(ax, x, y, w, h, label, color):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=0.8",
                 linewidth=1.6, linestyle="--", edgecolor=color,
                 facecolor=color, alpha=0.08, zorder=1))
    ax.text(x - w / 2 + 1.4, y + h / 2 - 1.0, label, ha="left", va="center",
            color=color, fontsize=9, fontweight="bold", style="italic", zorder=2)


def arrow(ax, x1, y1, x2, y2, text="", color="#2c3e50", style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=16, linewidth=1.6, color=color,
                 linestyle=ls, zorder=2))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.7, text, ha="center",
                va="center", fontsize=8, color=color, zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def base(figsize, xlim, ylim, title):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color="#2c3e50", pad=12)
    return fig, ax


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", p)


# ---------------------------------------------------------------- Fig 1.1 Kill Chain
def fig_killchain():
    fig, ax = base((11, 2.6), (0, 58), (0, 10), "Fig 1.1  Cyber Kill Chain")
    stages = ["Recon", "Weaponize", "Deliver", "Exploit", "Install", "C2", "Actions\non Objectives"]
    cols = ["#5dade2", "#48c9b0", "#58d68d", "#f4d03f", "#eb984e", "#ec7063", "#a569bd"]
    x = 4
    for i, (s, c) in enumerate(zip(stages, cols)):
        box(ax, x, 5, 7, 3.2, s, c, fs=9)
        if i < len(stages) - 1:
            arrow(ax, x + 3.5, 5, x + 4.5, 5)
        x += 8
    save(fig, "fig1_1_killchain.png")


# ---------------------------------------------------------------- Fig 4.1 Vulnerable arch
def fig_vuln_arch():
    fig, ax = base((11, 7), (0, 60), (0, 42), "Fig 4.1  Vulnerable Architecture (the “before” state)")
    zone(ax, 16, 30, 30, 16, "dmz_net", RED)
    zone(ax, 40, 27, 36, 26, "internal_net", ORANGE)
    zone(ax, 30, 8, 56, 12, "monitoring (Wazuh agents + manager)", GREEN)

    box(ax, 8, 30, 12, 5, "attacker\n(nmap/hydra/sqlmap)", RED, fs=9)
    box(ax, 28, 30, 14, 6, "web-app\n(Flask portal)\nDUAL-HOMED", BLUE, fs=9)
    box(ax, 50, 34, 12, 5, "db\n(MySQL + PII)", ORANGE, fs=9)
    box(ax, 50, 22, 12, 5, "internal-svc\n(SSH backup)", PURPLE, fs=9)
    box(ax, 30, 8, 24, 5, "Wazuh SIEM  (manager / indexer / dashboard)", GREEN, fs=9)

    arrow(ax, 14, 30, 21, 30, "HTTP :8080", RED)
    arrow(ax, 35, 31, 44, 34, "SQL", BLUE)
    arrow(ax, 35, 29, 44, 23, "SSH (pivot)", BLUE)
    for sx in (28, 50, 50):
        arrow(ax, sx, 5.5 + 0, sx, 10.6 if sx == 28 else 19.5, color=GREEN, style="-|>", ls=":")
    ax.text(30, 39.5, "Design flaw: web-app bridges DMZ ↔ internal ⇒ one web compromise reaches the crown jewels",
            ha="center", fontsize=8.5, color="#922b21", style="italic")
    save(fig, "fig4_1_vuln_arch.png")


# ---------------------------------------------------------------- Fig 4.2 Attack chain -> MITRE
def fig_attack_chain():
    fig, ax = base((11, 8), (0, 100), (0, 78), "Fig 4.2  Attack Chain mapped to MITRE ATT&CK")
    stages = [
        ("1. Recon", "T1595"), ("2. Initial Access", "T1110 / T1190"),
        ("3. Execution (RCE)", "T1059"), ("4. Persistence", "T1136/T1053/T1098"),
        ("5. Priv-Esc", "T1611"), ("6. Credential Access", "T1552"),
        ("7. Lateral Movement", "T1021 / T1078"), ("8. Collection", "T1005"),
        ("9. Exfiltration", "T1041 / T1048"),
    ]
    cols = ["#e67e22", "#e74c3c", "#c0392b", "#9b59b6", "#8e44ad",
            "#2980b9", "#16a085", "#27ae60", "#2c3e50"]
    y = 70
    for i, ((name, mit), c) in enumerate(zip(stages, cols)):
        box(ax, 30, y, 40, 5.5, name, c, fs=10)
        ax.text(72, y, mit, ha="left", va="center", fontsize=9,
                color=c, fontweight="bold")
        if i < len(stages) - 1:
            arrow(ax, 30, y - 2.75, 30, y - 5.0)
        y -= 7.8
    ax.text(50, 75.5, "Driven through the web tier (attacker reaches only the DMZ)",
            ha="center", fontsize=8.5, color="#566573", style="italic")
    save(fig, "fig4_2_attack_chain.png")


# ---------------------------------------------------------------- Fig 4.3 Detection pipeline
def fig_detection():
    fig, ax = base((11, 4.2), (0, 96), (0, 24), "Fig 4.3  Detection Pipeline (Wazuh SIEM)")
    box(ax, 11, 18, 18, 6, "Log sources\nsecurity.log / auth.log\nFIM (/app/uploads,/etc)", BLUE, fs=8)
    box(ax, 11, 7, 18, 5, "Wazuh agents\n(web + internal)", BLUE, fs=8)
    box(ax, 38, 12, 18, 7, "Wazuh manager\nanalysisd + custom\nrules/decoders (MITRE)", GREEN, fs=8)
    box(ax, 64, 12, 16, 6, "Wazuh indexer\n(OpenSearch)", TEAL, fs=8)
    box(ax, 87, 12, 14, 6, "Dashboard\n(SOC view)", PURPLE, fs=8)
    arrow(ax, 20, 7, 29, 11)
    arrow(ax, 20, 18, 29, 13)
    arrow(ax, 47, 12, 56, 12, "alerts")
    arrow(ax, 72, 12, 80, 12)
    save(fig, "fig4_3_detection.png")


# ---------------------------------------------------------------- Fig 4.4 Hardened arch
def fig_hardened():
    fig, ax = base((11, 6.5), (0, 104), (0, 36), "Fig 4.4  Hardened Architecture (Zero-Trust, the “after” state)")
    for i, (lbl, col, cx) in enumerate([("edge_net", RED, 17), ("app_net", BLUE, 45),
                                        ("data_net", ORANGE, 73)]):
        zone(ax, cx, 22, 24, 18, lbl, col)
    zone(ax, 92, 22, 18, 18, "mgmt_net (isolated)", PURPLE)

    box(ax, 8, 22, 11, 5, "attacker", RED, fs=9)
    box(ax, 31, 22, 14, 6, "WAF\nModSecurity\n(OWASP CRS)", TEAL, fs=8)
    box(ax, 59, 22, 13, 6, "app\nnon-root, ro-FS\ncap_drop ALL", BLUE, fs=8)
    box(ax, 86, 22, 12, 5, "db\n(secret-based)", ORANGE, fs=8)
    box(ax, 92, 13, 13, 5, "internal-svc\n(key-only SSH)", PURPLE, fs=8)

    arrow(ax, 13.5, 22, 24, 22, "HTTP", RED)
    arrow(ax, 38, 22, 52.5, 22, "proxy", TEAL)
    arrow(ax, 65.5, 22, 80, 22, "SQL\n(secret)", BLUE)
    # blocked path app -> internal
    ax.add_patch(FancyArrowPatch((66, 19), (86, 16), arrowstyle="-|>",
                 mutation_scale=14, linewidth=1.6, color="#c0392b", linestyle=":"))
    ax.text(76, 16.2, "blocked\n(segmentation)", ha="center", fontsize=7.5, color="#c0392b")
    ax.text(52, 33.5, "No Docker socket  •  Docker secrets  •  cap_drop ALL  •  no-new-privileges  •  read-only FS",
            ha="center", fontsize=8.5, color="#1e8449", style="italic")
    save(fig, "fig4_4_hardened.png")


# ---------------------------------------------------------------- Fig 4.5 DevSecOps pipeline
def fig_devsecops():
    fig, ax = base((11, 2.8), (0, 96), (0, 11), "Fig 4.5  DevSecOps CI/CD Pipeline")
    steps = [("Commit", GREY), ("Hadolint\n(lint)", BLUE), ("Semgrep\n(SAST)", TEAL),
             ("Checkov\n(IaC)", PURPLE), ("Trivy\n(image CVE)", ORANGE),
             ("OWASP ZAP\n(DAST)", RED), ("Deploy", GREEN)]
    x = 7
    for i, (s, c) in enumerate(steps):
        box(ax, x, 5.5, 11.5, 4.2, s, c, fs=8)
        if i < len(steps) - 1:
            arrow(ax, x + 5.7, 5.5, x + 7.3, 5.5)
        x += 13
    ax.text(48, 10, "each gate fails the build on high-severity findings",
            ha="center", fontsize=8, color="#566573", style="italic")
    save(fig, "fig4_5_devsecops.png")


if __name__ == "__main__":
    fig_killchain()
    fig_vuln_arch()
    fig_attack_chain()
    fig_detection()
    fig_hardened()
    fig_devsecops()
    print("ALL DIAGRAMS DONE ->", OUT)
