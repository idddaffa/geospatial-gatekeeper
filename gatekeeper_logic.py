import arcpy
import os
import re
import csv
import datetime

def run_qc(input_folder, output_folder):
    arcpy.env.workspace = input_folder
    fcs = arcpy.ListFeatureClasses()
    
    if not fcs:
        arcpy.AddError("Empty folder or no shapefile/feature class found!")
        return

    # --- STRICT RULES FOR WELLS DATA ---
    REGEX_PATTERN = r"^[A-Za-z0-9]+_\d{4}_WELLS$"
    REQUIRED_GEOMETRY = "Point"
    REQUIRED_FIELDS = ["UWI", "WELL_NAME", "CLASS", "OPERATOR", "LONGITUDE", "LATITUDE"]

    report_data = []
    arcpy.SetProgressor("step", "Initializing Wells Data QC process...", 0, len(fcs), 1)

    for fc in fcs:
        filename = os.path.splitext(fc)[0]
        arcpy.SetProgressorLabel(f"Scanning: {filename}...")
        
        status = "PASS"
        issues = []
        
        # --- CHECK 1: NAMING CONVENTION ---
        if not re.match(REGEX_PATTERN, filename, re.IGNORECASE):
            status = "FAIL"
            issues.append("Invalid Naming Format (Required: WK_YEAR_WELLS)")
            
        # --- CHECK 2: GEOMETRY ---
        desc = arcpy.Describe(fc)
        if desc.shapeType != REQUIRED_GEOMETRY:
            status = "FAIL"
            issues.append(f"Invalid Geometry (Required: {REQUIRED_GEOMETRY}, Actual: {desc.shapeType})")
                    
        # --- CHECK 3: COORDINATE SYSTEM ---
        sr_name = desc.spatialReference.name
        if sr_name == "Unknown":
            status = "FAIL"
            issues.append("Unknown Coordinate System")

        # --- CHECK 4: ATTRIBUTE TABLE ---
        if desc.shapeType == REQUIRED_GEOMETRY:
            existing_fields = [f.name.upper() for f in arcpy.ListFields(fc)]
            missing_fields = []
            null_issues = []
            
            # A. Check for Required Fields
            for req_field in REQUIRED_FIELDS:
                if req_field.upper() not in existing_fields:
                    missing_fields.append(req_field)
            
            if missing_fields:
                status = "FAIL"
                issues.append(f"Missing Attribute Fields: {', '.join(missing_fields)}")
            else:
                # B. Check for Null/Empty Data
                try:
                    with arcpy.da.SearchCursor(fc, REQUIRED_FIELDS) as cursor:
                        for row_index, row in enumerate(cursor):
                            for col_index, val in enumerate(row):
                                if val is None or str(val).strip() == "":
                                    null_issues.append(f"Row {row_index+1} ({REQUIRED_FIELDS[col_index]} is Null/Empty)")
                                    status = "FAIL"
                except Exception as e:
                    issues.append(f"Failed to read table: {str(e)}")
                    status = "FAIL"
                    
            # Display all errors without limit
            if null_issues:
                error_summary = ", ".join(null_issues)
                issues.append(f"Null Data Detected: [{error_summary}]")

        # --- SAVE RESULTS ---
        final_note = " | ".join(issues) if issues else "Data Clean & Compliant"
        report_data.append([filename, desc.shapeType, sr_name, status, final_note])
        
        if status == "PASS":
            arcpy.AddMessage(f"[OK] {filename}")
        else:
            arcpy.AddWarning(f"[FAIL] {filename} -> {final_note}")
            
        arcpy.SetProgressorPosition()

    # --- GENERATE CSV REPORT ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_folder, f"QC_Wells_Report_{timestamp}.csv")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File Name", "Geometry Type", "Coordinate System", "QC STATUS", "Error Notes"])
        writer.writerows(report_data)
        
    arcpy.AddMessage(f"\n--- WELLS QC PROCESS COMPLETED ---")
    arcpy.AddMessage(f"Audit Report saved at: {csv_path}")

if __name__ == "__main__":
    in_folder = arcpy.GetParameterAsText(0)
    out_folder = arcpy.GetParameterAsText(1)
    run_qc(in_folder, out_folder)
