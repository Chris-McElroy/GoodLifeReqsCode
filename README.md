# The labour and resource use requirements of a good life for all
Chris McElroy and Daniel W. O’Neill

[![License: CC BY](https://img.shields.io/badge/licence-CC%20BY-green)](https://creativecommons.org/licenses/by/4.0/)

+ [Overview](#Overview)
+ [Install and Data](#Install-and-Data)
+ [Usage](#Usage)
+ [Citation](#Citation)

## Overview

This is the code used to generate the results presented in the article "The labour and resource use requirements of a good life for all", published in [Global Environmental Change](https://doi.org/10.1016/j.gloenvcha.2025.103008) on May 22, 2025. We use multi-regional input–output (MRIO) analysis to calculate the footprints of two low-consumption scenarios and 5 reference baselines. More details and discussion about our methods and results are provided in the article.

The code uses data from several sources, including economic data from EXIOBASE, demographic data from OECD, and spending data from the supplementary materials provided alongside the article. MRIO analysis is done through the use of the PyMRIO library. More details on installing and using this code are provided below.


## Install and Data

Before running this code, you will need to install the PyMRIO libarary and download data from EXIOBASE. The PyMRIO library is available [here](https://github.com/IndEcol/pymrio/tree/master) and its documentation includes extensive details on both [how to use it](https://pymrio.readthedocs.io/en/latest/notebooks/explore.html) and [how MRIO analysis works generally](https://pymrio.readthedocs.io/en/latest/math.html). Our results are based on [EXIOBASE version 3.9.5](https://zenodo.org/records/14869924) (specifically the pxp or product version of 2019 data in version 3.9.5), though this version has significant issues with its labour account, so we used a fixed labour account that should be released with version 3.9.6. If you are interested in this labour account or have other questions about our methods, please contact Chris McElroy (contact@chris-mcelroy.com).

To set up the code, clone this repository, ensure the EXIOBASE data is saved to the `original data` folder, and that the variable `repo_path` in line 11 of `main.py` is set to the path the repository is stored in on your computer (and uncomment that line).

## Usage

To run the code, you can use the command `python3 main.py` from within the repository. This will generate excel files in the folder `excel output` with the results for each function. To isolate specific outputs, comment out some of the function calls in lines 326–333. The first time the code is run, it will generate the full dataset, which runs in about 5 minutes on my laptop and takes about 5.3 GB worth of additional space. If you run the code again, this generated data will be used, which results in the code running in about 90s on my laptop. If you would prefer to not generate the saved data (but take longer each time you run the calculations), comment out line 23 in `main.py`.

Note that the results in the `excel output` folder will be overwritten each time the code is run.

For comparison, our full results are available in the "Results" tab of the Supplementary Materials 2 document available with the article.

## Citation

The CC BY license means you are free to use and share this code, but you must attribute credit. Please do so by referencing the original article:

McElroy, C., O’Neill, D.W., 2025. The labour and resource use requirements of a good life for all. Global Environmental Change 92, 103008. https://doi.org/10.1016/j.gloenvcha.2025.103008.
