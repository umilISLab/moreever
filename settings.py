from typing import Final

from datetime import datetime
import os

DATEFORMAT_LOG: Final = "%Y%m%d%H%M%S"

datestamp: Final = datetime.now().strftime(DATEFORMAT_LOG)
# model_dir = os.path.expanduser(f"~/models/{datestamp}")
model_dir: Final = os.path.abspath(f"./models/{datestamp}")

db_dir: Final = os.path.abspath("./db")

DEBUG: Final = True

# VOCAB = "clustering"
# VOCAB = "variation"
# VOCAB:Final = "values"
# VOCAB = "mfd2.0.dummy" # TODO: remove dots in classes
# VOCAB: Final = "Refined_dictionary.dummy"
# VOCAB: Final = "Refined_dictionary.lan"
# VOCAB: Final = "mfd2.0.lan"
# VOCAB: Final = "mfd2.0.custom"
VOCAB: Final = os.environ["VOCAB"]

# CORPORA: Final = "stories"
# CORPORA: Final = "twitter"
# CORPORA: Final = "reddit"
# CORPORA: Final = "mft"
CORPORA: Final = os.environ["CORPORA"]

# DATABASE_URL: Final = f"sqlite:///db/{VOCAB}.{CORPORA}.sqlite?check_same_thread=False"
DATABASE_URL: Final = "postgresql://postgres:xxxxxx@db/postgres"

# LANG = "it"
# LANG: Final = "en"
LANG: Final = os.environ["ISO_LANG"]

# A clean dataset is bottom-up defined and has no vocabulary that does not occur.
# An unclean is top-down (typically from a generic dictionary) and has many irrelevant or less relevant tokens.
# Thus: 1) tokens are sorted by frequence, 2) missing tokens are not shown

CLEAN_THRESHOLD: Final = 0
# CLEAN_THRESHOLD: Final = 10
