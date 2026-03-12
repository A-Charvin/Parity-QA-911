# Technical Reference - Parity-QA-911

## Architecture Overview

The tool operates entirely on the road layer and produces a single output feature class. There are no spatial operations, no secondary inputs, and no geometry processing - parity is derived purely from the address range attribute fields. This makes the tool fast, deterministic, and fully independent of digitization direction reliability.

Execution follows a simple two-phase architecture:

1. **Copy phase** - road layer is copied to the output GDB and parity fields are added
2. **Parity phase** - a single UpdateCursor pass derives and writes all three parity fields

---

## Parity Derivation Logic

### Per-Side Parity

For each side (left and right), parity is derived from the from and to address values:
```
Parse f_val and t_val to int via float cast
Collect successfully parsed values into a list
If list is empty                          → Undetermined
If all values are even (v % 2 == 0)       → Even
If all values are odd  (v % 2 != 0)       → Odd
If mix of even and odd                    → Both
```

The `Both` case occurs when a segment's range spans both odd and even numbers, which is valid in some non-standard addressing schemes. It is recorded accurately rather than treated as an error.

### Diff Logic
```
If Parity_L == Undetermined or Parity_R == Undetermined → Unknown
If Parity_L == Parity_R                                 → Yes  (suspicious)
If Parity_L != Parity_R                                 → No   (correct)
```

`Yes` indicates both sides carry the same parity, which violates the standard alternating convention and warrants review. `No` indicates the sides alternate, which is the expected and correct pattern.

---

## Data Model

### Input
| Field | Type | Notes |
|---|---|---|
| From Address Left | Text or Numeric | Cast to float at runtime |
| To Address Left | Text or Numeric | Cast to float at runtime |
| From Address Right | Text or Numeric | Cast to float at runtime |
| To Address Right | Text or Numeric | Cast to float at runtime |

### Output - Road_Parity_Result
All fields from the input road layer are carried over. Three fields are appended:

| Field | Type | Values |
|---|---|---|
| `Parity_L` | Text (20) | `Even`, `Odd`, `Both`, `Undetermined` |
| `Parity_R` | Text (20) | `Even`, `Odd`, `Both`, `Undetermined` |
| `Parity_Diff` | Text (10) | `Yes`, `No`, `Unknown` |

---

## Cursor Strategy

A single `UpdateCursor` on `Road_Parity_Result` handles the entire parity derivation in one pass. No `SearchCursor` on a secondary dataset, no nested cursors, no in-memory structures required. The range fields and parity output fields are read and written in the same cursor row.

All cursors are opened with context managers to guarantee release on completion or error.

---

## Error Handling

| Condition | Behaviour |
|---|---|
| Range field is `None` | Value excluded from parity calculation silently |
| Range field cast to float fails | Value excluded from parity calculation silently |
| Both range fields on one side fail | That side returns `Undetermined` |
| Either side is `Undetermined` | `Parity_Diff` returns `Unknown` |
| No active map when tool runs | Warning message issued, layer not added to map, execution continues |

All data quality failures are handled defensively. The tool runs to completion across the full dataset regardless of how many individual range fields are missing or malformed.

---

## Add to Map

After writing results, the toolbox version attempts to add `Road_Parity_Result` to the active map using `arcpy.mp.ArcGISProject("CURRENT")`. If no active map is found or the operation fails for any reason, a warning message is issued and execution completes normally. The output is always written to the GDB regardless of whether the map addition succeeds.

---

## Performance

The tool requires a single full scan of the road dataset with no secondary reads. Runtime is O(n) where n is the number of road segments. No geometry is accessed. For a typical municipal road dataset of several thousand segments the tool runs in seconds.

---

## Known Constraints

- **No geometry used** - parity is derived from attribute fields only. Digitization direction is not consulted and does not affect results.
- **Text range fields** - range values stored as text are cast to float at runtime. Non-numeric content is excluded silently.
- **Both is not an error** - segments where a side spans odd and even numbers are recorded as `Both` without being flagged. These require human judgment to assess.
- **Output GDB must be a file GDB** - enterprise geodatabases are not supported as output targets.
