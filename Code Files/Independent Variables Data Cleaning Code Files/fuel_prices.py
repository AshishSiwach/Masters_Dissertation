import pandas as pd

def clean_fuel_price_data(file_list: list, output_filepath: str) -> None:
    """
    Cleans, combines, and processes weekly fuel price data into a monthly series.

    This function performs the following steps:
    1.  Loads and concatenates multiple fuel price CSV files.
    2.  Selects and renames the relevant date, petrol, and diesel price columns.
    3.  Converts the date column to datetime objects.
    4.  Resamples the weekly data to a monthly frequency by calculating the mean price.
    5.  Filters the data to the final range: January 2011 to June 2024.
    6.  Saves the cleaned, monthly data to a new CSV file.

    Args:
        file_list (list): A list of file paths for the raw fuel price data.
        output_filepath (str): The file path to save the cleaned CSV data.
    """
    try:
        # --- 1. Load and Combine Data ---
        # Read each CSV in the list and combine them into a single DataFrame.
        df_list = [pd.read_csv(file) for file in file_list]
        df_combined = pd.concat(df_list, ignore_index=True)

        # --- 2. Select and Rename Columns ---
        # Identify the correct petrol and diesel columns by looking for keywords in their names.
        petrol_col = [col for col in df_combined.columns if 'ULSP' in col and 'Pump price' in col][0]
        diesel_col = [col for col in df_combined.columns if 'ULSD' in col and 'Pump price' in col][0]
        
        # Select only the columns we need and give them standard names.
        df_selected = df_combined[['Date', petrol_col, diesel_col]].copy()
        df_selected.rename(columns={
            'Date': 'date',
            petrol_col: 'Petrol_Price',
            diesel_col: 'Diesel_Price'
        }, inplace=True)

        # --- 3. Convert Date and Handle Data Types ---
        # Convert the 'date' column from string to datetime objects.
        df_selected['date'] = pd.to_datetime(df_selected['date'], format='%d/%m/%Y')
        df_selected.set_index('date', inplace=True)
        
        # Ensure price columns are treated as numbers.
        df_selected['Petrol_Price'] = pd.to_numeric(df_selected['Petrol_Price'])
        df_selected['Diesel_Price'] = pd.to_numeric(df_selected['Diesel_Price'])
        
        # Sort by date to ensure correct time-series processing.
        df_selected.sort_index(inplace=True)

        # --- 4. Resample to Monthly Frequency ---
        # Group the weekly data by month ('M') and calculate the average price for each month.
        df_monthly = df_selected.resample('M').mean()
        
        # Turn the date index back into a regular column.
        df_monthly.reset_index(inplace=True)

        # --- 5. Filter to the Specified Date Range ---
        start_date = '2011-01-01'
        end_date = '2024-06-30'
        mask = (df_monthly['date'] >= start_date) & (df_monthly['date'] <= end_date)
        df_final = df_monthly.loc[mask].copy()

        # Round the final average prices to 2 decimal places.
        df_final['Petrol_Price'] = df_final['Petrol_Price'].round(2)
        df_final['Diesel_Price'] = df_final['Diesel_Price'].round(2)

        # --- 6. Save the Cleaned Data ---
        df_final.to_csv(output_filepath, index=False)
        print(f"Successfully cleaned and combined fuel price data. Saved to '{output_filepath}'")
        
    except FileNotFoundError as e:
        print(f"Error: One of the input files was not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use this script ---
# 1. Save this code as a Python file (e.g., `clean_fuels.py`).
# 2. Place your two fuel CSV files in the same directory.
# 3. Run the script. It will generate the 'fuel_prices_cleaned.csv' file.

if __name__ == '__main__':
    # List of the input files to be combined.
    INPUT_FILES = ["..//Original Data//weekly_fuel_prices_2003_to_2017.csv", "..//Original Data//road_fuel_prices_2018_2025.csv"]
    
    # Desired name for the final cleaned file.
    OUTPUT_FILE = "fuel_prices_cleaned.csv"
    
    clean_fuel_price_data(INPUT_FILES, OUTPUT_FILE)