# Koren's triode model estimation

The following scripts were adapted from the [original Matlab code](https://normankoren.com/Audio/Tuparam.zip)
to run in Python using Numpy and Scipy. We also use Matplotlib
to generate the chart using the fit model.

## Environment
Prepare the environment to run the code.

1. Get [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) and install on your computer.
2. Make sure it's installed properly and available in terminal of your choice. To do so -- run `python --version`
3. Create a new environment with only the necessary packages `conda env create -f conda_env.yaml`
4. Activate the new environment `conda activate ltspice`

## Finding the model parameters

This is now easy. Navigate to the folder with `tube_ltspice.py` and run `python tube_ltspice.py`. This will use the data file `input_data/12AX7ASYL.m` and create two files:
1. `models\12AX7A.model` with the estimated LTSpice model.
2. `plots\12AZ7A.png` with the estimated model output; the dots on the chart show the (Vp, Vg, Ip) points used to estimate the model and were taken from a datasheet.

### Estimating models for other tubes

The procedure is simple. 

1. Duplicate any of the `.m` files found in `input_data` folder.
2. Rename it to the name of the tube you want to estimate the model for, e.g. `12AT7.m`.
3. Update the contents of the newly created file (example below)
```
TubeName = '12AX7A';
Source = 'Sylvania Technical Manual (6AV6)';
VGP = 0:-.5:-4;  axset = [0 450 0 .004];
MU = 100;  VCT = .5;  Vpmax = 450;
Vp =    [10    50     100    120   220   200    300   300];
Vg =    [0     0      0      -1    -1    -2     -2    -3];
Idata = [.0003 .0012 .00212 .00075 .0025 .00056 .0021 .0006];
```
Here's the full list of the parameters currently supported by the script: `tube_name`, `tube_source`, `Vp`, `Vg`, `Idata`,
`MU`, `VGP`, `axset`, `Vpmax`, `VCT`. Most of these are self-explanatory but you can see their descriptions [here](https://normankoren.com/Audio/Tube_params.html). Most of these parameters can be sourced from the tube datasheet, some you can leave as is and adjust if the model doesn't estimate well.

4. To estimate the model for the new tube run `python tube_ltspice.py --tube_filename 12AT7` (note to not include the extension). You will find the estimated model in the `models` folder, and a the corresponding chart in the `plots` folder.


That's it folks. If you find a problem with the script (it's a bit hacky but should work) -- please, file an issue here.