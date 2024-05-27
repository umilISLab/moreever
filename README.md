# moreever - MulticORpus Explorer for Explicit Vocabulary References

This is a tool to visually explore (as a case of comparative linguistics) the presence of user-defined sets of textual references in several corpora. It is motivated by the conviction that quantitative analysis (or distant reading if you prefer) can lead to misinterpretations or omissions if not grounded in examples (close reading) from the actual corpora. The risk is somewhat discussed in Franco Moretti's "Falso Movimento", but is just a case of the need to have theory and empiricism go hand in hand.


This is meant to be useful for a set of three small corpora in English (tested on 3x~50K word tokens).



* Stemming (also including lemmatisation and morphological root extraction as variants) is supported as a way to extract more from the small corpora. For currently supported stemmers, see [stemmers.py](stemmers.py).

## Setup

To be able to use this tool, you would need to define:

* sets of words that represent your explicit references (labels representing values). These are defined as CSV files in a file placed in [./vocab](./vocab/) and referenced from [settings.py](settings.py), and

* corpora to be studied these are located in a directory named `./corpus.*` and referenced from [settings.py](settings.py).

To initialise the database, use 
    `docker exec -it api /app/populate.py <stemmer>`
or
    `docker exec -it api /app/populate.py --list`
to see all available stemmers for the given language.

### Corpora

Corpora are loaded in the [stories](stories/) directory, with each corpus represented by a subdirectory.

Currently these are fixed to three national corpora (see [const.py](const.py), [template.py](template.py)).

If not in possesion of corpora, use [PD-scrape.ipynb](PD-scrape.ipynb) to download fairy tales.

Also, clustering requires creation of models and is not integrated in the web interface.

### Values

Due to the original context of this research, we call the sets/clusters of explicit references (societal) values and the words that form these - labels.

Values are defined in a CSV-like file, where each line starts with the value representant, followed by label/keywords (synonyms) separated by commas. An example is provided in [values-edited.txt](values-edited.txt).

## Use
For local use, the dynamic version is advisable. For deployment the static version is more efficient, but possibly redundant in generating data for stemmers that are irrelevant.

Using [main.py](main.py) a version could be run that generates the analytical pages dynamically on demand. This has slower performance (barely noticeable for a single user).

Implementing caching is recommended in cases of heavier load. Probably best way to implement this is via HTTP headers.

## Screenshots

Currently there are three views: browser, heatmap and Venn diagram.

### Browser preview

The main view is the browser. It features three columns: lists of texts on the left, lists of values on the right and fulltexts in the middle. Navigation to other views and settings are available on the top.

![Browser preview](docs/browser-ps.png "Browser preview for Porter Stemmer")

### Clickable heatmap
![Clickable heatmap](docs/heatmap-ps.png "Clickable heatmap for Porter Stemmer")

### Venn diagram 
![Venn diagram](docs/venn-sb.png "Venn diagram for Snowball Stemmer")
