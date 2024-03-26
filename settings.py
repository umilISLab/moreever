from datetime import datetime
import os

dateformat_log = "%Y%m%d"
datestamp = datetime.now().strftime(dateformat_log)
# model_dir = os.path.expanduser(f"~/models/{datestamp}")
model_dir = os.path.abspath(f"./models/{datestamp}")

db_dir = os.path.abspath("./db")

DEBUG = True

VOCAB = "clustering"

lang = "it"
