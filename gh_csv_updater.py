"""
Grasshopper CSV Parameter Updater

Instructions:
1. Place a Python script component on your Grasshopper canvas.
2. Create two inputs on the component:
   - `Update` (Type hint: bool)
   - `CSV_File` (Type hint: str)
3. Copy and paste this script into the component.
4. Wire a Button or Boolean Toggle to `Update`.
5. Wire a File Path or Panel containing the CSV path to `CSV_File`.

The CSV must have columns: `input name`, `type`, `value`
"""

import os
import csv
import Grasshopper as gh
import System

def get_gh_doc():
    if 'ghenv' in globals():
        return ghenv.Component.OnPingDocument()
    if 'ghdoc' in globals():
        # Depending on environment, ghdoc might be the document itself
        return ghdoc
    return None

def find_param_by_nickname(doc, nickname):
    matched_params = []
    # Search for floating parameters directly on the canvas
    for obj in doc.Objects:
        if isinstance(obj, gh.Kernel.IGH_Param):
            if obj.NickName == nickname:
                matched_params.append(obj)
    return matched_params

def update_param_value(param, type_str, value_str, doc):
    type_str = type_str.lower().strip()
    value_str = value_str.strip()

    # Handle primitives
    if type_str in ['float', 'num', 'number', 'double']:
        try:
            val = float(value_str)
            param.PersistentData.Clear()
            param.PersistentData.Append(gh.Kernel.Types.GH_Number(val))
            return True
        except ValueError:
            print("Error parsing {} as float".format(value_str))

    elif type_str in ['int', 'integer']:
        try:
            val = int(value_str)
            param.PersistentData.Clear()
            param.PersistentData.Append(gh.Kernel.Types.GH_Integer(val))
            return True
        except ValueError:
            print("Error parsing {} as int".format(value_str))

    elif type_str in ['string', 'str', 'text']:
        param.PersistentData.Clear()
        param.PersistentData.Append(gh.Kernel.Types.GH_String(value_str))
        return True

    elif type_str in ['bool', 'boolean']:
        val = value_str.lower() in ['true', '1', 't', 'yes', 'y']
        param.PersistentData.Clear()
        param.PersistentData.Append(gh.Kernel.Types.GH_Boolean(val))
        return True

    # Handle reference types (geometry, etc) where value_str is the NickName of the source
    elif type_str in ['crv', 'curve', 'pt', 'point', 'geo', 'geometry', 'brep', 'srf', 'surface']:
        source_params = find_param_by_nickname(doc, value_str)
        if not source_params:
            print("Could not find source parameter with nickname '{}' on canvas".format(value_str))
            return False

        source_param = source_params[0]

        # Wire source to this param
        param.RemoveAllSources()
        param.AddSource(source_param)
        return True

    else:
        print("Unsupported type: {}".format(type_str))
        return False

def schedule_callback(ghdoc):
    # This callback runs when the solution is finished and triggers a new one
    ghdoc.NewSolution(False)

def main():
    # Check inputs (which are provided as globals by the GH Python component)
    if 'Update' not in globals() or not Update:
        return

    if 'CSV_File' not in globals() or not CSV_File or not os.path.exists(CSV_File):
        print("Invalid CSV file path or CSV_File input not provided")
        return

    doc = get_gh_doc()
    if not doc:
        print("Could not find Grasshopper document context")
        return

    updated_count = 0

    # Read the CSV file
    with open(CSV_File, mode='r') as f:
        reader = csv.reader(f)
        # Handle python 2/3 next() compatibility
        try:
            headers = next(reader)
        except StopIteration:
            headers = None

        if not headers:
            print("Empty CSV file")
            return

        header_lower = [h.lower().strip() for h in headers]

        try:
            name_idx = header_lower.index("input name")
            type_idx = header_lower.index("type")
            value_idx = header_lower.index("value")
        except ValueError:
            print("Warning: Could not find exact headers 'input name', 'type', 'value'. Assuming columns 0, 1, 2.")
            name_idx, type_idx, value_idx = 0, 1, 2

        for row in reader:
            if len(row) <= max(name_idx, type_idx, value_idx):
                continue

            input_name = row[name_idx]
            input_type = row[type_idx]
            input_value = row[value_idx]

            target_params = find_param_by_nickname(doc, input_name)
            if not target_params:
                print("Warning: No parameter found with NickName '{}'".format(input_name))
                continue

            for param in target_params:
                # Need to record undo state if we are doing this cleanly
                param.RecordUndoEvent("CSV Update")
                if update_param_value(param, input_type, input_value, doc):
                    # Expire the parameter so it recalculates
                    param.ExpireSolution(False)
                    updated_count += 1

    if updated_count > 0:
        print("Successfully updated {} parameters.".format(updated_count))
        # Schedule a solution to evaluate the expired parameters
        delegate = gh.Kernel.GH_Document.GH_ScheduleDelegate(schedule_callback)
        doc.ScheduleSolution(5, delegate)

if __name__ == "__main__":
    main()
