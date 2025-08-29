import pandas as pd

def clean_bank_rate_data(input_filepath: str, output_filepath: str) -> None:
    """
    Cleans and processes the Bank of England bank rate history data.

    This function performs the following steps:
    1.  Loads the source CSV file.
    2.  Renames columns to a standard format ('date', 'Bank_Rate').
    3.  Converts the 'Date Changed' column from 'DD Mon YY' format to datetime objects.
    4.  Resamples the data from an "on-change" basis to a regular monthly series,
        forward-filling the rate to subsequent months.
    5.  Filters the data to the range: January 2011 to June 2024.
    6.  Saves the cleaned, monthly data to a new CSV file.

    Args:
        input_filepath (str): The file path for the raw bank rate data from the user.
        output_filepath (str): The file path to save the cleaned CSV data.
    """
    try:
        # --- 1. Load Data ---
        # Assumes the CSV has columns 'Date Changed' and 'Rate'
        df = pd.read_csv(input_filepath)
        
        # --- 2. Rename Columns ---
        df.rename(columns={'Date Changed': 'date', 'Rate': 'Bank_Rate'}, inplace=True)

        # --- 3. Convert Date and Set Index ---
        # Use format='%d %b %y' to correctly parse dates like "05 May 22"
        df['date'] = pd.to_datetime(df['date'], format = "%d-%m-%Y")
        df.set_index('date', inplace=True)
        
        # Ensure the rate is a number
        df['Bank_Rate'] = pd.to_numeric(df['Bank_Rate'])
        
        # Sort chronologically to ensure correct resampling
        df.sort_index(inplace=True)

        # --- 4. Resample to Monthly Frequency ---
        # Resample to the end of each month ('M').
        # Use 'ffill()' (forward fill) to carry the last known rate forward.
        df_monthly = df.resample('M').ffill()
        
        # Use 'bfill()' (backward fill) to handle the very first period
        # if the dataset starts after our desired start date.
        df_monthly.bfill(inplace=True)
        
        # Turn the date index back into a column
        df_monthly.reset_index(inplace=True)

        # --- 5. Filter to the Specified Date Range ---
        start_date = '2011-01-01'
        end_date = '2024-06-30'
        mask = (df_monthly['date'] >= start_date) & (df_monthly['date'] <= end_date)
        df_final = df_monthly.loc[mask].copy()
        
        # --- 6. Save the Cleaned Data ---
        df_final.to_csv(output_filepath, index=False)
        
        print(f"Successfully cleaned and resampled Bank Rate data.")
        print(f"Output saved to '{output_filepath}'")
        print(f"Data now covers the period from {df_final['date'].min().date()} to {df_final['date'].max().date()}.")
        
    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use this script ---

# 1. Save this code as a Python file (e.g., `clean_script.py`).
# 2. Make sure your bank rate data file is in the same folder.
# 3. Change the INPUT_FILE variable to the exact name of your CSV file.
# 4. Run the script from your terminal: python clean_script.py

# DEFINE INPUT FILENAME HERE
INPUT_FILE = "..//Original Data//Bank of England Database.csv" 
    
# DEFINE OUTPUT FILENAME HERE
OUTPUT_FILE = "bank_rate_cleaned.csv"
    
clean_bank_rate_data(INPUT_FILE, OUTPUT_FILE)