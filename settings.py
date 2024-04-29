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
# VOCAB = "values"
# VOCAB = "mfd2.0.dummy" # TODO: remove dots in classes
VOCAB: Final = "Refined_dictionary.dummy"
# VOCAB: Final = "Refined_dictionary.lan"

DATABASE_URL: Final = f"sqlite:///{VOCAB}.sqlite?check_same_thread=False"

# lang = "it"
lang: Final = "en"
