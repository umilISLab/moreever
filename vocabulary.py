from glob import glob

vocabulary = [v[6:-4] for v in glob("vocab/*.csv")]
