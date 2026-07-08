# FPGA-Based-Cognitive-Radar-Waveform-Generation
# FPGA-Based NLFM Waveform Generator for Cognitive Radar

![Vivado](https://img.shields.io/badge/Vivado-2023.1-red)
![Language](https://img.shields.io/badge/Language-SystemVerilog-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![FPGA](https://img.shields.io/badge/FPGA-Zynq%20UltraScale%2B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Project Overview

This project implements a **Non-Linear Frequency Modulated (NLFM) waveform generator** for Cognitive Radar applications using a **Xilinx Zynq UltraScale+ FPGA**.

The NLFM waveform is generated offline in Python, converted into a COE (Coefficient) memory initialization file, stored inside the FPGA Block RAM using the Xilinx NLFM  Generator IP, and accessed through a custom SystemVerilog IP core.

The design demonstrates the complete FPGA implementation flow:

- Python waveform generation
- COE file generation
- Custom IP development
- Vivado IP Packaging
- IP Integrator Block Design
- FPGA synthesis and implementation
- Bitstream generation
- Hardware verification

---

## Features

-  NLFM waveform generation using Python
- Automatic COE file generation
- Custom reusable SystemVerilog IP
- IP Integrator compatible design
- FPGA implementation using Vivado 2023.1
- Hardware tested on the RealDigital AUP-ZU3 board
- Easy to integrate into larger radar signal processing systems

---

## Hardware

| Item | Description |
|------|-------------|
| FPGA Board | RealDigital AUP-ZU3 |
| FPGA Device | XCZU3EG-SFVC784-2-E |
| FPGA Family | Zynq UltraScale+ |
| Input Clock | 100 MHz |

---

## Software

- Vivado 2023.1
- Python 3.x
- NumPy
- Matplotlib

---

## Repository Structure

```
fpga-nlfm-waveform-generator
│
├── README.md
├── LICENSE
│
├── rtl/
│   ├── nlfm_waveform_gen.sv
│   └── tb_nlfm_waveform_gen.sv
│
├── coe/
│   └── nlfm_wave.coe
│
├── python/
│   ├── generate_nlfm.py
│
│   └── verify_waveform.py
│
├── constraints/
│   └── top.xdc
│
├── images/
│ 
│   ├── block_design.png 
│   └── ila_capture.png
│
└── bitstream/
    └── design_1_wrapper.bit
```

---

## System Architecture

```
Python NLFM Generator
          │
          ▼
Generate COE File
          │
          ▼
Custom NLFM IP
          │
          ▼
Vivado IP Integrator
          │
          ▼
Zynq UltraScale+ FPGA
          │
          ▼
Hardware Verification
```

---

## Design Flow

1. Generate the NLFM waveform using Python.
2. Convert waveform samples into a COE file.
3. Load the COE file into the Block Memory Generator.
4. Develop the custom `nlfm_waveform_gen` SystemVerilog module.
5. Package the design as reusable Vivado IP.
6. Create a Block Design using IP Integrator.
7. Generate HDL Wrapper.
8. Run Synthesis.
9. Run Implementation.
10. Generate Bitstream.
11. Program the FPGA.

---



---

## Hardware Verification

The design was successfully implemented on the **RealDigital AUP-ZU3 Development Board**.

Hardware verification included:

- Successful synthesis
- Successful implementation
- Successful bitstream generation
- Initialization using COE
- Custom IP integration
- Functional verification

---

## Applications

This project can be extended for:

- Cognitive Radar
- Pulse Compression Radar
- Software Defined Radar
- FPGA Signal Processing
- Digital Waveform Generation
- Radar Research

---



---

## Results

Example results include:

- Python generated NLFM waveform
- Vivado simulation waveform
- Block Design




---



### Open Vivado

Open:

```
vivado/project/
```

### Generate Output Products

Generate all IP output products.

### Run

- Synthesis
- Implementation
- Generate Bitstream

### Program FPGA

Program the generated bitstream onto the AUP-ZU3 board.

---

## Author

**Marisa Mathew**

M.Tech – VLSI & Embedded Systems

Rajagiri School of Engineering & Technology

Research Interests:

- FPGA Design
- Digital Signal Processing
- Radar Signal Processing
- Cognitive Radar
- VLSI Design
- Embedded Systems

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- Xilinx Vivado Design Suite
- AMD Xilinx IP Catalog
- RealDigital AUP-ZU3 Development Board
- Rajagiri School of Engineering & Technology
- NIT Calicut
