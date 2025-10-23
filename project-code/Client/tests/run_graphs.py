import argparse
import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


plot_colors = ["#0e2032", "#9b1f34"]

def load_to_dataframe(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for protocol, ops in raw.items():
        if not isinstance(ops, dict):
            continue
        for txn_type, runs in ops.items():
            if not isinstance(runs, list):
                continue
            for i, pair in enumerate(runs):
                # Accept dicts or lists (robustness)
                if isinstance(pair, dict):
                    lat = pair.get("latency")
                    cpu = pair.get("cpu")
                else:
                    lat = pair[0] if len(pair) > 0 else None
                    cpu = pair[1] if len(pair) > 1 else None
                if lat is None or cpu is None:
                    continue
                rows.append(
                    {
                        "protocol": str(protocol),
                        "txn_type": str(txn_type),
                        "run_idx": i,
                        "latency": float(lat),
                        "cpu": float(cpu),
                    }
                )

    if not rows:
        raise ValueError("No valid rows parsed from JSON. Check the input format.")
    df = pd.DataFrame(rows)
    return df


def ensure_out(out_dir):
    os.makedirs(out_dir, exist_ok=True)


def savefig(path):
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def grouped_bar(ax, categories, series_dict, title, ylabel):
    """
    categories: list of category labels on x (e.g., txn_types)
    series_dict: {series_name -> list of values aligned with categories}
    """
    x = np.arange(len(categories))
    n_series = len(series_dict)
    width = min(0.8 / max(n_series, 1), 0.25)

    for idx, (name, vals) in enumerate(series_dict.items()):
        ax.bar(x + (idx - (n_series - 1) / 2) * width, vals, width=width, label=name, color=plot_colors[idx])

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=20, ha="right")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)


# ----------------------------
# Plots
# ----------------------------
def plot_avg_bar(df, metric, out_dir):
    """Bar — Average metric per Protocol per Transaction Type"""
    metric_label = "Latency (s)" if metric == "latency" else "CPU (%)"
    # pivot into categories=txn_type, series=protocol
    cats = sorted(df["txn_type"].unique())
    series = {}
    for proto in sorted(df["protocol"].unique()):
        vals = []
        for t in cats:
            subset = df[(df["protocol"] == proto) & (df["txn_type"] == t)][metric]
            vals.append(subset.mean() if not subset.empty else np.nan)
        series[proto] = vals

    fig, ax = plt.subplots(figsize=(10, 6))
    grouped_bar(ax, cats, series, f"Average {metric_label} by Protocol & Transaction", metric_label)
    savefig(os.path.join(out_dir, f"bar_avg_{metric}.png"))


def plot_box(df, metric, out_dir):
    """Box plot — distribution per Protocol, separated by transaction type (one file per txn_type)."""
    metric_label = "Latency (s)" if metric == "latency" else "CPU (%)"
    for t in sorted(df["txn_type"].unique()):
        sub = df[df["txn_type"] == t]
        if sub.empty:
            continue
        # Ensure consistent protocol order
        protos = sorted(sub["protocol"].unique())
        data = [sub[sub["protocol"] == p][metric].values for p in protos]

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.boxplot(data, labels=protos, showmeans=True)
        ax.set_title(f"{metric_label} Distribution by Protocol — {t}")
        ax.set_ylabel(metric_label)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        savefig(os.path.join(out_dir, f"box_{metric}_{t}.png"))


def plot_scatter_tradeoff(df, out_dir):
    """Scatter — Latency vs CPU, color by protocol, marker by txn_type."""
    protos = sorted(df["protocol"].unique())
    txns = sorted(df["txn_type"].unique())

    # cycles
    colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1", "C2", "C3", "C4", "C5"])
    markers = ["o", "s", "^", "D", "P", "X", "*", "v", "<", ">", "h"]
    colors[0] = plot_colors[0]
    colors[1] = plot_colors[1]
    proto_to_color = {p: colors[i % len(colors)] for i, p in enumerate(protos)}
    txn_to_marker = {t: markers[i % len(markers)] for i, t in enumerate(txns)}
    
    fig, ax = plt.subplots(figsize=(9, 7))
    for p in protos:
        for t in txns:
            sub = df[(df["protocol"] == p) & (df["txn_type"] == t)]
            if sub.empty:
                continue
            ax.scatter(
                sub["latency"],
                sub["cpu"],
                label=f"{p} • {t}",
                marker=txn_to_marker[t],
                edgecolor="white",
                linewidths=0.5,
                s=60,
                c=proto_to_color[p],
                alpha=0.8,
            )

    ax.set_title("Latency vs CPU — Trade-off (points = individual runs)")
    ax.set_xlabel("Latency (s)")
    ax.set_ylabel("CPU (%)")
    # Make a compact legend
    handles, labels = ax.get_legend_handles_labels()
    # Reduce legend clutter by grouping: one legend per protocol and one for markers
    # Protocol legend
    from matplotlib.lines import Line2D

    proto_handles = [Line2D([0], [0], marker="o", color=proto_to_color[p], linestyle="", label=p) for p in protos]
    marker_handles = [Line2D([0], [0], marker=txn_to_marker[t], color="gray", linestyle="", label=t) for t in txns]

    leg1 = ax.legend(handles=proto_handles, title="Protocol", frameon=False, loc="upper left")
    ax.add_artist(leg1)
    ax.legend(handles=marker_handles, title="Transaction", frameon=False, loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.3)
    savefig(os.path.join(out_dir, "scatter_latency_vs_cpu.png"))


