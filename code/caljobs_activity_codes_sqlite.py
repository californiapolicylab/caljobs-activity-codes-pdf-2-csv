import os
import glob
import sqlite3
import pandas as pd
import caljobs_activity_codes_dictionary_converter
import caljobs_activity_codes_detailed_listing_converter
import caljobs_activity_codes_detailed_listing_employer_converter
import caljobs_activity_codes_and_perf_crosswalk_converter

# Init SQLite3 file-based instance. Save instance file in project root.
db = sqlite3.connect("caljobs_act_codes.db")

# Check if CSVs are there, and create them if not.
if (not os.path.exists("output/caljobs_activity_codes_dictionary.csv")):
    caljobs_activity_codes_dictionary_converter.convert()

if (not os.path.exists("output/caljobs_activity_codes_detailed_listing.csv")):
    caljobs_activity_codes_detailed_listing_converter.convert()

if (not os.path.exists("output/caljobs_activity_codes_detailed_listing_employer.csv")):
    caljobs_activity_codes_detailed_listing_employer_converter.convert()

if (not os.path.exists("output/caljobs_activity_codes_and_perf_crosswalk.csv")):
    caljobs_activity_codes_and_perf_crosswalk_converter.convert()

# Iterante through CSVs and load them to SQLite3
for file in glob.glob("output/*.csv"):
    df = pd.read_csv(file)
    table_name = os.path.basename(file).split(".")[0]
    df.to_sql(table_name, db, if_exists="replace", index=False)

# Press Ctrl+C to stop service
print("\n*******************\nSQLite3 DB up.\nRun 'sqlite3 ./caljobs_act_codes.db' in another command line window.\nCome back to this window and press Ctrl+C when done.\n*******************")
try:
    while True:
        pass
except KeyboardInterrupt:
    pass