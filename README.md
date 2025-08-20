# Introduction

This repository contains mapping process for centerline extraction and interpolation, modified based on the repository [Cl2-UWaterloo/Raceline-Optimization](https://github.com/CL2-UWaterloo/Raceline-Optimization).


# List of components
* `grob_tracks`: This folder contains the reference track csvs generated.
* `helper_funcs`: This package contains some helper functions used in several other functions when
calculating the global race trajectory.
* `maps`: cleaned tracks with clear track boundaries.
* `params`: This folder contains a parameter file with optimization and vehicle parameters.
* `outputs`: This folder constains the centerline information and corresponding coefficients for the spline interpretation.


# Getting Started

The code is developed with Ubuntu 20.04 LTS and Python 3.8.

Ubuntu 22.04 does not include Python 3.8 in the default repositories, so you need to add the deadsnakes PPA:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

Then, install Python 3.8 and required tools:
```bash
sudo apt install -y python3.8 python3.8-distutils python3.8-venv
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.8 get-pip.py
```

Clone the repository
```bash
git clone https://github.com/WeiqiLyu/centerline_generation.git
cd centerline_generation
```

Then, set up your virtual environment. Conda is the recommended method.

```bash
python3.8 -m venv ./centerline_venv
source ./centerline_venv/bin/activate
python --version    # Should display Python 3.8.x
```

Install the required python packages
```bash
pip install -r requirements.txt
```

# Steps

### For `slam_toolbox`
If you generated the map through `slam_toolbox`, consult https://stevengong.co/notes/Raceline-Optimization.
You might need to photoshop the map first to remove any artifacts and have clear track boundaries.

First, run `map_converter.ipynb`, and then run `sanity_check.ipynb` to make sure the line generated is correct.

This will export a `.csv` file of the map to `grob_tracks`.

### For Waypoint Generator
Alternatively, if you generated the map by storing a set of waypoints, you can directly store it inside `grob_tracks`.

### Common steps
Then, run `centerline_generation.py` with the map name to generate the trajectory (expects the map to be inside `grob_tracks`). By default, the generated centerline will be stored inside `outputs/<map_name>`.

```bash
python3 centerline_generation.py --map_name CIIT_klein_gmapping_clean
```

