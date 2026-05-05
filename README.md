# alex-babel

An app/tool for easier communication with Grasshopper and value modification using CSV files.

This repository contains Python scripts (`gh_csv_updater.py` and `gh_csv_exporter.py`) designed to be used inside Grasshopper Python Components. They allow you to externalize your parameters into a simple `.csv` file, making it easy to drive your Grasshopper definitions without hunting for sliders and inputs on the canvas, as well as export existing parameters to generate the CSV.

## Features
- **Export Parameters:** Automatically extract "top-level" inputs (those with no incoming wires and a custom NickName) to create a starter CSV.
- **Update Primitive Types:** Automatically push `float`, `int`, `string`, and `bool` values to components based on their `NickName`.
- **Reference Geometry:** Dynamically wire reference parameters (like Curves, Points, Breps) to target parameters by name.
- **On-Demand Updates:** Trigger updates with a simple boolean toggle to avoid constant recalculations.

## Setup Instructions

### Exporter Setup (`gh_csv_exporter.py`)
Use this to generate your initial CSV from existing parameters.
1. Open Grasshopper.
2. Drag a **Python 3 Script** component (in Rhino 8) onto your canvas.
3. Add two inputs to the component:
   - `Export` (Set Type Hint to `bool`)
   - `CSV_File` (Set Type Hint to `str`)
4. Wire a Button to the `Export` input.
5. Wire a File Path or Panel containing the absolute path to your desired `.csv` output file to the `CSV_File` input.
6. Open `gh_csv_exporter.py` from this repository, copy its contents, and paste it into the Python component's code editor.

### Updater Setup (`gh_csv_updater.py`)
Use this to update parameters in Grasshopper based on a CSV.
1. Open Grasshopper.
2. Drag a **Python 3 Script** component (in Rhino 8) onto your canvas.
3. Add two inputs to the component:
   - `Update` (Set Type Hint to `bool`)
   - `CSV_File` (Set Type Hint to `str`)
4. Wire a Boolean Toggle or Button to the `Update` input.
5. Wire a File Path or Panel containing the absolute path to your `.csv` file to the `CSV_File` input.
6. Open `gh_csv_updater.py` from this repository, copy its contents, and paste it into the Python component's code editor.

## CSV Format

Your CSV file should have the following headers exactly (case-insensitive):
`input name`, `type`, `value`

### Supported Types

- **Primitives:** `float`, `num`, `int`, `integer`, `string`, `str`, `bool`, `boolean`
- **Geometry/References:** `crv`, `curve`, `pt`, `point`, `geo`, `geometry`, `brep`, `srf`, `surface`

### Example `sample_data.csv`

```csv
input name,type,value
domain-start-a,float,0.10
domain-end-a,float,0.90
some-integer-param,int,42
my-text-param,string,Hello World
is-active,bool,True
first-att-crv,crv,att-curve
target-point,pt,source-point
```

## How It Works

### Primitive Values (Numbers, Text, Booleans)
If your CSV reads:
`domain-start-a,float,0.10`

1. Create a `Number` parameter on your Grasshopper canvas.
2. Right-click the parameter and change its name (NickName) to `domain-start-a`.
3. When you trigger the Python script, it will find that parameter and inject the value `0.10` directly into it.

### Geometry / Reference Links
If your CSV reads:
`first-att-crv,crv,att-curve`

1. Create a `Curve` parameter on the canvas that contains your referenced Rhino geometry. Rename it to `att-curve`.
2. Somewhere else in your script where you need that curve, create another `Curve` parameter and rename it to `first-att-crv`.
3. When you trigger the script, it will find `first-att-crv`, clear its existing wires, and wire it directly to `att-curve`.

## Export Workflow Details
When you trigger the **Export** script, it scans your canvas for "top-level" inputs. An input is exported if:
1. It has **no incoming wires** (it's the start of a data flow).
2. It has a **custom NickName** (the user has renamed it from the default "Number", "Curve", etc.).

For standard data (Sliders, Toggles, Panels, or typed parameters), it extracts the value.
For geometry/reference parameters (like a Curve named `att-crv`), it creates a line in the CSV to set up a future link. It will output the name as `{NickName}-1` (e.g. `att-crv-1`) and the value as the original name (`att-crv`). You can then manually create an `att-crv-1` parameter later, and the Updater will wire it for you.
