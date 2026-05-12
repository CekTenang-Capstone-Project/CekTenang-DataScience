import re
import pandas as pd
import numpy as np

def parse_number(value):
    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    if text == "":
        return np.nan

    match = re.search(r"-?\d+(\.\d+)?", text)

    if match:
        return float(match.group(0))

    return np.nan


def parse_date(value):
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()

    if text == "":
        return pd.NaT

    date = pd.to_datetime(text, errors="coerce")

    if pd.isna(date):
        date = pd.to_datetime(text, errors="coerce", dayfirst=True)

    return date
