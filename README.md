# CSV Extractor tool for tables in CalJOBS Activity Codes PDFs

The Employment Development Department of California has for a long time made public PDF files containing the activity codes of the services they offer through the CalJOBS system, along with how these affect a user's journey.

A rundown and description of the PDFs can be found at the end of [this document](https://edd.ca.gov/siteassets/files/jobs_and_training/pubs/wsd19-06.pdf), but this repository makes them available in its `sourcedata/` directory for easier processing and exploration.

The output are CSV files that can be then imported into a DB, RStudio or a Jupyter Notebook for analysis.

# How does it work?

1. Open up a terminal/command window.

2. Clone/download the repo to `caljobs-activity-codes-pdf-2-csv/` dir.
  - If cloning it, use `git clone https://github.com/californiapolicylab/caljobs-activity-codes-pdf-2-csv` from your PC, not from a VM.

3. `cd` into `caljobs-activity-codes-pdf-2-csv/` and type `pip install requirements.txt`. This will install the necessary dependencies
  - You may also have to install some OS dependencies, which will be easier with Linux's `apt`

4. Type `python code/caljobs_activity_codes_sqlite.csv`. The script will check directory structure and create files if they are not there, and then spin up a SQLite3 database with these CSV as tables. This may take a while. Don't interrupt the process until you see the followng:
```
*******************
SQLite3 DB up.
Run 'sqlite3 ./caljobs_act_codes.db' file.
Press Ctrl+C when done.
*******************
```

5. Open up any DB visualizer of your choice and connect with the following URL: `jdbc:sqlite:/path/to/caljobs-activity-codes-pdf-2-csv/caljobs_act_codes.db`.

6. Table names are identical to the file names below.
  - `caljobs_activity_codes_dictionary`
  - `caljobs_activity_codes_detailed_listing`
  - `caljobs_activity_codes_detailed_listing_employer`
  - `caljobs_activity_codes_and_perf_crosswalk`

7. Spine is in table `caljobs_activity_codes_dictionary`, and the key used to travel to the rest of the tables is `activity_code`.

: warning: If you are running this code from WSL, but wish to connect to the SQLite3 instance created here using a Windows DB client, you will have to create a symlink from the `caljobs_act_codes.db` to anywhere in the Windows filesystem. We suggest typing: `ln -s /mnt/c/Users/[_your windows user_]/Desktop/caljobs_act_codes.d`.

## Example query

Let's take the following query:

```sql
select dl.reporting_category, 
sum(prog_affiliation_adult_dw),
sum(prog_affiliation_msfw),
sum(prog_affiliation_nfjp),
sum(prog_affiliation_taa),
sum(prog_affiliation_wp_jvsg),
sum(prog_affiliation_youth)
from caljobs_activity_codes_dictionary cd
join caljobs_activity_codes_detailed_listing dl 
on (cd.activity_code = dl.activity_code)
group by dl.reporting_category;
```

This query attempts to count the programs by reporting category.

## How is this done?

We use the [`camelot-py`](https://camelot-py.readthedocs.io/en/master/) library, which depends on ghostscript and tkinter. Running on Linux will prove easier, due to these dependencies on Windows being finnicky in terms of installation.

There is 1 converter for each PDF file, in the form of a notebook that must be run in a Jupyter environment.

`camelot-py` uses ghostscript to detect and extract tables as a raster image, and then process them via OCR, but does this page by page, so tables that span several pages are extracted as multiple tables, hence the necessary post-processing. Also, since it works with images, it is adequate for PDFs that contain images of scanned tables.
