import pandas as pd

def explore_csv(file_path):
    """
    Loads a CSV file and prints basic information about it.
    """
    try:
        df = pd.read_csv(file_path)
        print("Successfully loaded the CSV file.")
        print("\\nFirst 5 rows of the dataframe:")
        print(df.head())
        print("\\nInformation about the dataframe:")
        df.info()
        print("\\nNumber of missing values in each column:")
        print(df.isnull().sum())
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    explore_csv("archive (3)/amazon.csv")
