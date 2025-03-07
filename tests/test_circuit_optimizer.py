# MIT License
#
# Copyright (c) 2022 Quandela
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import Callable

from perceval.utils.algorithms.circuit_optimizer import CircuitOptimizer
from perceval.utils.algorithms import norm
from perceval.components import BS, PS, Circuit
from perceval.utils import P, Matrix

import pytest


perfect_theta = BS.r_to_theta(r=.5)

def _ps(i):
    return PS(P(f"phi_3_{i}"))


def _check_optimize(size: int, mzi_func: Callable[[int], None]):
    circuit_optimizer = CircuitOptimizer()
    template_interferometer = Circuit.generic_interferometer(size, mzi_func,
                                                             phase_shifter_fun_gen=_ps,
                                                             phase_at_output=True)
    random_unitary = Matrix.random_unitary(size)
    result_circuit, fidelity = circuit_optimizer.optimize(random_unitary, template_interferometer)
    assert 1 - fidelity < circuit_optimizer.threshold
    assert norm.fidelity(result_circuit.compute_unitary(), random_unitary) == pytest.approx(fidelity)

def test_circuit_optimizer():
    def mzi(i):
        return Circuit(2) // PS(P(f"phi_1_{i}")) // BS.Rx(perfect_theta) \
            // PS(P(f"phi_2_{i}")) // BS.Rx(perfect_theta)

    for size in range(6, 17, 2):
        _check_optimize(size, mzi)


def test_circuit_optimizer_bs_convention():
    for bs_ctor in [BS.Ry, BS.H]:
        def mzi_conv(i):
            return Circuit(2) // PS(P(f"phi_1_{i}")) // bs_ctor(perfect_theta) \
                // PS(P(f"phi_2_{i}")) // bs_ctor(perfect_theta)

        _check_optimize(12, mzi_conv)
