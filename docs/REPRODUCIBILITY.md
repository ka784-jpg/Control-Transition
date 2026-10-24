# Reproducibility and Tests

[Overview](../README.md) | [Models](MODELS.md) | [Results](RESULTS.md)

## Reproduce the Examples

The README commands run the same bounded sweeps used for the checked-in plots.
Use a fresh output directory for each run. Plotters also refuse to overwrite
files. Saved data include model parameters, seeds, versions, and source hashes.

- Classical: Julia 1.12.6, standard libraries only, L=8,16,32; two noise settings;
  p=0,0.1,...,1; 64 trajectories per point; 2L^2 updates.
- Qiskit: Python 3.12, pinned direct dependencies; L=4,6; p=0.25,0.5,0.75;
  12 circuits per point; L^2 operations; 512 shots per circuit. All simulation is local.

`examples/expected/classical/` contains `magnetization.csv` and `metadata.toml`.
`examples/expected/qiskit/` contains per-circuit results, raw shot counts, and
`metadata.json`. Reproducing a statistical trend is distinct from exact bitwise
reproduction across library versions and platforms.

## Test Coverage

```sh
julia --project=. --startup-file=no tests/runtests.jl
python -m unittest discover -s tests -p test_qiskit.py -v
python tests/integrity.py --plots
```

Julia tests check magnetization bounds, binary states, seeded repeatability,
the fully controlled noiseless endpoint, pointer wraparound, and single-/two-bit
depolarizing probabilities against their analytical values. Python tests check
circuit reproducibility, operation counts at control/scrambling endpoints,
Born-reset probabilities for a Bell state, observable calculations, invalid
inputs, and output protection. Integrity tests check original source hashes,
figure hashes, local documentation links, saved CSVs, and plotting commands.

GitHub Actions runs on Windows and Linux. It executes both examples as well as
their tests. No IBM account or hardware credentials are used.

## Limits

The examples are small reproducibility checks, not precision finite-size fits.
There is no bundled hardware shot campaign, MPS engine, device calibration,
or complete experimental data-analysis pipeline. Paper figures are included as
attributed scientific context and are clearly separated from the generated
example plots. The source map identifies what each workflow actually computes.
