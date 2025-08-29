import pandas as pd

def clean_and_merge_gt_data(file_mapping: dict, output_filepath: str) -> None:
    """
    Cleans, processes, and merges multiple Google Trends CSV files.

    This function performs the following steps for each file:
    1.  Loads the CSV, skipping initial header rows.
    2.  Renames columns to a standard format ('date' and a specific GT name).
    3.  Converts the 'Month' column (YYYY-MM) to a proper end-of-month date.
    4.  Merges all individual DataFrames into a single master DataFrame.
    5.  Filters the final data to the range: January 2011 to June 2024.
    6.  Saves the cleaned, combined data to a new CSV file.

    Args:
        file_mapping (dict): A dictionary where keys are file paths and values
                             are the desired final column names.
        output_filepath (str): The file path to save the cleaned CSV data.
    """
    try:
        cleaned_dfs = []

        # --- 1. Loop through and clean each file ---
        for file_path, col_name in file_mapping.items():
            # Load the data, skipping the first 2 rows of metadata
            df = pd.read_csv(file_path, skiprows=2)
            
            # Rename the columns to 'date' and the specific trend name
            df.columns = ['date', col_name]
            
            # Convert 'Month' (e.g., '2011-01') to an end-of-month datetime object
            df['date'] = pd.to_datetime(df['date']) + pd.offsets.MonthEnd(0)
            
            # Ensure the trend data is numeric
            df[col_name] = pd.to_numeric(df[col_name])
            
            cleaned_dfs.append(df)

        # --- 2. Merge all cleaned DataFrames ---
        # Start with the first dataframe and iteratively merge the others
        df_merged = cleaned_dfs[0]
        for df_to_merge in cleaned_dfs[1:]:
            df_merged = pd.merge(df_merged, df_to_merge, on='date', how='outer')

        # --- 3. Filter to the specified date range ---
        start_date = '2011-01-01'
        end_date = '2024-06-30'
        mask = (df_merged['date'] >= start_date) & (df_merged['date'] <= end_date)
        df_final = df_merged.loc[mask].copy()

        # Sort by date chronologically
        df_final.sort_values(by='date', inplace=True)

        # --- 4. Save the Cleaned Data ---
        df_final.to_csv(output_filepath, index=False)
        print(f"Successfully cleaned and merged Google Trends data. Saved to '{output_filepath}'")
        
    except FileNotFoundError as e:
        print(f"Error: An input file was not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use this script ---
# 1. Save this code as a Python file (e.g., `clean_gt.py`).
# 2. Place your four Google Trends CSV files in the same directory.
# 3. Run the script. It will generate the 'google_trends_cleaned.csv' file.

# Define the mapping of files to their final column names as per the proposal
GT_FILES = {
        "..//Original Data//GT_Public_Interest.csv": "GT_Awareness_General",
        "..//Original Data//GT_Awareness.csv": "GT_Awareness_Consideration",
        "..//Original Data//GT_Infra.csv": "GT_Infrastructure_Concern",
        "..//Original Data//GT_range.csv": "GT_Range_Anxiety"
    }

# Define the desired name for the final cleaned file
OUTPUT_FILE = "google_trends_cleaned.csv"

# Execute the function
clean_and_merge_gt_data(GT_FILES, OUTPUT_FILE)