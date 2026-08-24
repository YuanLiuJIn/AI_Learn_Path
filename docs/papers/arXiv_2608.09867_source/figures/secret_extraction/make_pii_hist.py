import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.family"] = "serif"
rcParams["pdf.fonttype"] = 42

cats = ["PII", "Technical\nidentifiers", "Credentials"]  # sorted big -> small
# All sources (synthetic incl.), distinct real values -- the deduplication stage
# of tab:leak_funnel, using the same grouping as that table:
#   PII         = name, address, email, date of birth, government ID, payment card, phone
#   technical   = IP address, URL, file/repo path, internal/account/session identifier
#   credentials = access token, API key, password, private key
# (the taxonomy's "other" bucket, 29 values, is not plotted; 367+363+182+29 = 941)
vals = [367, 363, 182]
# Match the accepted decoded-reasoning palette used in Appendix D:
# personal information = salmon, technical identifiers = neutral gray,
# credentials = red accent.
PERSONAL, TECHNICAL, CREDENTIALS = "#DA9C8E", "#B9B9B9", "#C43C45"
PANEL_GRID, PANEL_BORDER, PANEL_INK = "#E8E8E4", "#B9B9B9", "#27272A"
colors = [PERSONAL, TECHNICAL, CREDENTIALS]  # Credentials incl. API keys

fig, ax = plt.subplots(figsize=(4.2, 2.7))
bars = ax.bar(range(len(cats)), vals, color=colors, width=0.6, zorder=3)
ax.set_ylim(0, 410)
ax.set_ylabel("distinct leaked items", fontsize=10)
ax.set_xticks(range(len(cats)))
ax.set_xticklabels(cats, fontsize=9.5)
ax.tick_params(axis="x", length=0)
ax.tick_params(axis="y", labelsize=9)
ax.yaxis.grid(True, color=PANEL_GRID, linewidth=0.8, zorder=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.spines["left"].set_color(PANEL_BORDER)
ax.spines["bottom"].set_color(PANEL_BORDER)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 7, str(v),
            ha="center", va="bottom", fontsize=9.5, color=PANEL_INK)
fig.savefig("figures/secret_extraction/pii_types.pdf", bbox_inches="tight", pad_inches=0.02)
print("wrote figures/secret_extraction/pii_types.pdf")
