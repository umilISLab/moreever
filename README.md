# moreever - MulticORpus Explorer for Explicit ValuE References

This is a tool to visually explore (for the sake of comparison) the presence of user-defined sets of textual references in several corpora. It is motivated by the conviction that quantitative analysis (or distant reading if you prefer) can lead to misinterpretations or omissions if not grounded in examples (close reading) from the actual corpora. The risk is somewhat discussed in Franco Moretti's "Falso Movimento", but is just a case of the need to have theory and empiricism go hand in hand.


This is meant to be useful for a set of three small corpora in English (tested on 3x~50K word tokens).



* Lemmatisation/stemming is supported as a way to extract more from the small corpora. For currently supported stemmers, see [stemmers.py](stemmers.py).

## Setup

To be able to use this tool, you would need to define:

* sets of words that represent your explicit references (labels representing values), and

* corpora to be studied (currently specific to three national corpora (de, it, pt)

### Corpora

Corpora are loaded in the [stories](stories/) directory, with each corpus represented by a subdirectory.

Currently these are fixed to three national corpora (see [const.py](const.py), [template.py](template.py)).

If not in possesion of corpora, use [PD-scrape.ipynb](PD-scrape.ipynb) to download fairy tales.

### Values

Due to the original context of this research, we call the sets/clusters of explicit references (societal) values and the words that form these - labels.

Values are defined in a CSV-like file, where each line starts with the value representant, followed by label/keywords (synonyms) separated by commas. An example is provided in [values-edited.txt](values-edited.txt).

## Use
Running [deploy.py](deploy.py) generates a static website in the [site](site/) directory to browse the texts with the values highlighter. To run locally, use [site/run.sh](site/run.sh)

A dynamic version is work in progress.
## Screenshots

Currently there are three views: browser, heatmap and Venn diagram.

### Browser preview

The main view is the browser. It features three columns: lists of texts on the left, lists of values on the right and fulltexts in the middle. Navigation to other views and settings are available on the top.

![Browser preview](docs/browser-ps.png "Browser preview for Porter Stemmer")

### Clickable heatmap
![Clickable heatmap](docs/heatmap-ps.png "Clickable heatmap for Porter Stemmer")

### Venn diagram 
![Venn diagram](docs/venn-sb.png "Venn diagram for Snowball Stemmer")
