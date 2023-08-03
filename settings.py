from datetime import datetime
import os

dateformat_log = "%Y%m%d"
datestamp = datetime.now().strftime(dateformat_log)
model_dir = os.path.expanduser(f"~/models/{datestamp}")
# model_dir = "/home/mapto/models/20230713"
# model_dir = "/home/mapto/models/20230707.renamed"

db_dir = "/home/mapto/work/moreever/db"
