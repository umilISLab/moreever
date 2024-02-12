from glob import glob

vocabulary = [v[:-4] for v in glob("*.csv")]
