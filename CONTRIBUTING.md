# Contributing

Please describe the model, parameter choices, and expected numerical behavior in
issues or pull requests. Include a small seeded reproduction and package versions.

Run the Julia tests, local Qiskit tests, and integrity checks documented in the
[reproducibility guide](docs/REPRODUCIBILITY.md). Add focused tests for changes to
noise channels, pointer conventions, reset behavior, or observable definitions.

Keep the original source files intact. Extend the supported examples or add a
clearly documented module. Do not commit credentials, hardware tokens, private
data, generated virtual environments, or large simulation campaigns. Paper assets
must retain their scientific attribution and separate licensing.
