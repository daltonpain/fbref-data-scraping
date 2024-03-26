__all__ = [
    "RENAME_COLUMNS",
    "COLUMNS",
    "CATEGORIES",
    "scrape_and_process",
    "tidy_columns",
]

# ----------------------------------- Imports -----------------------------------
import requests
import warnings
import pandas as pd
from bs4 import BeautifulSoup

warnings.filterwarnings(
    "ignore", message="Passing literal html to 'read_html' is deprecated"
)
pd.options.mode.chained_assignment = None  # default='warn'

# ----------------------------------- Constants -----------------------------------


RENAME_COLUMNS = {
    "shooting": "SHOOT",
    "passing": "PASS",
    "pass_types": "PT",
    "goal_and_shot_creation": "GSC",
    "defensive_actions": "DA",
    "possession": "POSS",
    "miscellaneous": "MISC",
}

COLUMNS = {
    "shooting": ["Squad", "Sh", "Dist"],
    "passing": ["Squad", "TotDist", "PrgDist", "Att", "KP"],
    "pass_types": ["Squad", "Crs", "CK"],
    "goal_and_shot_creation": [
        "Squad",
        "PassLive",
        "PassDead",
        "TO",
        "Sh",
        "Fld",
        "Def",
    ],
    "defensive_actions": ["Squad", "Tkl", "Att", "Blocks", "Int"],
    "possession": ["Squad", "Poss"],
    "miscellaneous": ["Squad", "CrdY", "CrdR", "Fls", "Recov"],
}

CATEGORIES = [
    "shooting",
    "passing",
    "passing_types",
    "gca",
    "defense",
    "possession",
    "misc",
]

# ----------------------------------- Functions -----------------------------------

def scrape_and_process(url, cols, season):
    """Scrape and process the data from the website."""
    
    # scrape (grab data from the website)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    table_data = pd.read_html(str(table))[0]

    # process (format the data a bit)
    table_data.columns = table_data.columns.droplevel([0])
    selected_data = table_data[cols]
    selected_data.loc[:, "SEASON"] = season
    
    return selected_data


def tidy_columns(df, col):
    """Further formatting that needs to be done after scraping and processing."""

    df.reset_index(drop=True, inplace=True)
    df.columns = df.columns.str.upper()

    # append category to the column names
    new_columns = [
        (
            f"{RENAME_COLUMNS[col]}_{column}"
            if column not in ["SQUAD", "SEASON"]
            else column
        )
        for column in df.columns
    ]
    df.rename(columns=dict(zip(df.columns, new_columns)), inplace=True)
    
    # give duplicated columns unique names
    last_col = pd.Series(df.columns)
    for dup in last_col[last_col.duplicated()].unique(): 
        last_col[last_col[last_col == dup].index.values.tolist()] = [dup + str(i) if i != 0 else dup for i in range(sum(last_col == dup))]
    df.columns = last_col
    
    return df
