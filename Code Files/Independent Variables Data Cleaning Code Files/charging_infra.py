import pandas as pd

def clean_charging_infra_data_by_year_month(input_filepath: str, output_filepath: str) -> None:
    """
    Loads a clean CSV of quarterly UK charging data with separate Year and
    Month columns, resamples it to a monthly series, and prepares it for the
    master dataset.

    This is the final corrected version that robustly handles resampling and
    interpolation to produce the correct output.

    Args:
        input_filepath (str): The file path for the clean quarterly CSV data.
        output_filepath (str): The file path to save the cleaned monthly CSV data.
    """
    try:
        # --- 1. Load and Prepare Quarterly Data ---
        df_quarterly = pd.read_csv(input_filepath)
        df_quarterly.columns = ['year', 'month', 'total_charging_devices']

        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        df_quarterly['month'] = df_quarterly['month'].map(month_map)
         
        # Create a proper datetime column from the separate year and month columns.
        df_quarterly['date'] = pd.to_datetime(df_quarterly[['year', 'month']].assign(day=1))
        df_quarterly = df_quarterly[['date', 'total_charging_devices']].set_index('date')

        # --- 2. Correctly Resample and Interpolate ---
        # Resample to a DAILY frequency, which allows for a smooth interpolation.
        df_daily = df_quarterly.resample('D').asfreq()
        df_daily['total_charging_devices'] = df_daily['total_charging_devices'].interpolate(method='linear')
        
        # Now, sample the last day of each month to get our clean monthly series.
        df_monthly_interp = df_daily.resample('ME').last()
        df_monthly_interp.reset_index(inplace=True)

        # --- 3. Create Full Date Range and Merge ---
        # Create the complete date range required for the final project.
        full_date_range = pd.date_range(start='2011-01-01', end='2024-06-30', freq='ME')
        df_final = pd.DataFrame(full_date_range, columns=['date'])

        # Left-merge the interpolated data. This correctly places the data from
        # 2015 onwards and leaves NaNs for the earlier, empty years.
        df_final = pd.merge(df_final, df_monthly_interp, on='date', how='left')

        # --- 4. Handle Missing Pre-2015 Data ---
        # Fill the NaN values for the pre-2015 period with 0.
        df_final['total_charging_devices'] = df_final['total_charging_devices'].fillna(0)
        
        # Convert the column to a clean integer type.
        df_final['total_charging_devices'] = df_final['total_charging_devices'].round(0).astype(int)

        # --- 5. Rename and Save ---
        df_final.rename(columns={'total_charging_devices': 'Charging_Infrastructure'}, inplace=True)

        df_final.to_csv(output_filepath, index=False)
        print(f"Successfully cleaned charging infrastructure data. Saved to '{output_filepath}'")
        print("\n--- First 5 rows of the cleaned data (showing 0s for early years): ---")
        print(df_final.head())
        print("\n--- Last 5 rows of the cleaned data (showing correct recent data): ---")
        print(df_final.tail())
        
    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



INPUT_FILE = "charging_infra.csv"
OUTPUT_FILE = "charging_infra_cleaned.csv"
clean_charging_infra_data_by_year_month(INPUT_FILE, OUTPUT_FILE)