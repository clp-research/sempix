# Entailment via Model Building

This documents the "entailment via model building" experiments reported in
[1].

* First, the test sets are prepared, in `make_datasets.ipynb`. This results in several files being created in `./EntailOut`, namely `capobj.csv` and `capreg.csv`, which each collect 20k premises, hypothesis pairs. (Balanced.)


* Then, some embeddings must be available:
    1. For the MSCOCO captions. This is done in `DSGV-PATHS/Preproc/CapEmbed`, where also a nearest neighbour index is precomputed. The expecation is that `caps.ann` and `cap_embeds.npz` are available in `preproc_path` (from config).
    2. We also need embeddings into the same space, for the object names that are tested, and for the region descriptions. This is done using the universal sentence encoder [2], in `embed_objreg_colab.ipynb`, which I ran on <http://colab.researchgoogle.com>. This gives us `capobj.npz` and `capreg.npz`, which are expected in `EntailOut/`.

* The actual model building method is performed and evaluated in `model_building.ipynb`.



[1] David Schlangen, "Natural Language Semantics With Pictures: Some Language & Vision Datasets and Potential Uses for Computational Semantics", IWCS 2019, Gothenburg.

[2] Cer, D., Yang, Y., Kong, S., Hua, N., Limtiaco, N., John, R. St., … Kurzweil, R. (2018). Universal Sentence Encoder. ArXiv. http://doi.org/arXiv:1803.11175v2
