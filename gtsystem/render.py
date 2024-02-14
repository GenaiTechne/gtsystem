import pandas as pd
from IPython.display import display, Markdown

def md(text):
    display(Markdown(text))

def df(df):
    # Set display options for max column width
    pd.set_option('display.max_colwidth', None)

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

    # Apply the styles
    styled_df = df.style.set_table_styles(styles)

    # Display the DataFrame
    return styled_df
