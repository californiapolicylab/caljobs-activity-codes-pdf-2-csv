# CSV Extractor tool for tables in CalJOBS Activity Codes PDFs

The Employment Development Department of California has for a long time made public PDF files containing the activity codes of the services they offer through the CalJOBS system, along with how these affect a user's journey.

A rundown and description of the PDFs can be found at the end of [this document](https://edd.ca.gov/siteassets/files/jobs_and_training/pubs/wsd19-06.pdf), but this repository makes them available in its `sourcedata/` directory for easier processing and exploration.

The output are CSV files that can be then imported into a DB, RStudio or a Jupyter Notebook for analysis.

## How is this done?

We use the [`camelot-py`](https://camelot-py.readthedocs.io/en/master/) library, which depends on ghostscript and tkinter. Running on Linux will prove easier, due to these dependencies on Windows being finnicky in terms of installation.

There is 1 converter for each PDF file, in the form of a notebook that must be run in a Jupyter environment.

`camelot-py` uses ghostscript to detect and extract tables as a raster image, and then process them via OCR, but does this page by page, so tables that span several pages are extracted as multiple tables, hence the necessary post-processing. Also, since it works with images, it is adequate for PDFs that contain images of scanned tables.
