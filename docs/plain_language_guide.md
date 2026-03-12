# Plain Language Guide - Parity-QA-911

## What Is Address Parity?

In North American municipal addressing, house numbers are not assigned randomly. Streets follow a convention where one side carries even numbers and the other carries odd numbers. Drive down a typical residential street and the left side might have houses numbered 100, 102, 104 while the right side has 101, 103, 105. This alternating pattern is called address parity, and it's one of the foundational rules that makes street addressing consistent and navigable.

In a 911 road dataset, every road segment stores this information explicitly through address range fields - four numbers that declare what the lowest and highest address is on each side of that segment. The parity of each side is directly readable from those numbers: if the left side runs from 100 to 198, it's an even side. If the right side runs from 101 to 199, it's an odd side.

---

## What Goes Wrong

The problem this tool is designed to find is when both sides of a road segment carry the same parity. If the left side is even and the right side is also even, the standard alternating convention has broken down somewhere. In practice this usually means one of two things:

The address ranges were entered on the wrong sides during data creation or editing. Someone put the even ranges in the left fields and the even ranges in the right fields when one of those should have been odd. This is a data entry error and the fix is straightforward once you know which segments are affected.

The segment was digitized in the wrong direction. Road segments have a from-end and a to-end, and left and right are defined relative to which direction you're travelling along the segment. If a segment was digitized in the opposite direction to the rest of its street, its left and right sides are flipped, which can make correctly entered ranges appear to be on the wrong sides. This is a geometry issue rather than an attribute issue.

Both cause the same symptom in the data - same parity on both sides - which is exactly what this tool detects.

---

## What the Tool Checks

For every road segment the tool reads the four address range fields and works out the parity of each side independently:

- If both the from and to address on the left side are even, the left side is even
- If both are odd, the left side is odd
- If one is odd and one is even, the left side is recorded as Both - which happens in some rural or non-standard addressing schemes and isn't necessarily wrong
- If the range fields are empty or contain values that can't be read as numbers, the side is recorded as Undetermined

The same logic runs for the right side. Then the two sides are compared. If they match - both even or both odd - the segment is flagged. If they alternate correctly, it's clean. If either side couldn't be determined, the result is recorded as Unknown rather than making a guess.

---

## What Gets Created

The tool produces a single output - a copy of your road layer called `Road_Parity_Result` - with three new fields:

**Parity_L** records the parity of the left side: `Even`, `Odd`, `Both`, or `Undetermined`.

**Parity_R** records the parity of the right side using the same values.

**Parity_Diff** is the summary flag: `Yes` means both sides carry the same parity and the segment needs review, `No` means the sides alternate correctly, and `Unknown` means one or both sides couldn't be determined from the range data.

Your original road layer is never touched. The results go to the copy only.

---

## How to Read the Results

Symbolize `Road_Parity_Result` by `Parity_Diff` and the problem segments stand out immediately.

A cluster of `Yes` segments running along a single street is the clearest signal that the whole street was digitized in a reversed direction. Every segment on that street will show the same symptom because the direction flip affects all of them consistently. The fix in that case is to reverse the digitization direction of those segments and swap the left and right range values to match.

Isolated `Yes` segments scattered across different streets with no geographic pattern are more likely individual data entry errors - someone entered the even ranges on the right side and the odd ranges on the left side for that particular segment. Those need to be corrected one by one.

Segments showing `Both` on either side aren't necessarily wrong. Rural roads, industrial areas, and some older addressing schemes don't always follow strict odd/even conventions. These are worth a second look but shouldn't be treated as automatic errors.

`Unknown` segments have missing or unparseable range data and need attention regardless of parity - if the range fields are empty or contain non-numeric values, the addressing data for that segment is incomplete.

---

## What This Tool Does Not Fix

The tool identifies parity problems - it doesn't resolve them. Correcting the underlying issues requires manual work in the road dataset, either fixing range values that were entered on the wrong sides or correcting segment digitization direction. The `Parity_Diff` field tells you which segments need attention and the `Parity_L` and `Parity_R` fields give you the context to understand what specifically is wrong with each one.

---

## Re-running the Tool

The tool is safe to re-run at any time. `Road_Parity_Result` is deleted and rebuilt from scratch on every run, so correcting issues in the source road data and re-running always gives you a fresh result reflecting the current state of the dataset.
