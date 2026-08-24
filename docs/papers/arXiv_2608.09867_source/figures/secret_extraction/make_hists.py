#!/usr/bin/env python3
"""Build the two Secret-Extraction bar charts from the sensitivity labels.

  main-text  pii_types.pdf        4 bars: PII / Secrets / IP / Emails
  appendix   pii_types_full.pdf   one bar per sub-category (fine taxonomy)

Counts = distinct sensitive items across all decoded sessions, deduplicated by
trace. Reads the new meta/sub schema; falls back to canon() for any legacy label.

  python3 make_hists.py            # from paper/figures/secret_extraction/
"""
import json, glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib import rcParams

rcParams["font.family"] = "serif"
rcParams["pdf.fonttype"] = 42

ROOTS = ["/is/sg2/apanfilov/trace-sources", "/is/cluster/fast/apanfilov/trace-sources"]

# Which label set to chart. `sensitivity_labels_opus48` was built on the Opus-4.8
# reconciliations (the good set); the older `sensitivity_labels` was built on the
# self-reconciliations, which are unreliable wherever the source model refused the
# reconcile task and we fell back to the raw longest decode. Do NOT mix the two:
# label_sensitive.py rglobs *_consensus.json, so pointing it at a dataset root
# picks up both folders.
LABEL_DIR = "sensitivity_labels_opus48"

# sub -> meta (mirrors label_sensitive.META_SUB, plus stray labeller variants so
# every distinct value lands in a headline meta rather than silently vanishing)
SUB2META = {
    # personal_information
    "name": "personal_information", "email": "personal_information",
    "phone": "personal_information", "address": "personal_information",
    "physical_address": "personal_information", "postcode": "personal_information",
    "date_of_birth": "personal_information", "government_id": "personal_information",
    "passport": "personal_information", "ssn": "personal_information",
    "payment_card": "personal_information",
    # credentials
    "api_key": "credentials", "token": "credentials",
    "password": "credentials", "private_key": "credentials",
    "bearer_token": "credentials", "csrf_token": "credentials",
    "access_token": "credentials", "api_identifier": "credentials",
    # ip
    "ip_address": "ip_address",
    # technical_identifier
    "url": "technical_identifier", "file_path": "technical_identifier",
    "session_id": "technical_identifier", "account_id": "technical_identifier",
    "internal_id": "technical_identifier", "internal_identifier": "technical_identifier",
    "session_identifier": "technical_identifier", "user_id": "technical_identifier",
    "domain": "technical_identifier", "hostname": "technical_identifier",
    "endpoint": "technical_identifier", "api_endpoint": "technical_identifier",
    "api_url": "technical_identifier", "website_url": "technical_identifier",
    "subdomain": "technical_identifier", "tenant_id": "technical_identifier",
    "agent_id": "technical_identifier", "trace_id": "technical_identifier",
    "job_id": "technical_identifier", "identifier": "technical_identifier",
    "port": "technical_identifier", "commit_hash": "technical_identifier",
    "id": "technical_identifier",
    "other": "other",
}


def norm(v):
    return " ".join((v or "").split()).strip().lower()

# legacy free-text -> sub, for any label not yet re-run under the new schema
def legacy_sub(t):
    t = (t or "").strip().lower().replace(" ", "_").replace("-", "_")
    if "api_key" in t or "aws" in t or "secret" in t or "credential" in t or "license_key" in t:
        return "api_key"
    if "token" in t or "jwt" in t or "bearer" in t:
        return "token"
    if "password" in t or "passwd" in t or t == "pin":
        return "password"
    if "private_key" in t or "ssh_key" in t:
        return "private_key"
    if "email" in t:
        return "email"
    if "phone" in t:
        return "phone"
    if "birth" in t or t == "dob":
        return "date_of_birth"
    if any(x in t for x in ("passport", "ssn", "national_id", "drivers", "tax_id")):
        return "government_id"
    if "card" in t or "iban" in t or "cvv" in t:
        return "payment_card"
    if "address" in t or "postal" in t or "geo" in t or "location" in t:
        return "address"
    if "name" in t and not any(x in t for x in ("user", "file", "host", "domain", "path")):
        return "name"
    if t == "ip" or "ip_address" in t:
        return "ip_address"
    if any(x in t for x in ("url", "domain", "endpoint", "hostname", "website", "repository")):
        return "url"
    if "path" in t:
        return "file_path"
    if "session" in t:
        return "session_id"
    if "account" in t or "user_id" in t:
        return "account_id"
    return "internal_id"


def sub_of(it):
    return it.get("sub") or legacy_sub(it.get("type", ""))


def load_counts():
    # Read the per-root labels.jsonl summaries (one line == one trace-block).
    # After a completed relabel these are rewritten fresh, so they are the fast,
    # authoritative source; dedup by "trace" guards against any --force leftovers.
    #
    # Counts are DISTINCT VALUES: a leaked item is counted once no matter how many
    # blocks repeat it (file paths / ids otherwise dominate). sub_v holds per-sub
    # value sets; meta_v holds per-meta value sets so meta totals dedup across subs.
    lf = []
    for r in ROOTS:
        lf += glob.glob(f"{r}/*/decoded/{LABEL_DIR}/labels.jsonl")
        lf += glob.glob(f"{r}/*/*/decoded/{LABEL_DIR}/labels.jsonl")
    lf = sorted(set(lf))
    seen = set()
    sub_v, meta_v = {}, {}
    n = 0
    for f in lf:
        try:
            lines = open(f).read().splitlines()
        except Exception:
            continue
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            if not isinstance(rec, dict):
                continue
            if str(rec.get("sensitive", "")).lower() != "yes":
                continue
            items = rec.get("items") or []
            if not items:
                continue
            key = rec.get("trace", "") or rec.get("id", "")
            if not key or key in seen:
                continue
            seen.add(key)
            n += 1
            for it in items:
                if not isinstance(it, dict):
                    continue
                nv = norm(it.get("value"))
                if not nv:
                    continue
                s = sub_of(it)
                m = SUB2META.get(s, "other")
                sub_v.setdefault(s, set()).add(nv)
                meta_v.setdefault(m, set()).add(nv)
    sub_c = {s: len(v) for s, v in sub_v.items()}
    meta_c = {m: len(v) for m, v in meta_v.items()}
    # email counted at meta level (distinct emails), split out of PII bar
    email_c = len({v for v in (sub_v.get("email") or set())})
    return sub_c, meta_c, email_c, n


