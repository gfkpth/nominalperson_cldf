# Overview

This repository contains a database with syntactic data on >100 languages with a focus on properties relating to the phenomenon of (ad)nominal person. The code here creates a [CLDF](https://github.com/cldf/cldf/)-conformant database, a format designed for linguistic applications, from older (and somewhat unorderly) csv-files.

**This is still work in progress.**

A previous implementation of the data as a relational (SQL) database can be found [here](https://github.com/gfkpth/nominal_person). That repo also contains the a jupyter notebook extracting example sentences for nominal person from a LaTeX-file, see  [here](https://github.com/gfkpth/nominal_person/tree/main/db-creation-notes/CLDF).

# (Ad-)nominal person

One common form of nominal person are personal pronouns forming co-constituents of a co-referring nominal expression as in English *we linguists*.
More detailed information on relevant phenomena and the range of cross-linguistic variation can be found in [Höhn (2020)](https://doi.org/10.5334/gjgl.1121) and [Höhn (2024)](https://doi.org/10.1515/lingty-2023-0080) as well as [my dissertation](https://ling.auf.net/lingbuzz/003618). If you use this data, I'd appreciate it if you'd let me know. If you are a linguist interested in (ad)nominal person and struggle with using this database, feel free to get in touch.

Note that this is currently work in progress. 

## Notes on the setup of a new CLDF

For the original tutorial see here: <https://github.com/cldf/cldfbench/blob/master/doc/tutorial.md>. 
In this section, I aim to document the concrete steps needed for my slightly more complex dataset.


### Preliminaries

0. Ensure that the python program `cldfbench` is installed, for instructions see [here](https://github.com/cldf/cldfbench/blob/master/README.md). [`pycldf`](https://github.com/cldf/pycldf) is going to be useful as well.

Using a virtual environment is recommended, I am using conda to create one inside the folder I want to use for the cldf.

```shell
conda create -p .venv python==3.12
conda activate .venv
pip install cldfbench pycldf
```

 c

1. Create a new cldf structure. For consistency, make sure to provide as ID the name of the folder that you want to use.

```shell
cd ..
cldfbench new
```

I am moving one level up in the file structure because I created my virtual environment inside the target folder. If you're using a system-installed cldfbench (or create your virtual environment in a different location), you can just run `cldfbench new` in the parent folder of where you want your cldf folder to sit.

2. Insert any raw data that should be integrated into the dataset into the `raw/` Folder.

3. Run catconfig to install [glottolog](https://github.com/glottolog/glottolog) into the local system and create a catalog.ini file pointing to it. To make the API for glottolog available you also need to install the package `pyglottolog`, which I suggest installing before if it is not available in your system/virtual environment.

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


### Setting up the cldfbench_[projectname].py

As described in the available tutorials, `cldfbench new` creates a general template on which to build. The crucial code for converting my csv-data into CLDF needs to go to `cldfbench-[projectname].py`. 

The following code generates the CLDF-conformant dataset in the `cldf/` folder:

```shell
cldfbench makecldf cldfbench_nominalperson_cldf.py
```

The following code validates the generated dataset and displays errors or warnings encountered during validation:

```shell
cldf validate cldf/
```


# To Do/Questions:


## Implementation

- Associating examples to values in case there is more than one relevant example
  - For regular normalisation in standard relational tables I'd expect to set up a separate table linking example ids to value ids, but given the handling of sources, CLDF doesn't seem to strictly require transforming data into first normal form to avoid multiple values, is that right?
  - So would it be better to just have a list (semicolon separated?)
- How to deal with complex words in examples, i.e. analyzed_words has two elements separated by space that are glossed as one element in original source. In LaTeX I encompass both elements in {} and have kept this for the examples.csv for now, but it fails at validation. (Applies to rows 73 and 148)
- fine-grained parameter-assignments of examples (ExampleTable) to values (ValuesTable)
  - currently just a rough check: if demonstrative contained in gloss -> PPDC, otherwise just regular
- tried copying in source.bib to allow generation of sqlite db, but still `cldf createdb --infer-primary-keys cldf nominalperson.sqlite` still fails at writing the ValueTable_SourceTable (i.e. probably a mapping table?) 
  - found the issue: inconsistencies in naming of references in sources.bib and the versions automatically generated from the regular references in the grammarchecks.csv table (examples.csv, by contrast, has direct access to the correct bib keys); to unify

  ## Documentation

- write-up for usage, especially regarding parameter-codes.json
- details for tutorial-like guide
  - What are possible values for `args.writer.objects['ValueTable']`?
  - How does the following part skipped over in the tutorial work when needed?
    - "Because we only create a single CLDF dataset here, we do not need to call with self.cldf_writer(...) as ds: explicitly. Instead, an initialized cldfbench.cldf.CLDFWriter instance is available as args.writer."
