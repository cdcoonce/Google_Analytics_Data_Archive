    ## imports
import os
import pandas as pd
import uuid
import csv
import openpyxl

    ## Load Properties
file_path = "Google_Analytics/properties.xlsx"
properties = pd.read_excel(file_path, engine='openpyxl')

    ## Validate File
print(properties.head())

    ## Generate Tokens
property_names = properties['property_name'].tolist()
token_map = {name: str(uuid.uuid4()) for name in property_names}

    ## Save the mapping to a CSV file
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Original Name", "Token"]) 
    for name, token in token_map.items():
        writer.writerow([name, token])

    ## Changing Names
properties_anon = [
    {"property_name": token_map[row['property_name']], 
        "property_id": row['property_id'], 
        "view_id": row['view_id']}
    for _, row in properties.iterrows()
    ]

anon_df = pd.DataFrame(properties_anon)
print("Anonymized Data:", anon_df)

anon_df.to_csv(file_path, index=False)