import sys
from pathlib import Path
import unittest
import tempfile
import numpy as np
from qiskit import QuantumCircuit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from qiskit_local import build_circuit, magnetization, simulate, run


class LocalCircuitTests(unittest.TestCase):
    def test_seeded_circuit(self):
        self.assertEqual(build_circuit(seed=4), build_circuit(seed=4))
        self.assertNotEqual(build_circuit(seed=4), build_circuit(seed=5))

    def test_control_endpoint(self):
        circuit = build_circuit(L=4, p=1.0)
        self.assertEqual(circuit.count_ops()["reset"], 16)
        self.assertEqual(simulate(circuit, shots=64), {"0000": 64})

    def test_scramble_endpoint(self):
        operations = build_circuit(L=4, p=0.0).count_ops()
        self.assertEqual(operations["cx"], 16)
        self.assertEqual(operations.get("reset", 0), 0)
        self.assertEqual(operations["rx"], 32)

    def test_reset_born_and_magnetization(self):
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.reset(0)
        circuit.measure_all()
        counts = simulate(circuit, shots=4096, seed=9)
        self.assertEqual(set(counts), {"00", "10"})
        self.assertLess(abs(counts["00"]/4096 - 0.5), 0.03)
        self.assertEqual(counts, simulate(circuit, shots=4096, seed=9))
        mean, variance = magnetization({"00": 10, "11": 10}, 2)
        self.assertEqual((mean, variance), (0.0, 1.0))

    def test_invalid_inputs(self):
        for kwargs in (dict(L=1), dict(p=np.nan), dict(p=2), dict(steps=0), dict(seed=-1)):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_circuit(**kwargs)
        with self.assertRaises(ValueError):
            magnetization({"02": 1}, 2)
        with self.assertRaises(ValueError):
            simulate(build_circuit(), shots=0)
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(FileExistsError):
            run(directory)


if __name__ == "__main__":
    unittest.main()
