import camelot
import pickle
import pandas as pd

def convert():
    # Pickle file to serialize camelot input
    pickle_file_path="output/caljobs_activity_codes_dictionary_camelot_output.pkl"
    # Read in PDF file with camelot-py. This processing is expensive.
    tbls = camelot.read_pdf("sourcedata/caljobs_activity_codes_dictionary.pdf", pages="2-61")
    # Serialize the object read from PDF to prevent constant conversion
    with open(pickle_file_path, "wb") as handle:
        pickle.dump(tbls, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # Load serialized object
    with open(pickle_file_path, "rb") as handle:
        tbls_pkl = pickle.load(handle)

    # Initialize lists that will be later converted to pandas series
    activity_code_list = []
    activity_name_list = []
    activity_description_list = []

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
        activity_code_list.extend(df[0].values.tolist())
        # Since the "activity_name" column has a lot of formatted text, and camelot-py processes
        # newlines as \n, we split the text in the cell by the \n occurrences, with each split
        # being processed different and turned into a different column.
        name_splits = df[1].str.split("\n")
        # we then traverse each of the splits 
        for name_split in name_splits:
            # we make a copy of the split so we can remove one of the actual name of the activity
            # and concatenate the rest as description
            name_split_copy = name_split.copy()
            # We iterate through the split string separated by \n
            for item in name_split:
                # If the item is over 3 chars long, then it is the activity name
                if len(item.strip()) >= 3:
                    # add it to the list we will create the dataframe with
                    activity_name_list.append(item.strip())
                    # remove identified activity name from the copy
                    name_split_copy.remove(item)
                    # and then join the remaining splits as a single string and add it to the
                    # list that contains all the descriptions
                    activity_description_list.append(" ".join(name_split_copy))
                    # on to the next row's split
                    break

    # Create dataframe with all lists above
    caljobs_act_code_dictionary = pd.DataFrame({"activity_code":activity_code_list, "activity_name": activity_name_list, "activity_description": activity_description_list})
    # remove trailing and leading spaces for * in some of the descriptions
    caljobs_act_code_dictionary['activity_description'] = caljobs_act_code_dictionary['activity_description'].str.replace(r"\s*\*\s+", "", regex=True)
    # Fix scrambled columns. Often when camelot-py misdetects cell boundaries or a row is split
    # across a page break, it will be processed as an additional row.
    missing_140 = caljobs_act_code_dictionary.loc[141,'activity_name'] + " " + caljobs_act_code_dictionary.loc[141,'activity_description']
    caljobs_act_code_dictionary.loc[140,'activity_description'] = missing_140
    # Remove unnecessary index before writing out CSV
    caljobs_act_code_dictionary = caljobs_act_code_dictionary.drop(index = 141, axis=0).reset_index(drop=True)
    # Create new column to identify originator of the activity according to first character of the activity code
    caljobs_act_code_dictionary["activity_originator"] = caljobs_act_code_dictionary["activity_code"].apply(lambda x: "System" if x[0].isnumeric() else "Employer" if x[0]=="E" else "Follow-up")
    # Save CSV
    caljobs_act_code_dictionary.to_csv("output/caljobs_activity_codes_dictionary.csv", index=False)