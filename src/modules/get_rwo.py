import pandas as pd
from pandas import DataFrame


def rwo_data_reader(filename, Type="rate"):
    with open(f"{filename}") as f:
        lines = f.readlines()

    if Type == "rate":
        df = pd.DataFrame(
            [line.split("\t")[:5] for line in lines[6:]],
            columns=["Year", "Oil_Rate", "Water_Rate", "Cumul_Oil", "Cumul_Water"],
        )
    elif Type == "period":
        df = pd.DataFrame(
            [line.split("\t")[:6] for line in lines[6:]],
            columns=["Year", "Oil_Prd", "Water_Prd", "Gas_Prd", "Water_Inj", "Gas_Inj"],
        )

    df = df.apply(pd.to_numeric, errors="coerce", downcast="float")

    if Type == "rate":
        df = df[df["Year"] % 365 == 0]

    return df
