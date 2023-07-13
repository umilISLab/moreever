# moreever - MulticORpus Explorer for Explicit ValuE References

This is a tool to visually explore (for the sake of comparison) the presence of clusters of textual references in several corpora.
This is meant to work with small corpora. That's why lemmatisation/stemming is supported. For currently supported stemmers, see [stemmers.py](stemmers.py).

## Setup
### Corpora
Corpora are loaded in the [stories](stories/) directory, with each corpus represented by a subdirectory.

Currently these are fixed to national corpora (see [const.py](const.py)).

If not in possesion of corpora, use [PD-scrape.ipynb](PD-scrape.ipynb) to download fairy tales.

### Values

Values are defined in a CSV-like file, where each line starts with the value representant, followed by label/keywords (synonyms) separated by commas. An example is provided in [values-edited.txt](values-edited.txt).

## Use
Running [deploy.py](deploy.py) generates a static website in the [site](site/) directory to browse the texts with the values highlighter. To run locally, use [site/run.sh](site/run.sh)

A dynamic version is work in progress.
## Screenshots

### Browser preview
![Browser preview](docs/browser.png "Browser preview")

### Clickable heatmap
![Clickable heatmap](docs/heatmap.png "Clickable heatmap")