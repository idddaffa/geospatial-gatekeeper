# Geospatial Data Gatekeeper
Automated QA/QC engine for spatial databases using Python (ArcPy). A Python-based tool built with **ArcPy** to automate rigorous quality control for oil and gas spatial data. This tool ensures that every feature class entering the database meets strict organizational standards.

### 🛠️ Key Features (4-Layer Validation)
1. **Naming Convention:** Uses Regex to enforce strict standardized naming.
2. **Geometry Integrity:** Checks for correct geometry types (e.g., Point for Wells).
3. **Spatial Reference:** Ensures all data uses the approved Coordinate Reference System (CRS).
4. **Attribute Schema:** Validates the existence of mandatory fields (UWI, WELL_NAME, etc.).

### ⚡ Performance Benchmarks
* **Execution Time:** 0.11 seconds for 5 SHP files.
* **Scalability:** Optimized to handle 10,000+ records in seconds using `arcpy.da.SearchCursor`.

### 📊 Deliverables
The tool automatically generates a **CSV Audit Report**, providing a clear list of "PASS/FAIL" status and specific error messages for immediate data correction.
