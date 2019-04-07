*David Schlangen, 2019-04-07*

# Semantics with Pictures

This repository started out as a companion to my IWCS 2019 paper "Natural Language Semantics with Pictures: Some Language & Vision Datasets and Potential Uses for Computational Semantics" [[pdf]](http://www.google.com). It documents the experiments reported there, but goes beyond the material in that paper. The repository also collects the main material for my summer 2019 Potsdam class on ["computational semantics with pictures"](https://compling-potsdam.github.io/sose19-pm1-pictures/).
Finally, the notebooks here rely on the output of the preprocessing of the various image and image annotation corpora discussed here, the code for which is collected in the [clp-vision](http://github.com/clp-research/clp-vision.git) repository. In that sense, this repository can also be seen as a companion to that code.

## What you can find here

Start reading in [01_SemPics](01_SemPics), either with [the paper](01_SemPics/sempix_iwcs.pdf) or with [the notebook](01_SemPics/semantics_with_pictures.ipynb).

You will find an overview of the image corpora that we have preprocessed, and an illustration of the preprocessing format, in [02_ImageCorpora/image_corpora.ipynb](02_ImageCorpora/image_corpora.ipynb). (A technical overview without text is in [all_preprocessed.ipynb](all_preprocessed.ipynb).)

The additional annotation that links the image corpora with natural language expressions of all kinds, and tasks that can be defined with it, are shown in [03_Tasks](03_Tasks). Perhaps start reading with [denotations.ipynb](03_Tasks/denotations.ipynb). A draft of a paper that tries to make a bit of sense of the strategy of defining tasks and games and stuff to make progress is there as well, [Language Tasks and Language Games](03_Tasks/task_worlds_games_draft.pdf).


## Some technical notes

If you want to execute the notebooks, you need to have set an environment variable `VISCONF` that points to a config file (format explained / illustrated in the [clp-vision](http://github.com/clp-research/clp-vision.git) repo), and you also need to have access to the output of the preprocessing done in that repo, and the image data. And you need to have a ton of dependencies installed, of which I should really compile a list, and will do, at some point.

The notebooks here look best (and as intended) when the Jupyter extensions `latex_env`, `toc2`, and `codefolding` are installed; which can be done easily via [NB extensions](https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/). 


## Citation

If you make use of any material in here, please cite
> David Schlangen, Natural Language Semantics with Pictures: Some Language & Vision Datasets and Potential Uses for Computational Semantics, Proceedings of the International Conference on Computational Semantics (IWCS), 2019, Gothenburg, May
