import os
import glob
import sqlite3
import pandas as pd

all_files = glob.glob("output/*.csv")
db = sqlite3.connect("caljobs_act_codes.db")

for file in all_files:
    df = pd.read_csv(file)
    table_name = os.path.basename(file).split(".")[0]
    df.to_sql(table_name, db, if_exists="replace", index=False)

print("SQLite3 DB up. Run 'sqlite3 ./caljobs_act_codes.db' file.\nPress Ctrl+C when done.")
try:
    while True:
        pass
except KeyboardInterrupt:
    pass