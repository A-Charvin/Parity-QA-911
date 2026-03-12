import arcpy
import os


class Toolbox:
    def __init__(self):
        self.label = "Parity QA 911"
        self.alias = "ParityQA911"
        self.tools = [ParityQATool]


class ParityQATool:
    def __init__(self):
        self.label = "Road Parity Check"
        self.description = (
            "Derives left and right side address parity for road segments from "
            "address range fields. Outputs a copy of the road layer with Parity_L, "
            "Parity_R, and Parity_Diff fields appended. Input layer is never modified."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):

        # 0 — Road layer
        p_road = arcpy.Parameter(
            displayName="Road Segment Layer",
            name="road_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        # 1 — From Address Left
        p_fL = arcpy.Parameter(
            displayName="From Address Left Field",
            name="road_fL_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        p_fL.parameterDependencies = ["road_fc"]

        # 2 — To Address Left
        p_tL = arcpy.Parameter(
            displayName="To Address Left Field",
            name="road_tL_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        p_tL.parameterDependencies = ["road_fc"]

        # 3 — From Address Right
        p_fR = arcpy.Parameter(
            displayName="From Address Right Field",
            name="road_fR_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        p_fR.parameterDependencies = ["road_fc"]

        # 4 — To Address Right
        p_tR = arcpy.Parameter(
            displayName="To Address Right Field",
            name="road_tR_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        p_tR.parameterDependencies = ["road_fc"]

        # 5 — Output GDB
        p_out_gdb = arcpy.Parameter(
            displayName="Output Geodatabase",
            name="out_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        p_out_gdb.filter.list = ["Local Database"]
        p_out_gdb.defaultEnvironmentName = "workspace"

        return [p_road, p_fL, p_tL, p_fR, p_tR, p_out_gdb]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        if parameters[0].altered and not parameters[0].hasError():
            desc = arcpy.Describe(parameters[0].valueAsText)
            if desc.shapeType != "Polyline":
                parameters[0].setErrorMessage(
                    "Road layer must be a Polyline feature class."
                )
        return

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------
    @staticmethod
    def get_side_parity(f_val, t_val):
        values = []
        for v in [f_val, t_val]:
            if v is not None:
                try:
                    values.append(int(float(v)))
                except:
                    pass
        if not values:
            return "Undetermined"
        parities = set("Even" if v % 2 == 0 else "Odd" for v in values)
        if parities == {"Even"}:
            return "Even"
        elif parities == {"Odd"}:
            return "Odd"
        else:
            return "Both"

    @staticmethod
    def get_diff(parity_l, parity_r):
        if parity_l == "Undetermined" or parity_r == "Undetermined":
            return "Unknown"
        return "Yes" if parity_l == parity_r else "No"

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    def execute(self, parameters, messages):
        road_fc  = parameters[0].valueAsText
        fL_fld   = parameters[1].valueAsText
        tL_fld   = parameters[2].valueAsText
        fR_fld   = parameters[3].valueAsText
        tR_fld   = parameters[4].valueAsText
        out_gdb  = parameters[5].valueAsText

        road_result = os.path.join(out_gdb, "Road_Parity_Result")

        # ------------------------------------------------------------------
        # Step 1 — Copy road layer
        # ------------------------------------------------------------------
        messages.addMessage("Step 1/3 — Copying road layer to output GDB...")
        if arcpy.Exists(road_result):
            arcpy.Delete_management(road_result)
        arcpy.CopyFeatures_management(road_fc, road_result)

        for fname, flength in [
            ("Parity_L",    20),
            ("Parity_R",    20),
            ("Parity_Diff", 10),
        ]:
            arcpy.AddField_management(road_result, fname, "TEXT", field_length=flength)

        messages.addMessage("           Road layer copied and fields added.")

        # ------------------------------------------------------------------
        # Step 2 — Run parity check
        # ------------------------------------------------------------------
        messages.addMessage("Step 2/3 — Running parity check...")

        road_fields = [
            fL_fld, tL_fld,
            fR_fld, tR_fld,
            "Parity_L", "Parity_R", "Parity_Diff"
        ]

        with arcpy.da.UpdateCursor(road_result, road_fields) as cur:
            for row in cur:
                try:
                    fL = float(row[0]) if row[0] is not None else None
                except:
                    fL = None
                try:
                    tL = float(row[1]) if row[1] is not None else None
                except:
                    tL = None
                try:
                    fR = float(row[2]) if row[2] is not None else None
                except:
                    fR = None
                try:
                    tR = float(row[3]) if row[3] is not None else None
                except:
                    tR = None

                parity_l = self.get_side_parity(fL, tL)
                parity_r = self.get_side_parity(fR, tR)
                diff     = self.get_diff(parity_l, parity_r)

                row[4] = parity_l
                row[5] = parity_r
                row[6] = diff

                cur.updateRow(row)

        messages.addMessage("           Parity check complete.")

        # ------------------------------------------------------------------
        # Step 3 — Summary and add to map
        # ------------------------------------------------------------------
        messages.addMessage("Step 3/3 — Summarizing results and adding to map...")

        total    = int(arcpy.GetCount_management(road_result)[0])
        diff_yes = 0
        diff_no  = 0
        diff_unk = 0

        with arcpy.da.SearchCursor(road_result, ["Parity_Diff"]) as cur:
            for row in cur:
                if row[0] == "Yes":
                    diff_yes += 1
                elif row[0] == "No":
                    diff_no += 1
                else:
                    diff_unk += 1

        # Add result to current map
        try:
            aprx      = arcpy.mp.ArcGISProject("CURRENT")
            active_map = aprx.activeMap
            if active_map is not None:
                active_map.addDataFromPath(road_result)
                messages.addMessage("           Road_Parity_Result added to map.")
            else:
                messages.addWarningMessage(
                    "No active map found. Add Road_Parity_Result manually from the output GDB."
                )
        except Exception as e:
            messages.addWarningMessage(
                f"Could not add layer to map: {e}. Add Road_Parity_Result manually from the output GDB."
            )

        messages.addMessage("=" * 50)
        messages.addMessage("Parity Check Complete")
        messages.addMessage("=" * 50)
        messages.addMessage(f"  Total road segments     : {total}")
        messages.addMessage(f"  Parity agrees (No diff) : {diff_no}")
        messages.addMessage(f"  Parity differs (Yes)    : {diff_yes}")
        messages.addMessage(f"  Unknown                 : {diff_unk}")
        messages.addMessage("-" * 50)
        messages.addMessage(f"  Road_Parity_Result → {road_result}")
        messages.addMessage("=" * 50)

        return