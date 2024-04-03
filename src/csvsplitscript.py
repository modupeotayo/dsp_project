import os
import pandas as pd
import numpy as np


def introduce_data_issues(df):
    # Add more data issues as needed
    # Introduce missing values
    df.loc[df.sample(frac=0.03).index, 'Air temperature [K]'] = np.nan
    # Introduce out-of-range values
    df.loc[df.sample(frac=0.03).index, 'Process temperature [K]'] = df.loc[df.sample(frac=0.03).index, 'Process temperature [K]'] * 1.1
    # Introduce random noise with different data types
    df.loc[df.sample(frac=0.03).index, 'Torque [Nm]'] = df.loc[df.sample(frac=0.03).index, 'Torque [Nm]'] + np.random.normal(0, 5, size=len(df.sample(frac=0.03))) 

    return df

def split_and_save_data(df, output_folder, num_files):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Calculate the number of rows in each chunk
    chunk_size = len(df) // num_files

    # Split dataset into multiple files
    for i in range(num_files):
        start_index = i * chunk_size
        end_index = start_index + chunk_size if i < num_files - 1 else None
        split_df = df.iloc[start_index:end_index]

        # Save each split dataset to a separate file
        split_df.to_csv(os.path.join(output_folder, f'data_split_{i}.csv'), index=False)

if __name__ == "__main__":
    # Load main dataset
    main_dataset_path = 'predictive_maintenance.csv'
    main_df = pd.read_csv(main_dataset_path)

    # Introduce data issues
    main_df_with_issues = introduce_data_issues(main_df)

    # Split dataset and save to raw-data folder
    output_folder = '../data/raw-data'
    num_files_to_generate = 10
    split_and_save_data(main_df_with_issues, output_folder, num_files_to_generate)
