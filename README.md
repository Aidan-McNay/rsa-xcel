# `rsa-xcel`

Two implementations of RSA hardware accelerators, meant to be tightly coupled to a processor for speeding up encryption and decryption computations significantly. This represents a final project for Cornell University's ECE 5745: Complex Digital ASIC Design.

## Prerequisites

The hardware is implemented in Verilog, and is simulated using [Verilator](https://github.com/verilator/verilator). Specifically, the project is 
verified using [PyMTL3](https://github.com/pymtl/pymtl3), a Python framework for hardware modeling and testing.

## Algorithms

Overall, the project details 4 different algorithms

 - "Naive" RSA implementing modular exponentiation via exponentiation by squaring
 - RSA implemented using [Montgomery multiplication](https://www.ams.org/journals/mcom/1985-44-170/S0025-5718-1985-0777282-X/S0025-5718-1985-0777282-X.pdf), operating on values in `n`-residue format.
 - "Naive" RSA using a modular exponentiation hardware accelerator
 - Montgomery RSA using a modular exponentiation hardware accelerator operating on `n`-residue values

This hardware is meant to be coupled with a RISC-V processor; the code for this has been removed, as it is part of the ECE 4750/5745 courses at Cornell University, but is discussed in the accompanying 
[report](./doc/report.pdf). Overall, we can show that, compared to the naive software implementation, our hardware accelerator using Montgomery multiplication and `n`-residue values can achieve a speedup
of `20.85` for encryption, and `34.82` for decryption, largely due to the differences in the properties of the data (with various other tradeoffs in area and energy).

## Verification

All of our high-level algorithms were implemented in Python, and are contained in `algo` (this code was similarly implemented in C to run on the processor, but has similarly been removed).
Our algorithms are compared not only against each other, but against [Python's RSA module](https://pypi.org/project/rsa/), which serves as our golden model

Our hardware verification is done through PyMTL3. Here, we can re-use our functional-level models, as well as Python's RSA module, and verify our modules through comparison on a representative set of 
workloads. All individual modules are unit-tested, and tests are re-used across our two accelerators due to their modularity in having the same interface.

## Results

All of the results are collected and summarized in [the report for ECE 5745](./doc/report.pdf)
