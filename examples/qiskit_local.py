"""Seeded adaptive reset/scrambling circuits on a local Aer simulator."""
import argparse
import csv
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import tempfile
import shutil

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def build_circuit(L=4, p=0.5, *, steps=None, seed=2026):
    if isinstance(L, bool) or not isinstance(L, int) or not 2 <= L <= 10:
        raise ValueError("L must be an integer from 2 to 10")
    if not np.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("p must be finite and in [0,1]")
    steps = L * L if steps is None else steps
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 2 * L * L:
        raise ValueError("steps must be an integer from 1 to 2*L^2")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**31:
        raise ValueError("seed must be a nonnegative 32-bit integer")
    rng = np.random.default_rng(seed)
    circuit = QuantumCircuit(L)
    order = list(reversed(range(L)))
    for _ in range(steps):
        if rng.random() < p:
            circuit.reset(order[0])
            order = order[1:] + order[:1]
        else:
            order = order[-1:] + order[:-1]
            angles = rng.uniform(0, 2 * np.pi, 6)
            for j in range(2):
                circuit.rz(angles[3*j], order[j])
                circuit.rx(angles[3*j+1], order[j])
                circuit.rz(angles[3*j+2], order[j])
            a, b = order[:2]
            circuit.cx(a, b) if rng.random() < 0.5 else circuit.cx(b, a)
    circuit.measure_all()
    return circuit


def magnetization(counts, L):
    if not counts or L < 1:
        raise ValueError("counts and a positive width are required")
    total, first, second = 0, 0.0, 0.0
    for key, n in counts.items():
        bits = key.replace(" ", "")
        if len(bits) != L or set(bits) - {"0", "1"} or not isinstance(n, int) or n <= 0:
            raise ValueError("invalid bitstring counts")
        mz = 1 - 2 * bits.count("1") / L
        total += n
        first += n * mz
        second += n * mz * mz
    mean = first / total
    return mean, max(0.0, second / total - mean * mean)


def simulate(circuit, *, shots=512, seed=2026):
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= 100000:
        raise ValueError("shots must be an integer from 1 to 100000")
    backend = AerSimulator(method="statevector", max_parallel_threads=1)
    compiled = transpile(circuit, backend, seed_transpiler=seed, optimization_level=0)
    return backend.run(compiled, shots=shots, seed_simulator=seed).result().get_counts()


def run(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(dir=output.parent))
    try:
        rows, records = [], []
        for L in (4, 6):
            for index, p in enumerate((0.25, 0.5, 0.75)):
                for realization in range(12):
                    seed = 2026 + 10000 * L + 100 * index + realization
                    circuit = build_circuit(L, p, seed=seed)
                    counts = simulate(circuit, shots=512, seed=seed+1000000)
                    mean, variance = magnetization(counts, L)
                    rows.append([L, p, realization, seed, 512, mean, variance])
                    records.append(dict(L=L, p=p, realization=realization, counts=counts))
        with (stage / "circuits.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["L", "p", "realization", "seed", "shots", "mean_mz", "shot_variance"])
            writer.writerows(rows)
        (stage / "counts.json").write_text(json.dumps(records, indent=2) + "\n")
        metadata = dict(qiskit=version("qiskit"), aer=version("qiskit-aer"), numpy=version("numpy"),
                        steps="L^2", initial_state="all zero", noise="none; local ideal Aer",
                        circuits_per_point=12, shots=512, seed_base=2026,
                        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        (stage / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(f"Saved local Qiskit results to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    run(parser.parse_args().output)
