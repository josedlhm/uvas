import pandas as pd

def create_historical_data(source_csv_path, destination_csv_path):

# Load the source DataFrame
    source_df = pd.read_csv(source_csv_path)

    # Extract the last row from the source DataFrame
    last_row = source_df[['date', 'object_count']].iloc[-1]

    # Attempt to load the destination DataFrame, or create it if it doesn't exist
    try:
        destination_df = pd.read_csv(destination_csv_path)
    except FileNotFoundError:
        destination_df = pd.DataFrame(columns=['date', 'object_count'])

    # Check if the current date already exists in the destination DataFrame
    if last_row['date'] in destination_df['date'].values:
        # If the date exists, update the row
        destination_df.loc[destination_df['date'] == last_row['date'], 'object_count'] = last_row['object_count']
    else:
        # If the date does not exist, append the new row
        destination_df = pd.concat([destination_df, last_row.to_frame().T], ignore_index=True)
    # Ensure the date column is treated as datetime
    destination_df['date'] = pd.to_datetime(destination_df['date']) 

    # Save the updated destination DataFrame back to CSV
    destination_df.to_csv(destination_csv_path, index=False)

    print(f"Data for {last_row['date']} updated or appended successfully to {destination_csv_path}.")
    return destination_df
