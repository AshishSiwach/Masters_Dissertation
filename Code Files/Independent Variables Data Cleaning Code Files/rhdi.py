import pandas as pd

def clean_rhdi_data(input_filepath: str, output_filepath: str) -> None:
    """
    Cleans and processes quarterly Real Household Disposable Income (RHDI) data.

    This function performs the following steps:
    1.  Loads the source CSV file from the ONS.
    2.  Renames columns to a more user-friendly format.
    3.  Converts the 'Period' column (e.g., "2011 Q1") to datetime objects,
        setting them to the end of each quarter.
    4.  Upsamples the quarterly data to a monthly frequency.
    5.  Uses linear interpolation to estimate values for the new, empty months.
    6.  Filters the data to only include dates from January 2011 onwards.
    7.  Saves the cleaned, monthly data to a new CSV file.

    Args:
        input_filepath (str): The file path for the raw RHDI data.
        output_filepath (str): The file path to save the cleaned CSV data.
    """
    try:
        # --- 1. Load Data and Initial Cleaning ---
        df_rhdi = pd.read_csv(input_filepath)

        # Rename columns for clarity and consistency
        df_rhdi.rename(columns={'Period': 'date', 'Value': 'RHDI_per_head'}, inplace=True)

        # --- 2. Convert 'date' from 'YYYY QX' to datetime objects ---
        # Map each quarter to the end-of-month date for that quarter.
        df_rhdi['date'] = df_rhdi['date'].str.replace(r' Q1', '-03-31')
        df_rhdi['date'] = df_rhdi['date'].str.replace(r' Q2', '-06-30')
        df_rhdi['date'] = df_rhdi['date'].str.replace(r' Q3', '-09-30')
        df_rhdi['date'] = df_rhdi['date'].str.replace(r' Q4', '-12-31')
        df_rhdi['date'] = pd.to_datetime(df_rhdi['date'])

        # --- 3. Resample to Monthly and Interpolate ---
        # Set date as the index to perform time-series operations
        df_rhdi.set_index('date', inplace=True)

        # Resample the quarterly data to a monthly frequency ('M').
        # This creates NaN values for the 2 new months within each quarter.
        df_monthly = df_rhdi.resample('M').asfreq()

        # Use linear interpolation to create a smooth estimate for the missing monthly values
        df_monthly['RHDI_per_head'] = df_monthly['RHDI_per_head'].interpolate(method='linear')

        # --- 4. Final Filtering and Formatting ---
        # Filter the data to start from January 1, 2011
        df_monthly = df_monthly[(df_monthly.index >= '2011-01-01') & (df_monthly.index <= '2024-06-30')]
        
        # Round the interpolated values for cleanliness
        df_monthly['RHDI_per_head'] = df_monthly['RHDI_per_head'].round(4)

        # Reset the index to turn the date back into a column
        df_monthly.reset_index(inplace=True)

        # --- 5. Save the Cleaned Data ---
        df_monthly.to_csv(output_filepath, index=False)
        print(f"Successfully cleaned data and saved to '{output_filepath}'")
        print("\n--- First 5 rows of the final data: ---")
        print(df_monthly.head())

    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Execute the function ---
if __name__ == '__main__':
    # Define the input and output file names
    INPUT_FILE = "..//Original Data//Real_HH_Disposable_Income.csv"
    OUTPUT_FILE = "rhdi_cleaned_2011_2024_cleaned.csv"

    # Run the cleaning process
    clean_rhdi_data(INPUT_FILE, OUTPUT_FILE)