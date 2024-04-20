import pandas as pd
from IPython.display import display, Markdown, Image
import base64
import re

def md(text):
    display(Markdown(text))

def img(url):
    return Image(url=url)

def _display_base64_image(base64_string):
    image_data = base64.b64decode(base64_string)
    display(Image(data=image_data))

def _contains_markdown_table(s):
    # Simplified regex pattern
    # Checks for the presence of "-----" and at least three pipes "|"
    pattern = r'(?:\|[^|\n]*?){3,}.*\n[-| :]*[-]{2,}[-| :]*'
    return bool(re.search(pattern, s))

def chat(chat_json):
    # Define role to emoji mapping
    role_emoji = {
        "system": "⚙️",
        "user": "👤",
        "assistant": "💬"
    }
    
    # Start the markdown output
    markdown_output = []
    
    for message in chat_json:
        role = message["role"]
        content = message["content"]
        
        # Check for mixed content type in user messages
        if role == "user" and isinstance(content, list):
            # Process mixed content types
            text_lines = []
            for item in content:
                if item['type'] == 'text':
                    text_lines.append(f"{role_emoji[role]}**{item['text']}**")
                elif item['type'] == 'image_url':
                    display(Image(url=item['image_url']['url']))
                elif item['type'] == 'image' and item['source']['type'] == 'base64':
                    _display_base64_image(item['source']['data'])
            markdown_line = '\n'.join(text_lines)
        elif role == "system":
            # System messages in italics
            markdown_line = f"{role_emoji[role]} *{content}*"
        elif role == "user":
            # Simple user messages in bold
            markdown_line = f"{role_emoji[role]} **{content}**"
        else:
            # Assistant messages in plain text with an emoji
            markdown_line = f"{role_emoji[role]}\n{content}" \
                if _contains_markdown_table(content) else f"{role_emoji[role]} {content}"
        
        markdown_output.append(markdown_line)
    
    # Display all text content as Markdown
    display(Markdown('\n\n'.join(markdown_output)))

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