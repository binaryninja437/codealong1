import pandas as pd
import numpy as np

def clean_amazon_data(file_path):
    """
    Cleans the amazon dataset by handling missing values and correcting data types.
    """
    try:
        df = pd.read_csv(file_path)
        print("Successfully loaded the CSV file.")

        # Clean 'discounted_price' and 'actual_price'
        for col in ['discounted_price', 'actual_price']:
            df[col] = df[col].str.replace('₹', '').str.replace(',', '').astype(float)

        # Clean 'discount_percentage'
        df['discount_percentage'] = df['discount_percentage'].str.replace('%', '').astype(int)

        # Clean 'rating' - there's a row with '|' that needs to be handled
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

        # Clean 'rating_count'
        df['rating_count'] = df['rating_count'].str.replace(',', '', regex=False)
        df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')

        # Handle missing values in 'rating_count'
        mean_rating_count = df['rating_count'].mean()
        df['rating_count'].fillna(mean_rating_count, inplace=True)

        # Handle missing values in 'rating'
        mean_rating = df['rating'].mean()
        df['rating'].fillna(mean_rating, inplace=True)

        print("\nData after cleaning:")
        df.info()

        return df

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    cleaned_df = clean_amazon_data("archive (3)/amazon.csv")
    if cleaned_df is not None:
        cleaned_df.to_csv("amazon_cleaned.csv", index=False)
        print("\nCleaned data saved to amazon_cleaned.csv")
