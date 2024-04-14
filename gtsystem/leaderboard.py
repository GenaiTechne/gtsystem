import pandas as pd

LEADERS = None

def filter_and_order(ascending=False, **kwargs):
    """
    Filter the dataframe based on the substrings provided in kwargs for specific columns.
    Sort the resulting dataframe based on the 'orderby' parameter if provided, defaults to 'Elo'.

    Example: filtered_df = filter_and_order(df, Model='GPT-4', orderby='Elo')

    Args:
    df (DataFrame): The dataframe to operate on.
    **kwargs: Column names and their corresponding substring values to match.
              The special keyword 'orderby' can be used to specify the column to sort by.
    
    Returns:
    DataFrame: Filtered and sorted DataFrame.
    """
    # Extract the orderby parameter if provided, else default to 'Elo'
    orderby = kwargs.pop('orderby', 'Elo')
    
    # Filter the dataframe
    for column, substring in kwargs.items():
        fildered_df = LEADERS[LEADERS[column].astype(str).str.contains(substring, na=False)]
    
    # Sort the dataframe
    return fildered_df.sort_values(by=orderby, ascending=ascending)

def top_n_sorted(n, columns=['Elo'], ascending=True):
    """
    Return the top N rows from the dataframe sorted by the specified columns.

    Example: top_results = top_n_sorted(filtered_df, 5, columns=['Elo'], ascending=False)

    Args:
    df (DataFrame): The dataframe to operate on.
    n (int): Number of top rows to return.
    columns (list): List of columns to sort by.
    ascending (bool or list of bool): Whether or not the sorting should be in ascending order.

    Returns:
    DataFrame: A DataFrame of the top N sorted rows.
    """
    return LEADERS.sort_values(by=columns, ascending=ascending).head(n)

def top_rank(n):
    return top_n_sorted(n, columns=['Rank'], ascending=True)

def model(model):
    return filter_and_order(ascending=False, Model=model, orderby='Elo')

def vendor(vendor):
    return filter_and_order(ascending=False, Organization=vendor, orderby='Elo')

def read_leaderboard(file_path):
    global LEADERS

    LEADERS = pd.read_excel(file_path)
    return LEADERS
