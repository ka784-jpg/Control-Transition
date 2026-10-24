# Models and Interfaces

[Overview](../README.md) | [Results](RESULTS.md) | [Reproducibility](REPRODUCIBILITY.md)

## Classical Bitstring Model

Each trajectory is an L-bit configuration. Magnetization is
`M_z = 1 - 2*mean(bits)`. A moving pointer chooses the active sites.
With probability p the active bit is reset to zero and the pointer advances in
one direction; otherwise the pointer moves the opposite way and the active
pair is replaced by two independent fair bits. The source uses periodic indexing.

The noise updates act on diagonal probabilities:

- Single bit: flip with probability `psq/2`.
- Pair: keep its value with probability `1-3*ptq/4`; change to each other pair
  with probability `ptq/4`.

These are the computational-basis transition probabilities of
`rho -> (1-epsilon)*rho + epsilon*I/d` on the acted-on subsystem. They are not a
representation of a coherent state. The pair is already uniform after the
classical scrambling update, so subsequent pair depolarization preserves that
uniform distribution. A bitstring model cannot diagnose coherent interference
or entanglement merely by matching average magnetization.

```julia
include("examples/classical.jl")
result = ClassicalControl.trajectory(L=16, p=0.5, psq=0.01,
                                     ptq=0.001, steps=512, seed=2026)
result.magnetization  # Includes the initial t=0 value
result.bits          # Final binary configuration
```

The adapter loads original function definitions, omitting unused imports and
using its own seeded driver instead of the batch `runy` function. Each trajectory
resets the pointer and random initial state. The kernel uses mutable globals and
the default RNG: use serial calls or separate processes, not shared threaded calls.
The wrapper caps L at 256 and steps at 2L^2 and rejects invalid probabilities.

## Qiskit Circuit Model

```python
from examples.qiskit_local import build_circuit, simulate, magnetization
circuit = build_circuit(L=4, p=0.5, steps=16, seed=2026)
counts = simulate(circuit, shots=512, seed=29)
mean_mz, shot_variance = magnetization(counts, 4)
```

The initial state is all zero. A control operation is `reset`; a scrambling
operation applies `Rz-Rx-Rz` rotations on both active qubits and one CNOT with
random orientation. Angles are uniform in [0,2*pi). This particular angle sampler
is **not an exact Haar U(2) sampler**. The periodic ordering and gate sequence
follow the included Qiskit source; they should not be silently substituted for
another gate ensemble in a quantitative comparison.

`simulate` uses local Aer statevectors, supports reset with Born sampling,
and accepts simulator/transpiler seeds. No remote provider is initialized.
The small example has no noise model. Its `shot_variance` is the variance of
final computational-basis magnetizations, not the paper's specialized
variance-over-circuits quantum-fluctuation observable.

## Original Source Files

The two root-level files remain unchanged so existing links continue to work.
The Julia template has unused external imports and a batch-specific `runy`
interface. The Qiskit source imports legacy `IBMQ`, `execute`, and fake-provider
APIs and launches a job at top level. It is retained for source reference, not
advertised as the current runnable entry point. Use the tested examples above.

For Aer API details, see the
[official AerSimulator documentation](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html).
