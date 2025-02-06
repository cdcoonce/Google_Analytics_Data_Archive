import pandas as pd
import numpy as np

def Doc_To_Secret_Code(url):
    ## Read in the data
    df_list = pd.read_html(url, encoding="utf-8", header=0)
    df = df_list[0]

    
    max_x = df["x-coordinate"].max()
    max_y = df["y-coordinate"].max()

    ## Create Blank grid
    grid = np.full((max_y + 1, max_x + 1), " ", dtype=str)

    for _, row in df.iterrows():
        x = int(row["x-coordinate"])
        y = int(max_y - row["y-coordinate"])
        char = row["Character"]
        grid[y][x] = char

    for row in grid:
        print("".join(row))

## Start the Function
gdoc = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"#
Doc_To_Secret_Code(gdoc)