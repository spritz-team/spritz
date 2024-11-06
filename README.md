# spritz framework


### Installation 

We highly suggest to handle the environment with `Mamba` and `Miniforge`. The latter installation takes about `2Gb` of space so be sure to install it in a location with at least `4Gb` of space.
To install the latest `Miniforge` release run the following 

```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Use the `mamba activate` to activate an environment or create a custom one to handle `spritz` packages.

Clone the spritz repository and install all necessary requirements (`Python>=3.10`) 

```
git clone git@github.com:spritz-team/spritz.git
cd spritz 
pip install -r requirements.txt
pip install .
```

Now you are ready to use the framework, the steps along with the scripts are described in the following section.

### Steps
0. Edit and source start.sh to setup your python environment (mamba, venv or LCG release)
1. Create a config folder under configs, you might copy vbfz-2018, edit the config.py, the script_worker_dumper.py is the executable that is run on the condor job
2. `spritz-fileset`: get the list of all files (replicas and nevents) for each dataset defined in `data/{year}/samples/active_samples.py` (user has to change this file)
3. run `spritz-chunks` to create all the chunks and their metadata
4. run `spritz-batch` to submit on condor
5. `spritz-checkerrors` to check which job failed (should resubmit manually)
6. `spritz-merge` will merge all the results into a pickle file (removing all metadata and old errors)
7. `spritz-postproc` will take the pickle file and output a root file with simple directories and TH1s 
8. `spritz-plot`