def bar(ax, labels, vals, colors):
    bars = ax.bar(range(len(labels)), vals, color=colors, width=0.66, zorder=3)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.grid(True, color="#e6e3dd", linewidth=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#8a8a8a")
    ax.spines["bottom"].set_color("#8a8a8a")
    top = max(vals) if vals else 1
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + top * 0.015, str(v),
                ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, top * 1.12)


# palette shared with Fig. 2 (token_recovery) so the paper reads as one system
BLUE   = "#1f5fa8"  # ip_address
GREEN  = "#2e9e5b"  # technical_identifier
PURPLE = "#6d5dd3"  # personal_information
RED    = "#e01e5a"  # credentials
ORANGE = "#f26a1b"  # email
AMBER  = "#f4a800"  # other
GRAY   = "#c9c7c2"

# Appendix-only palette: the accepted decoded-reasoning colors. Technical IDs
# intentionally recede in gray while credentials retain the red accent.
APP_COLORS = {
    "personal_information": "#DA9C8E",
    "credentials": "#C43C45",
    "ip_address": "#27272A",
    "technical_identifier": "#B9B9B9",
    "other": "#F3DEDE",
}

PRETTY_SUB = {
    "account_id": "account identifier",
    "api_key": "API key",
    "date_of_birth": "date of birth",
    "file_path": "file or repository path",
    "government_id": "government ID",
    "internal_id": "internal identifier",
    "ip_address": "IP address",
    "payment_card": "payment card",
    "private_key": "private key",
    "session_id": "session identifier",
}


def main():
    sub_c, meta_c, emails, n = load_counts()
    print(f"deduped flagged traces: {n}")
    print("sub counts:", dict(sorted(sub_c.items(), key=lambda x: -x[1])))
    print("meta counts:", dict(sorted(meta_c.items(), key=lambda x: -x[1])))

    # ---- main text: PII / Credentials / IP / Emails (distinct values) ----
    # PII bar excludes emails (shown as their own bar); all counts meta-deduped.
    pii = meta_c.get("personal_information", 0) - emails
    secrets = meta_c.get("credentials", 0)
    ip = meta_c.get("ip_address", 0)
    labels = ["PII", "Credentials", "IP", "Email"]
    vals = [pii, secrets, ip, emails]
    colors = [PURPLE, RED, BLUE, ORANGE]
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    bar(ax, labels, vals, colors)
    ax.set_ylabel("distinct leaked items", fontsize=10)
    fig.savefig("pii_types.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("main:", dict(zip(labels, vals)), "-> pii_types.pdf")

    # ---- appendix: every sub, grouped by meta ----
    meta_order = ["personal_information", "credentials", "ip_address",
                  "technical_identifier", "other"]
    mcol = {"personal_information": PURPLE, "credentials": RED,
            "ip_address": BLUE, "technical_identifier": GREEN, "other": AMBER}
    order = []
    for m in meta_order:
        subs = [(s, v) for s, v in sub_c.items() if SUB2META.get(s) == m]
        order += sorted(subs, key=lambda x: -x[1])
    labs = [s for s, _ in order]
    vals2 = [v for _, v in order]
    cols2 = [APP_COLORS[SUB2META.get(s, "other")] for s in labs]
    pretty = [PRETTY_SUB.get(s, s.replace("_", " ")) for s in labs]

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    y = list(range(len(labs)))
    bars = ax.barh(y, vals2, color=cols2, edgecolor="white", linewidth=0.6,
                   height=0.72, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(pretty, fontsize=9.2)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.8, max(vals2) * 2.0)
    ax.set_xlabel("distinct leaked items (log scale)", fontsize=10)
    ax.xaxis.set_major_locator(ticker.FixedLocator([1, 10, 100, 1000]))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.xaxis.grid(True, which="major", color="#E8E8E4", linewidth=0.9, zorder=0)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#B9B9B9")

    for bar_obj, value in zip(bars, vals2):
        ax.text(value * 1.08, bar_obj.get_y() + bar_obj.get_height() / 2,
                f"{value:,}", ha="left", va="center", fontsize=8.8,
                color="#27272A")

    cursor = 0
    for meta in meta_order[:-1]:
        cursor += sum(1 for s in labs if SUB2META.get(s, "other") == meta)
        ax.axhline(cursor - 0.5, color="#E8E8E4", linewidth=0.8, zorder=1)

    handles = [plt.Rectangle((0, 0), 1, 1, color=APP_COLORS[m]) for m in meta_order]
    ax.legend(handles, [m.replace("_", " ") for m in meta_order],
              fontsize=8.2, frameon=False, ncol=3,
              loc="lower center", bbox_to_anchor=(0.5, 1.005))
    fig.tight_layout()
    fig.savefig("pii_types_full.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print("appendix -> pii_types_full.pdf")


if __name__ == "__main__":
    main()
