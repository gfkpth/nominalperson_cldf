# Notes on the setup of a new CLDF

For the original tutorial see here: <https://github.com/cldf/cldfbench/blob/master/doc/tutorial.md>
In this file, I aim to document the conrete steps needed for my slightly more complex dataset.


## Preliminaries

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

2. Insert any raw data that should be integrated into the dataset into the `raw/` Folder.

3. Run catconfig to install a [glottolog](https://github.com/glottolog/glottolog) into the local system and create a catalog.ini file pointing to it. To make the API for glottolog available you also need to install the package `pyglottolog`, which I suggest installing before if it is not available in your system/virtual environment.

```shell
pip install pyglottolog
cldfbench catconfig
```

This prompts you to install several auxiliary datasets. For the current use case, I want glottolog, so I pick yes to that and decline the concepticon and clts.
Note that on Linux this clones <https://github.com/glottolog/glottolog> into ~/.config/cldf/glottolog, with a weight of about 1.5GB.

Alternatively, you could download/`git clone https://github.com/glottolog/glottolog` into some other location and create a ~/.config/cldf/catalog.ini file with the appropriate path as follows (I'm not sure if this has any downsides to directly following the catconfig flow in use cases I haven't encountered yet):

```shell
# ~/.config/cldf/catalog.ini
[clones]
glottolog = /path/of/your/local/glottolog/repository
```


## Setting up the cldfbench_[projectname].py





# Questions:

- What are possible values for `args.writer.objects['ValueTable']`?
- How does the following part skipped over in the tutorial work when needed?
  - "Because we only create a single CLDF dataset here, we do not need to call with self.cldf_writer(...) as ds: explicitly. Instead, an initialized cldfbench.cldf.CLDFWriter instance is available as args.writer."
