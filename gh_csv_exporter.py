"""
Grasshopper CSV Parameter Exporter

Instructions:
1. Place a Python script component on your Grasshopper canvas.
2. Create two inputs on the component:
   - `Export` (Type hint: bool)
   - `CSV_File` (Type hint: str)
3. Copy and paste this script into the component.
4. Wire a Button to `Export`.
5. Wire a File Path or Panel containing the CSV path to `CSV_File`.

This script finds top-level inputs (components with no incoming wires and a custom NickName),
extracts their values or sets up reference links, and writes them to a CSV.
"""

import os
import csv
import Grasshopper as gh

def get_gh_doc():
    if 'ghenv' in globals():
        return ghenv.Component.OnPingDocument()
    if 'ghdoc' in globals():
        return ghdoc
    return None

def is_top_level(obj):
    # Check if the object is a parameter and has no incoming wires
    if isinstance(obj, gh.Kernel.IGH_Param):
        return obj.SourceCount == 0
    return False

def has_custom_nickname(obj):
    # Check if the NickName is different from the default Name
    return obj.NickName != obj.Name

def get_param_type_str(obj):
    type_name = obj.TypeName.lower()

    if "number" in type_name or "float" in type_name or "double" in type_name:
        return "float"
    elif "integer" in type_name or "int" in type_name:
        return "int"
    elif "string" in type_name or "text" in type_name:
        return "string"
    elif "boolean" in type_name or "bool" in type_name:
        return "bool"
    elif "curve" in type_name or "crv" in type_name:
        return "crv"
    elif "point" in type_name or "pt" in type_name:
        return "pt"
    elif "geometry" in type_name or "geo" in type_name:
        return "geo"
    elif "brep" in type_name:
        return "brep"
    elif "surface" in type_name or "srf" in type_name:
        return "srf"

    # Check if it's a Slider, Toggle, or Panel
    if isinstance(obj, gh.Kernel.Special.GH_NumberSlider):
        return "float" # or int based on slider type, but float is safe
    elif isinstance(obj, gh.Kernel.Special.GH_BooleanToggle):
        return "bool"
    elif isinstance(obj, gh.Kernel.Special.GH_Panel):
        return "string"

    # Default to geo for unknown types as a fallback for referenced geometry
    return "geo"

def extract_value(obj, type_str):
    # For geometry/reference types, we output the NickName as the value
    if type_str in ['crv', 'pt', 'geo', 'brep', 'srf']:
        return obj.NickName

    # For primitive types, we try to extract the value
    if isinstance(obj, gh.Kernel.Special.GH_NumberSlider):
        return str(obj.CurrentValue)
    elif isinstance(obj, gh.Kernel.Special.GH_BooleanToggle):
        return str(obj.Value)
    elif isinstance(obj, gh.Kernel.Special.GH_Panel):
        return str(obj.UserText)

    # For standard parameters, read from VolatileData or PersistentData
    if isinstance(obj, gh.Kernel.IGH_Param):
        if obj.VolatileDataCount > 0:
            first_branch = obj.VolatileData.Branches[0]
            if first_branch.Count > 0:
                # GH_Type wrappers have a Value property
                if hasattr(first_branch[0], 'Value'):
                    return str(first_branch[0].Value)
                else:
                    return str(first_branch[0])
        elif not obj.PersistentData.IsEmpty:
            first_branch = obj.PersistentData.Branches[0]
            if first_branch.Count > 0:
                if hasattr(first_branch[0], 'Value'):
                    return str(first_branch[0].Value)
                else:
                    return str(first_branch[0])

    return ""

def main():
    if 'Export' not in globals() or not Export:
        return

    if 'CSV_File' not in globals() or not CSV_File:
        print("Invalid CSV file path or CSV_File input not provided")
        return

    doc = get_gh_doc()
    if not doc:
        print("Could not find Grasshopper document context")
        return

    export_data = []
    export_data.append(["item name", "type", "value"])

    for obj in doc.Objects:
        # We look for IGH_Param (standard parameters) or Special objects (Slider, Toggle, Panel)
        is_param = isinstance(obj, gh.Kernel.IGH_Param)
        is_special = isinstance(obj, (gh.Kernel.Special.GH_NumberSlider, gh.Kernel.Special.GH_BooleanToggle, gh.Kernel.Special.GH_Panel))

        if is_param or is_special:
            if is_top_level(obj) and has_custom_nickname(obj):
                type_str = get_param_type_str(obj)
                val_str = extract_value(obj, type_str)

                name_str = obj.NickName

                # For geometry, output name as {NickName}-1
                if type_str in ['crv', 'pt', 'geo', 'brep', 'srf']:
                    name_str = "{}-1".format(name_str)

                export_data.append([name_str, type_str, val_str])

    if len(export_data) <= 1:
        print("No eligible components found to export.")
        return

    try:
        # Ensure directory exists
        dir_name = os.path.dirname(CSV_File)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(CSV_File, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(export_data)

        print("Successfully exported {} parameters to {}.".format(len(export_data) - 1, CSV_File))
    except Exception as e:
        print("Error writing to CSV: {}".format(e))

if __name__ == "__main__":
    main()
