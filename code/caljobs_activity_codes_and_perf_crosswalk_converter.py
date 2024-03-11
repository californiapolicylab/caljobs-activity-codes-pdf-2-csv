import camelot
import pickle
import pandas as pd

def convert():
    # Pickle file to serialize camelot input
    pickle_file_path = "output/caljobs_activity_codes_and_perf_crosswalk_camelot_output.pkl"
    # Read in PDF file with camelot-py. This processing is expensive.
    tbls = camelot.read_pdf("sourcedata/caljobs_activity_codes_and_perf_crosswalk.pdf", pages="1-3")
    # Serialize the object read from PDF to prevent constant conversion
    with open(pickle_file_path, "wb") as handle:
        pickle.dump(tbls, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # Load serialized object
    with open(pickle_file_path, "rb") as handle:
        tbls_pkl = pickle.load(handle)
    # Initialize lists that will be later converted to pandas series
    activity_code = []
    credential_attainment = []
    measurable_skill_gains = []
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
        # Replacing 'x' for 1 and null for 0 for the 2 columns below
        credential_attainment.extend(df[6].str.replace("x", "1").replace("", "0"))
        measurable_skill_gains.extend(df[7].replace("x", "1").replace("", "0"))

    # Create dataframe with series created above
    caljobs_act_codes_perf_crosswalk = pd.DataFrame({
        "activity_code": activity_code,
        "credential_attainment":credential_attainment,
        "measurable_skill_gains":measurable_skill_gains
    })

    # Fix scrambled columns. Often when camelot-py misdetects cell boundaries or a row is split
    # across a page break, it will be processed as an additional row.
    caljobs_act_codes_perf_crosswalk.loc[5,"activity_code"] = caljobs_act_codes_perf_crosswalk.loc[5,"activity_code"][:3]
    caljobs_act_codes_perf_crosswalk.loc[9,"activity_code"] = caljobs_act_codes_perf_crosswalk.loc[9,"activity_code"][:3]
    # Save to CSV
    caljobs_act_codes_perf_crosswalk.to_csv("output/caljobs_activity_codes_and_perf_crosswalk.csv", index=False)