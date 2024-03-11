import camelot
import pickle
import pandas as pd

def convert():
    # Pickle file to serialize camelot input
    pickle_file_path = "output/caljobs_activity_codes_detailed_listing_employer_camelot_output.pkl"
    # Read in PDF file with camelot-py. This processing is expensive.
    tbls = camelot.read_pdf("sourcedata/caljobs_activity_codes_detailed_listing_employer.pdf", pages="1-2")
    # Serialize the object read from PDF to prevent constant conversion
    with open(pickle_file_path, "wb") as handle:
        pickle.dump(tbls, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # Load serialized object
    with open(pickle_file_path, "rb") as handle:
        tbls_pkl = pickle.load(handle)

    # Initialize lists that will be later converted to pandas series
    activity_code = []
    reporting_category = []

    # camelot-py imports tables from each page separately, even if a table spans across 2 pages,
    # but a PDF contains only 1 table, so we must iterate through the dataframes imported to
    # process them and generate a single table, with each column requiring particular processing
    # and cleansing.
    for tbl in tbls_pkl:
        # Read rows starting from row index 2 because camelot-py didn't interpret the 1st and 2nd
        # rows as headers.
        df = tbl.df.tail(-1)
        # add the 1st column to the code list. we're using "extend" instead of "append" because
        # we're adding several elements at a time instead of just 1.
        activity_code.extend(df[0])
        # clean column of \n chars
        reporting_category.extend(df[2].replace("\n", "", regex=True))

    # put together final dataframe with series from lists above
    caljobs_act_codes_detailed_list_emp = pd.DataFrame({
        "activity_code": activity_code,
        "reporting_category_employer":reporting_category
    })
    # Save CSV
    caljobs_act_codes_detailed_list_emp.to_csv("output/caljobs_activity_codes_detailed_listing_employer.csv", index=False)