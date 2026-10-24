# Paper Figures and Executable Examples

[Overview](../README.md) | [Models](MODELS.md) | [Reproducibility](REPRODUCIBILITY.md)

Figure numbers follow [arXiv:2509.18259v1](https://arxiv.org/abs/2509.18259v1).
Paper figures are collaboration results. Their presence does not imply that this
repository contains every experimental, MPS, or analytical pipeline behind them.

## Figure 7: Noise Analysis

![Figure 7](figures/fig07.png)

The supplemental noise analysis compares magnetization and fitted transition
parameters under different depolarizing error rates.

[Original PDF](figures/fig07.pdf) | [Classical source](../Classical%20Noise%20Code)
| [Runnable driver](../examples/classical.jl).

The source evolves binary configurations through reset, pair randomization, and
single-/two-bit noise updates. The driver runs those update functions and saves
the magnetization mean and standard error. It does not implement the full
finite-size fitting pipeline used for the published panels.

### Example Output

![Classical example](../examples/classical.png)

[CSV and seed metadata](../examples/expected/classical/).
Error bars come from 64 independent trajectories per point. The two panels use
single-bit error parameters 0.01 and 0.3, with the pair parameter one tenth as large.

## Figure 1: Protocol Context

![Figure 1](figures/fig01.png)

The paper's circuit and phase schematic provides context for competing
scrambling and control operations.

[Original PDF](figures/fig01.pdf) | [Qiskit circuit builder](../examples/qiskit_local.py).

The local example uses the rotations, CNOT direction choice, reset, and moving
pointer convention of the included Qiskit source. It is not the hardware circuit
submission pipeline or a simulation of every panel in this figure.

## Figure 2: Results in Context

![Figure 2](figures/fig02.png)

Published comparisons between experimental, MPS, and statistical-mechanics results.

[Original PDF](figures/fig02.pdf).
The repository's small examples measure magnetization; they do not generate
the figure's complete dataset, quantum-fluctuation analysis, or bond dimensions.

### Local Qiskit Output

![Local Qiskit example](../examples/qiskit.png)

[Counts, circuit means, and metadata](../examples/expected/qiskit/).
Error bars are standard errors across 12 independently generated circuits per
point, each with 512 shots. The dashed p=0.5 line is a visual reference, not a fit.

## Source Map

| Workflow | Code | Output |
| --- | --- | --- |
| Classical diagonal-noise trajectories | [Original Julia functions](../Classical%20Noise%20Code), [adapter](../examples/classical.jl) | Magnetization vs control probability |
| Quantum reset/scrambling circuits | [Original Qiskit source](../Qiskit%20Code), [local example](../examples/qiskit_local.py) | Shot counts and per-circuit magnetization |
| Plotting example data | [plot.py](../examples/plot.py) | Separate, reproducible example figures |

[Asset attribution and source filenames](figures/README.md).
