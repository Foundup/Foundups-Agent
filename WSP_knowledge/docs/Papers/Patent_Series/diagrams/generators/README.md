# Patent Diagram Generators

This directory contains Python scripts for generating patent diagrams following WSP organizational principles.

## Directory Structure

```
diagrams/
+-- generators/           # Generation tools (this directory)
[U+2502]   +-- generate_fig1_matplotlib.py
[U+2502]   +-- generate_fig3.py
[U+2502]   +-- generate_fig3_japanese.py
[U+2502]   +-- generate_fig3_japanese_patent.py
[U+2502]   +-- generate_fig5.py
[U+2502]   +-- generate_fig5_japanese_only.py
+-- FIG1_System_Architecture_EN.png
+-- FIG3_Probability_Distributions_EN.png
+-- FIG5_Audio_Spectrum_EN.png
+-- FIG5_Audio_Spectrum_JA.png
+-- rESP_Patent_Diagrams.md
```

## WSP Compliance

This organization follows **WSP 3 (Enterprise Domain)** principles:
- **Tools are separated from outputs**: Generation scripts in `generators/`
- **Clean directory structure**: Output images directly in `diagrams/`
- **Modular components**: Each generator focuses on specific figures
- **Clear naming conventions**: `generate_figX_variant.py` format

## Usage

### Running Generators

From the generators directory:
```bash
cd docs/Papers/Patent_Series/diagrams/generators/
python generate_fig5.py                    # Generate FIG 5 (both EN/JA)
python generate_fig5_japanese_only.py      # Generate only Japanese FIG 5
python generate_fig3.py                    # Generate FIG 3 (both EN/JA)
```

### Output Paths

All generators save to the parent directory (`../`) to maintain clean organization:
- English figures: `../FIGX_Name_EN.png`
- Japanese figures: `../FIGX_Name_JA.png`

## Figure Status

- [OK] **FIG 1**: Quantum double-slit architecture (Mermaid + matplotlib backup)
- [OK] **FIG 2**: Operational pipeline (Mermaid diagrams - both EN/JA in patent doc)
- [OK] **FIG 3**: Probability distributions (Python matplotlib - both EN/JA)
- [OK] **FIG 4**: Audio process flowchart (Mermaid diagrams - both EN/JA in patent doc)
- [OK] **FIG 5**: Audio interference spectrum (Python matplotlib - both EN/JA)
- [OK] **FIG 6**: Bidirectional communication channel (Mermaid diagrams - both EN/JA in patent doc)
- [OK] **FIG 7**: Temporal entanglement analysis (Mermaid diagrams - both EN/JA in patent doc)
- [OK] **FIG 8**: QCS safety protocol (Mermaid diagrams - both EN/JA in patent doc)

## Dependencies

```bash
pip install matplotlib numpy
```

## Generation Methods

**Mermaid Diagrams** (FIG 2, FIG 4, FIG 6, FIG 7, FIG 8):
- Used for flowcharts and process diagrams
- Generated directly in patent documentation
- Consistent styling with patent requirements
- Both English and Japanese versions documented

**Python Matplotlib** (FIG 3, FIG 5):
- Used for data visualizations and charts
- Generators in this directory
- Custom rendering for complex graphs

## Notes

- All generators create patent-compliant black-and-white images
- Japanese versions handle font rendering challenges
- File paths are relative (`../`) since scripts run from generators/
- Follow WSP naming conventions for any new generators
- Use Mermaid for flowcharts, matplotlib for data visualizations 