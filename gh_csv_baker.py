"""
Grasshopper CSV Baker

Instructions:
1. Place a Python script component on your Grasshopper canvas.
2. Create two inputs on the component:
   - `Bake` (Type hint: bool)
   - `CSV_File` (Type hint: str)
3. Copy and paste this script into the component.
4. Wire a Button to `Bake`.
5. Wire a File Path or Panel containing the CSV path to `CSV_File`.

The CSV must have columns: `item name`, `layer`, `color`
"""

import os
import csv
import random
import Grasshopper as gh
import Rhino
import System

def get_gh_doc():
    if 'ghenv' in globals():
        return ghenv.Component.OnPingDocument()
    if 'ghdoc' in globals():
        return ghdoc
    return None

def find_params_by_nickname(gh_doc, nickname):
    matched = []
    for obj in gh_doc.Objects:
        if isinstance(obj, gh.Kernel.IGH_Param) and obj.NickName == nickname:
            matched.append(obj)
        elif isinstance(obj, gh.Kernel.IGH_Component) and obj.NickName == nickname:
            for param in obj.Params.Output:
                matched.append(param)
    return matched

def get_color_from_string(color_str, random_colors_dict):
    color_str = color_str.strip()
    if color_str.startswith('#'):
        try:
            hex_str = color_str.lstrip('#')
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return System.Drawing.Color.FromArgb(r, g, b)
            elif len(hex_str) == 3:
                r = int(hex_str[0]*2, 16)
                g = int(hex_str[1]*2, 16)
                b = int(hex_str[2]*2, 16)
                return System.Drawing.Color.FromArgb(r, g, b)
        except Exception:
            pass

    # Random color logic for string identifiers
    if color_str not in random_colors_dict:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        random_colors_dict[color_str] = System.Drawing.Color.FromArgb(r, g, b)

    return random_colors_dict[color_str]

def get_or_create_layer(doc, layer_path, color):
    parts = [p.strip() for p in layer_path.split('/') if p.strip()]
    if not parts:
        return None

    parent_id = System.Guid.Empty
    current_layer = None

    for part in parts:
        found = False
        for layer in doc.Layers:
            if layer.Name == part and layer.ParentLayerId == parent_id:
                current_layer = layer
                found = True
                break

        if not found:
            new_layer = Rhino.DocObjects.Layer()
            new_layer.Name = part
            new_layer.ParentLayerId = parent_id
            layer_index = doc.Layers.Add(new_layer)
            if layer_index >= 0:
                current_layer = doc.Layers[layer_index]
            else:
                return None

        parent_id = current_layer.Id

    if current_layer is not None:
        current_layer.Color = color
        doc.Layers.Modify(current_layer, current_layer.Index, True)

    return current_layer

def clear_layer_objects(doc, layer):
    objs = doc.Objects.FindByLayer(layer)
    if objs:
        for obj in objs:
            doc.Objects.Delete(obj.Id, True)

def get_geometry_from_param(param):
    geometries = []
    if hasattr(param, 'VolatileData'):
        for branch in param.VolatileData.Branches:
            for item in branch:
                val = getattr(item, 'Value', item)
                if isinstance(val, Rhino.Geometry.GeometryBase) or isinstance(val, Rhino.Geometry.Point3d) or isinstance(val, Rhino.Geometry.Line):
                    geometries.append(val)
    return geometries

def bake_geometry(doc, geometry, layer_index):
    attributes = Rhino.DocObjects.ObjectAttributes()
    attributes.LayerIndex = layer_index
    attributes.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromLayer

    if isinstance(geometry, Rhino.Geometry.Point3d):
        doc.Objects.AddPoint(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Line):
        doc.Objects.AddLine(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Curve):
        doc.Objects.AddCurve(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Brep):
        doc.Objects.AddBrep(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Surface):
        doc.Objects.AddSurface(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Mesh):
        doc.Objects.AddMesh(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.Hatch):
        doc.Objects.AddHatch(geometry, attributes)
    elif isinstance(geometry, Rhino.Geometry.TextEntity):
        doc.Objects.AddText(geometry, attributes)
    else:
        # Fallback/ignore if type is unhandled
        pass

def main():
    if 'Bake' not in globals() or not Bake:
        return

    if 'CSV_File' not in globals() or not CSV_File or not os.path.exists(CSV_File):
        print("Invalid CSV file path or CSV_File input not provided")
        return

    gh_doc = get_gh_doc()
    if not gh_doc:
        print("Could not find Grasshopper document context")
        return

    rhino_doc = Rhino.RhinoDoc.ActiveDoc
    if not rhino_doc:
        print("Could not find Active Rhino Document")
        return

    random_colors_dict = {}
    cleared_layers = set()
    baked_count = 0

    with open(CSV_File, mode='r') as f:
        reader = csv.reader(f)

        for i, row in enumerate(reader):
            # Skip header row if it exactly matches expected header names
            if i == 0 and len(row) >= 3:
                h0 = row[0].strip().lower()
                h1 = row[1].strip().lower()
                h2 = row[2].strip().lower()
                if h0 == 'item name' and h1 == 'layer' and h2 == 'color':
                    continue

            if len(row) < 3:
                continue

            item_name = row[0].strip()
            layer_path = row[1].strip()
            color_str = row[2].strip()

            if not item_name or not layer_path:
                continue

            params = find_params_by_nickname(gh_doc, item_name)
            if not params:
                continue

            all_geometries = []
            for param in params:
                all_geometries.extend(get_geometry_from_param(param))

            if not all_geometries:
                continue

            layer_color = get_color_from_string(color_str, random_colors_dict)

            layer = get_or_create_layer(rhino_doc, layer_path, layer_color)
            if not layer:
                print("Failed to get or create layer: {}".format(layer_path))
                continue

            if layer.Id not in cleared_layers:
                clear_layer_objects(rhino_doc, layer)
                cleared_layers.add(layer.Id)

            for geo in all_geometries:
                bake_geometry(rhino_doc, geo, layer.Index)
                baked_count += 1

    if baked_count > 0:
        print("Successfully baked {} geometries to layers.".format(baked_count))

if __name__ == "__main__":
    main()
