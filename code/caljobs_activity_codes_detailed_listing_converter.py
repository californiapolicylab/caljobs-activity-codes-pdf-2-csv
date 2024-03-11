import camelot
import pickle
import pandas as pd

def convert():
    # Pickle file to serialize camelot input
    pickle_file_path = "output/caljobs_activity_codes_detailed_listing_camelot_output.pkl"
    # Read in PDF file with camelot-py. This processing is expensive.
    tbls = camelot.read_pdf("sourcedata/caljobs_activity_codes_detailed_listing.pdf", pages="1-9")
    # Serialize the object read from PDF to prevent constant conversion
    with open(pickle_file_path, "wb") as handle:
        pickle.dump(tbls, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # Load serialized object
    with open(pickle_file_path, "rb") as handle:
        tbls_pkl = pickle.load(handle)
    # Initialize lists that will be later converted to pandas series
    activity_code = []
    programs_list = []
    reporting_category = []
    restarts_exit_clock = []
    pirl = []
    duration = []
    # camelot-py imports tables from each page separately, even if a table spans across 2 pages,
    # but a PDF contains only 1 table, so we must iterate through the dataframes imported to
    # process them and generate a single table, with each column requiring particular processing
    # and cleansing.
    for tbl in tbls_pkl:
        # Read rows starting from row index 3 because camelot-py didn't interpret the 1st and 2nd
        # rows as headers.
        df = tbl.df.tail(-2)
        # add the 1st column to the code list. we're using "extend" instead of "append" because
        # we're adding several elements at a time instead of just 1.
        activity_code.extend(df[0])
        # Grab columns 2 to 7 and across all of them, replace x for 1 and null for 0
        programs_list.append(df[list(range(2,8))].apply(lambda x: x.str.strip().replace("", "0").replace("x", "1")))
        # clean column of \n chars
        reporting_category.extend(df[8].replace("\n", "", regex=True))
        # replace NO for 0 and YES for 1
        restarts_exit_clock.extend(df[9].str.strip().replace("NO", "0").replace("YES", "1"))
        # clean columns of \n chars
        pirl.extend(df[10].replace("\n", "", regex=True))
        # remove trailing and leading spaces
        duration.extend(df[11].str.strip())

    # put together dataframe with programs (columns 2 to 7)
    programs_df = pd.concat(programs_list, ignore_index=True)
    programs_df.columns = ["prog_affiliation_adult_dw",
            "prog_affiliation_youth",
            "prog_affiliation_nfjp",
            "prog_affiliation_wp_jvsg",
            "prog_affiliation_msfw",
            "prog_affiliation_taa"]

    # put together final dataframe with series from lists and dataframe built with programs above
    caljobs_act_codes_detailed_list = pd.concat([
        pd.Series(activity_code).rename("activity_code"),
        programs_df,
        pd.Series(reporting_category).rename("reporting_category"),
        pd.Series(restarts_exit_clock).rename("restarts_exit_clock"),
        pd.Series(pirl).rename("pirl"),
        pd.Series(duration).rename("duration")
    ], axis=1)

    # Fix scrambled columns. Often when camelot-py misdetects cell boundaries or a row is split
    # across a page break, it will be processed as an additional row.
    caljobs_act_codes_detailed_list.loc[4,"activity_code"] = "06M"
    # Save CSV
    caljobs_act_codes_detailed_list.to_csv("output/caljobs_activity_codes_detailed_listing.csv", index=False)