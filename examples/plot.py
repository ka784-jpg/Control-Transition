"""Plot the included classical or local-Qiskit example output."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot(folder, output):
    folder, output = Path(folder), Path(output)
    if output.exists():
        raise FileExistsError(output)
    classical = (folder / "magnetization.csv").exists()
    file = folder / ("magnetization.csv" if classical else "circuits.csv")
    with file.open(newline="") as stream:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    if not rows or not all(np.isfinite(list(row.values())).all() for row in rows):
        raise ValueError("Missing or nonfinite data")
    noises = sorted({r["psq"] for r in rows}) if classical else [None]
    fig, axes = plt.subplots(1, len(noises), figsize=(5.0*len(noises), 3.8), squeeze=False)
    colors = ["#66459b", "#138a79", "#cc7136"]
    for ax, noise in zip(axes[0], noises):
        for color, L in zip(colors, sorted({r["L"] for r in rows})):
            selected = [r for r in rows if r["L"] == L and (not classical or r["psq"] == noise)]
            probabilities = sorted({r["p"] for r in selected})
            means, errors = [], []
            for p in probabilities:
                values = [r["mean_mz"] for r in selected if r["p"] == p]
                means.append(np.mean(values))
                errors.append(next(r["se_mz"] for r in selected if r["p"] == p) if classical
                              else np.std(values, ddof=1)/np.sqrt(len(values)))
            ax.errorbar(probabilities, means, yerr=errors, marker="o", markersize=4,
                        capsize=2, color=color, label=f"L = {int(L)}")
        ax.axvline(0.5, ls=":", color="0.6", lw=1)
        ax.set(xlabel="Control probability p", ylabel="Mean magnetization",
               ylim=(-0.1, 1.1), title=f"Single-qubit noise = {noise:g}" if classical else "Local Qiskit: ideal circuit")
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False)
    fig.suptitle("Classical bitstring example: 64 trajectories / point" if classical
                 else "12 circuits / point, 512 shots / circuit", fontsize=11)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plot(args.folder, args.output)
