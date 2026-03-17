# Parity-QA-911

ArcGIS Pro geoprocessing tool for deriving and validating left and right side address parity on road segments for NG911 dataset QA.

---

## What It Does

In a 911 road dataset, every segment carries address ranges for both the left and right side of the street. Under standard North American addressing conventions, one side of a road carries even numbers and the other carries odd numbers. When both sides of a segment carry the same parity - both even or both odd - something is wrong. Either the ranges were entered on the wrong sides, or the segment was digitized in a reversed direction causing left and right to flip.

This tool reads the address range fields on every road segment, derives the parity of each side independently, and flags any segment where the two sides don't follow the expected alternating pattern.

---

## Outputs

A single output feature class - `Road_Parity_Result` - is written to the specified output geodatabase. It is a copy of the input road layer with three fields appended:

| Field | Type | Description |
|---|---|---|
| `Parity_L` | Text (20) | Parity of the left side address range: `Even`, `Odd`, `Both`, or `Undetermined` |
| `Parity_R` | Text (20) | Parity of the right side address range: `Even`, `Odd`, `Both`, or `Undetermined` |
| `Parity_Diff` | Text (10) | `Yes` if both sides carry the same parity (suspicious), `No` if they alternate correctly, `Unknown` if either side is undetermined |

> The original input road layer is never modified. All results are written to the copy in the output geodatabase.

---

## Requirements

- ArcGIS Pro 3.x or later
- ArcPy (included with ArcGIS Pro)
- A file geodatabase containing a road segment polyline feature class with address range fields
- No additional Python packages required

---

## Installation

1. Clone or download this repository
```bash
git clone https://github.com/A-Charvin/Parity-QA-911.git
```
2. Open ArcGIS Pro and go to the **Catalog** pane
3. Right-click **Toolboxes** → **Add Toolbox**
4. Browse to `ParityQA.pyt` and add it
5. The tool will appear in your Catalog under Toolboxes

---

## Usage

### As a Geoprocessing Tool (Recommended)
1. Open the toolbox in the Catalog pane
2. Double-click **Road Parity Check**
3. Fill in the parameters:
   - Point to your road segment layer
   - Select the four address range fields from the dropdowns
   - Choose an output file geodatabase
4. Click Run
5. `Road_Parity_Result` is written to the output GDB and added to the active map automatically

### As a Notebook
A standalone notebook version (`Parity_Notebook.ipynb`) is included for direct use in ArcGIS Notebooks if you prefer to run and modify the logic interactively.

---

## Input Data Requirements

### Road Segment Layer (Polyline)
| Field | Type | Description |
|---|---|---|
| From Address Left | Text or Numeric | Start of address range, left side |
| To Address Left | Text or Numeric | End of address range, left side |
| From Address Right | Text or Numeric | Start of address range, right side |
| To Address Right | Text or Numeric | End of address range, right side |

> Field names do not need to match exactly - you select them from dropdowns when running the tool.

---

## How It Works

1. The road layer is copied to the output geodatabase - the original is never touched
2. For each segment, the left side parity is derived from the left range fields
3. The right side parity is derived from the right range fields independently
4. The two sides are compared and `Parity_Diff` is set accordingly
5. Results are written back to the copy and the layer is added to the active map

---

## Reading the Results

Symbolize `Road_Parity_Result` by `Parity_Diff`:

- `No` - left and right sides alternate correctly, segment is clean
- `Yes` - both sides carry the same parity, segment needs review
- `Unknown` - one or both sides have missing or unparseable range data

A cluster of `Yes` segments on a single street typically indicates the entire street was digitized in a reversed direction. Isolated `Yes` segments scattered across different streets are more likely individual data entry errors where ranges were entered on the wrong side.

---

## Known Limitations

- Parity is derived from address range numbers only - digitization direction is not used or trusted as a input given the inconsistencies common in real-world NG911 datasets
- `Both` on either side indicates a range that spans odd and even numbers, which occurs in some rural or non-standard addressing schemes and is not necessarily an error
- Output GDB must be a file geodatabase - enterprise geodatabases are not currently supported

---

## Documentation

| Document | Description |
|---|---|
| [Plain Language Guide](https://github.com/A-Charvin/Parity-QA-911/wiki/Plain-Language-Guide) | Concept and methodology written for all skill levels |
| [Technical Reference](https://github.com/A-Charvin/Parity-QA-911/wiki/Technical-Reference) | Algorithm, data model, and implementation details |
| [Toolbox Reference](https://github.com/A-Charvin/Parity-QA-911/wiki/Toolbox-Reference) | Parameters, validation, and troubleshooting for the `.pyt` tool |

---

## Related Tools

This tool is part of a small suite of NG911 address QA tools:

- **[Fishbone-QA-911](https://github.com/A-Charvin/Fishbone-QA-911)** - validates civic address points against road segment address ranges and produces fishbone visualization lines

---

## Contributing

Contributions are welcome. If you work in 911 GIS or municipal addressing and have suggestions for improving the parity logic or handling edge cases in non-standard addressing schemes, feel free to open an issue or submit a pull request.

---

## License

MIT License - free to use, modify, and distribute. Attribution appreciated but not required.

---

## Author

Developed for NG911 address data QA at Frontenac County, Ontario, Canada.
If you use or adapt this tool for your own municipality, feel free to open a discussion.