def plot_heatmap(df, metric, out_dir):
    """Heatmap — Average metric (rows=protocols, cols=txn types)"""
    metric_label = "Latency (s)" if metric == "latency" else "CPU (%)"
    pivot = (
        df.groupby(["protocol", "txn_type"])[metric]
        .mean()
        .unstack("txn_type")
        .reindex(index=sorted(df["protocol"].unique()), columns=sorted(df["txn_type"].unique()))
    )

    fig, ax = plt.subplots(figsize=(1.5 + 1.1 * pivot.shape[1], 1.5 + 0.7 * pivot.shape[0]))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_title(f"Average {metric_label} Heatmap")
    ax.set_xticks(np.arange(pivot.shape[1]))
    ax.set_yticks(np.arange(pivot.shape[0]))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticklabels(pivot.index)


    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            if np.isfinite(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=metric_label)
    savefig(os.path.join(out_dir, f"heatmap_avg_{metric}.png"))


def plot_dual_axis_per_txn(df, out_dir):
    """Dual-axis — For each transaction type, plot average latency (left) and CPU (right) across protocols."""
    for t in sorted(df["txn_type"].unique()):
        sub = df[df["txn_type"] == t]
        if sub.empty:
            continue
        agg = sub.groupby("protocol").agg(latency=("latency", "mean"), cpu=("cpu", "mean")).reset_index()
        agg = agg.sort_values("protocol")
        x = np.arange(len(agg))

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        w = 0.35
        ax1.bar(x - w / 2, agg["latency"], width=w, label="Latency (s)")
        ax2.bar(x + w / 2, agg["cpu"], width=w, label="CPU (%)")

        ax1.set_xticks(x)
        ax1.set_xticklabels(agg["protocol"], rotation=20, ha="right")
        ax1.set_title(f"Average Latency & CPU by Protocol — {t}")
        ax1.set_ylabel("Latency (s)")
        ax2.set_ylabel("CPU (%)")
        ax1.grid(axis="y", linestyle="--", alpha=0.3)

        # Build a combined legend
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper right")

        savefig(os.path.join(out_dir, f"dual_axis_{t}.png"))


# ----------------------------
# Main
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate performance graphs from experiment JSON.")
    parser.add_argument("input_json", help="Path to input JSON file")
    parser.add_argument(
        "-o", "--out", default="charts_output", help="Directory to write PNG charts (default: charts_output)"
    )
    args = parser.parse_args()

    ensure_out(args.out)
    df = load_to_dataframe(args.input_json)

    # Basic summary CSV (optional but handy)
    summary = (
        df.groupby(["protocol", "txn_type"])
        .agg(avg_latency=("latency", "mean"), p95_latency=("latency", lambda s: s.quantile(0.95)),
             avg_cpu=("cpu", "mean"), p95_cpu=("cpu", lambda s: s.quantile(0.95)),
             n_runs=("latency", "size"))
        .reset_index()
    )
    summary_path = os.path.join(args.out, "summary.csv")
    summary.to_csv(summary_path, index=False)

    # Plots
    plot_avg_bar(df, "latency", args.out)
    plot_avg_bar(df, "cpu", args.out)

    plot_box(df, "latency", args.out)
    plot_box(df, "cpu", args.out)

    plot_scatter_tradeoff(df, args.out)

    plot_heatmap(df, "latency", args.out)
    plot_heatmap(df, "cpu", args.out)

    plot_dual_axis_per_txn(df, args.out)

    print(f"Done. Charts written to: {os.path.abspath(args.out)}")
    print(f"Summary CSV: {os.path.abspath(summary_path)}")


if __name__ == "__main__":
    main()
