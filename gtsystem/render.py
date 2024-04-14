import pandas as pd
from IPython.display import display, Markdown, Image
from IPython.core.display import HTML

def md(text):
    display(Markdown(text))

def img(url):
    return Image(url=url)

def df(df, rows=None):
    # Set display options for max column width and precision
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.precision', 2)

    # Define CSS to hide the index and apply other styles
    styles = [
        dict(selector="th", props=[("font-size", "10pt"), ("text-align", "left")]),
        dict(selector="td", props=[
            ("text-align", "left"),
            ("word-wrap", "break-word"),
            ("overflow", "hidden"),
            ("text-overflow", "ellipsis")]),
        dict(selector=".index_name", props=[("display", "none")]),  # Hides the index name (if any)
        dict(selector=".row_heading, .blank", props=[("display", "none")])  # Hides the row headers (index)
    ]

    # Slice the DataFrame if top_n is specified
    if rows is not None:
        df = df.head(rows)

    # Format the DataFrame to display NaNs as empty strings and apply styles
    formatted_df = df.style.format(None, na_rep='').set_table_styles(styles)

    # Display the DataFrame
    return formatted_df