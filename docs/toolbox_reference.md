# Toolbox Reference - Parity-QA-911

## Overview

`ParityQA.pyt` is an ArcGIS Pro Python Toolbox containing a single tool - **Road Parity Check**. It derives and compares left and right side address parity for every road segment in the input layer and writes the results to a copy in the output geodatabase.

---

## Installation

1. Clone or download the repository
2. Open ArcGIS Pro and navigate to the **Catalog** pane
3. Right-click **Toolboxes** → **Add Toolbox**
4. Browse to `ParityQA.pyt` and select it
5. The toolbox appears in the Catalog pane and the tool is ready to run

To make the toolbox permanently available across all projects, right-click it and select **Add To Favorites**.

---

## Parameters

| # | Parameter | Type | Required | Description |
|---|---|---|---|---|
| 0 | Road Segment Layer | Feature Layer | Yes | Input road polyline layer - never modified |
| 1 | From Address Left Field | Field | Yes | From address range, left side |
| 2 | To Address Left Field | Field | Yes | To address range, left side |
| 3 | From Address Right Field | Field | Yes | From address range, right side |
| 4 | To Address Right Field | Field | Yes | To address range, right side |
| 5 | Output Geodatabase | Workspace | Yes | File GDB where the output will be written |

### Field Dropdowns
All four address range field parameters are dynamically populated based on the road layer selected. All field types are shown since range fields are commonly stored as text in NG911 datasets.

### Output Geodatabase
Defaults to the current ArcGIS Pro project's default geodatabase. Must exist before running - the tool will not create it.

---

## Validation

| Check | Behaviour |
|---|---|
| Road layer geometry type | Must be **Polyline** - error shown in dialog if not |
| Output GDB exists | Must exist before running |

---

## Execution Flow

1. **Step 1** - Road layer copied to `Road_Parity_Result` in output GDB, three parity fields added
2. **Step 2** - Single cursor pass derives `Parity_L`, `Parity_R`, and `Parity_Diff` for every segment
3. **Step 3** - Results summarized in Geoprocessing messages, `Road_Parity_Result` added to active map

---

## Output

### Road_Parity_Result (Polyline)

| Field | Type | Description |
|---|---|---|
| *(all original fields)* | - | Carried over from input road layer |
| `Parity_L` | Text (20) | Left side parity: `Even`, `Odd`, `Both`, or `Undetermined` |
| `Parity_R` | Text (20) | Right side parity: `Even`, `Odd`, `Both`, or `Undetermined` |
| `Parity_Diff` | Text (10) | `Yes`, `No`, or `Unknown` |

---

## Symbology Recommendations

Symbolize `Road_Parity_Result` by `Parity_Diff`:
- `No` - green or neutral, correct alternating parity
- `Yes` - red or orange, same parity both sides, needs review
- `Unknown` - yellow or grey, missing range data

---

## Re-running the Tool

`Road_Parity_Result` is deleted and recreated on every run. Safe to re-run after correcting source data with no cleanup required.

---

## Calling from a Script
```python
import arcpy

arcpy.ImportToolbox(r"C:\path\to\ParityQA.pyt")

arcpy.ParityQA911.ParityQATool(
    road_fc       = r"C:\path\to\data.gdb\Road_Segments",
    road_fL_field = "F_Addr_L_911",
    road_tL_field = "T_Addr_L_911",
    road_fR_field = "F_Addr_R_911",
    road_tR_field = "T_Addr_R_911",
    out_gdb       = r"C:\path\to\output.gdb"
)
```

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|---|---|---|
| All segments returning `Unknown` | Wrong fields selected | Confirm the four range fields are correctly mapped |
| All segments returning `No` | Data is clean or fields are all even/all odd across dataset | Spot check a few segments manually to confirm |
| Tool errors on output GDB | GDB does not exist | Create the file GDB before running |
| Layer not added to map | No active map open | Open a map in ArcGIS Pro before running, or add the layer manually from the output GDB |

---

## Known Limitations

- Parity is derived from range numbers only - digitization direction is not used
- `Both` on either side is recorded accurately and not automatically flagged
- Enterprise geodatabases are not supported as output targets
- The map addition step requires an active map to be open in ArcGIS Pro
