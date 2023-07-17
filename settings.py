from datetime import datetime

dateformat_log = "%Y%m%d"
datestamp = datetime.now().strftime(dateformat_log)
model_dir = f"/home/mapto/models/{datestamp}"

db_dir = "/home/mapto/work/moreever/db"
