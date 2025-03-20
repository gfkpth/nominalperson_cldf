# Notes on the setup of a new CLDF

For the original tutorial see here: <https://github.com/cldf/cldfbench/blob/master/doc/tutorial.md>
In this file, I aim to document the conrete steps needed for my slightly more complex dataset.

0. Ensure that the python program `cldfbench` is installed, for instructions see [here](https://github.com/cldf/cldfbench/blob/master/README.md). 

Using a virtual environment is recommended, I am using conda to create one inside the folder I want to use for the cldf.

```shell
conda create -p .venv python==3.12
conda activate .venv
pip install cldfbench
```

1. Create a new cldf structure. For consistency, make sure to provide as ID the name of the folder that you want to use.

```shell
cd ..
cldfbench new
```

I am moving one level up in the file structure because I created my virtual environment inside the target folder. If you're using a system installed cldfbench (or create your virtual environment in a different location), you can just run `cldfbench new` in the parent folder of where you want your cldf folder to sit.
