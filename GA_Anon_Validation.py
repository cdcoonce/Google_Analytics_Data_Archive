## Imports
import os
import pandas as pd
import uuid
import csv
import openpyxl

    ## Load File
file_path = "Google_Analytics/detailed_validation_report.xlsx"
file_path2 = "Google_Analytics/summary_validation_report.xlsx"
validation_report = pd.read_excel(file_path, engine='openpyxl')
validation_report2 = pd.read_excel(file_path2, engine='openpyxl')

    ## Load the token map
mapping_file_path = "Google_Analytics/token_mapping.csv"
token_map_df = pd.read_csv(mapping_file_path)

    ## Convert the token map into dictionaries for each column
token_maps = {
    col: dict(zip(token_map_df[token_map_df['Column'] == col]['Original Value'], 
                  token_map_df[token_map_df['Column'] == col]['Token']))
    for col in token_map_df['Column'].unique()
}
print("Token Maps:", token_maps)

    ## Anonymize the validation report
detailed_validation_report_anon = validation_report.copy()
summary_validation_report_anon = validation_report2.copy()

    ## Replace property values using the respective token map
if 'Property' in detailed_validation_report_anon.columns:
    detailed_validation_report_anon['Property'] = detailed_validation_report_anon['Property'].map(token_maps['property_name'])

    ## Save the anonymized validation report to a CSV file
detailed_validation_report_anon_file_path = "Google_Analytics/detailed_validation_report_anon.csv"
detailed_validation_report_anon.to_csv(detailed_validation_report_anon_file_path, index=False)

    ## Replace property values using the respective token map
if 'Property' in summary_validation_report_anon.columns:
    summary_validation_report_anon['Property'] = summary_validation_report_anon['Property'].map(token_maps['property_name'])

    ## Save the anonymized validation report to a CSV file
summary_validation_report_anon_file_path = "Google_Analytics/summary_validation_report_anon.csv"
summary_validation_report_anon.to_csv(summary_validation_report_anon_file_path, index=False)