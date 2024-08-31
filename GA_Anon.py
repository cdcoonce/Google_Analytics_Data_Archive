    ## Imports
import os
import pandas as pd
import uuid
import csv
import openpyxl

    ## Load File
file_path = "Google_Analytics/properties.xlsx"
properties = pd.read_excel(file_path, engine='openpyxl')

    ## Validate File
print(properties.head())

    ## Generate Tokens for Each Column
property_name_tokens = {name: str(uuid.uuid4()) for name in properties['property_name'].unique()}
property_id_tokens = {id: str(uuid.uuid4()) for id in properties['property_id'].unique()}
view_id_tokens = {view: str(uuid.uuid4()) for view in properties['view_id'].unique()}

    ## Save the mapping to a CSV file for each column
mapping_file_path = "Google_Analytics/token_mapping.csv"
with open(mapping_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Column", "Original Value", "Token"])
    
        # Write mapping for property_name
    for original_value, token in property_name_tokens.items():
        writer.writerow(["property_name", original_value, token])
    
        # Write mapping for property_id
    for original_value, token in property_id_tokens.items():
        writer.writerow(["property_id", original_value, token])
    
        # Write mapping for view_id
    for original_value, token in view_id_tokens.items():
        writer.writerow(["view_id", original_value, token])

    ## Anonymize Data
properties_anon = [
    {
        "property_name": property_name_tokens[row['property_name']],
        "property_id": property_id_tokens[row['property_id']],
        "view_id": view_id_tokens[row['view_id']]
    }
    for _, row in properties.iterrows()
]

anon_df = pd.DataFrame(properties_anon)
print("Anonymized Data:\n", anon_df)

    ## Save the anonymized data to a CSV file
anon_file_path = "Google_Analytics/anon_properties.csv"
anon_df.to_csv(anon_file_path, index=False)

print(f"Token mapping saved to {mapping_file_path}")
print(f"Anonymized data saved to {anon_file_path}")