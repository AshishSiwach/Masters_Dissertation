import pandas as pd

def clean_cpi_data_revised(input_filepath: str, output_filepath: str) -> None:
    """
    Cleans and processes the simplified, wide-format CPI data, filtering
    for the specific date range of Jan 2011 to Jun 2024.

    This function performs the following steps:
    1.  Loads the source CSV file.
    2.  Cleans column names by stripping whitespace.
    3.  "Melts" the dataframe from a wide format to a long format.
    4.  Creates a standardized 'date' column.
    5.  Coerces non-numeric CPI values (like '..') into NaN and removes them.
    6.  Filters the data to the range: January 2011 to June 2024.
    7.  Saves the cleaned, monthly data to a new CSV file.

    Args:
        input_filepath (str): The file path for the raw CPI data.
        output_filepath (str): The file path to save the cleaned CSV data.
    """
    try:
        # --- 1. Load and Clean Data ---
        df = pd.read_excel(input_filepath, skiprows=1)
        df.columns = df.columns.str.strip()

        # --- 2. Reshape Data ---
        month_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df_long = df.melt(
            id_vars=['Year'],
            value_vars=month_cols,
            var_name='Month',
            value_name='CPI'
        )

        # --- 3. Handle Data Types and Missing Values ---
        df_long.dropna(subset=['Year', 'Month'], inplace=True)
        df_long['CPI'] = pd.to_numeric(df_long['CPI'], errors='coerce')
        df_long.dropna(subset=['CPI'], inplace=True)
        df_long['Year'] = df_long['Year'].astype(int)
        
        # --- 4. Create Date Column ---
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        df_long['Month_Num'] = df_long['Month'].map(month_map)
        df_long['date'] = pd.to_datetime(
            df_long['Year'].astype(str) + '-' + df_long['Month_Num'].astype(str) + '-01'
        )
        df_long['date'] = df_long['date'] + pd.offsets.MonthEnd(0)
        
        # --- 5. Filter to the specified date range ---
        start_date = '2011-01-01'
        end_date = '2024-06-30'
        mask = (df_long['date'] >= start_date) & (df_long['date'] <= end_date)
        df_final = df_long.loc[mask].copy()

        # --- 6. Sort and Save ---
        df_final = df_final[['date', 'CPI']]
        df_final.sort_values(by='date', inplace=True)
        
        df_final.to_csv(output_filepath, index=False)
        print(f"Successfully cleaned and filtered CPI data. Saved to '{output_filepath}'")
        print(f"\nData covers the period from {df_final['date'].min().date()} to {df_final['date'].max().date()}.")

    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Execute the function ---
INPUT_FILE = "..//Original Data//cpi.xlsx"
OUTPUT_FILE = "cpi_cleaned_2011_2024.csv"
clean_cpi_data_revised(INPUT_FILE, OUTPUT_FILE)