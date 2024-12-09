from __future__ import nested_scopes
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse

def inspect_cell(cell):
    if isinstance(cell, dict):
        print(f"found a dictionary: {cell}")
    elif isinstance(cell, list):
        print(f"Found a list: {cell}")
    else:
        print(f"Cell value: {cell}")

def cell_contains_nested_dict(cell):
    return isinstance(cell, dict)

def handle_nulls(df):
    df = df.fillna(0)

def parse_date(date_string):
        try:
            parsed_date = parse(date_string)
            formatted_date = parsed_date.strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            return pd.NaT

def validate_data(file_path, numeric_metrics, start_date, end_date):
    try:
        df = pd.read_csv(file_path)
        df['ga:date'] = df['ga:date'].apply(parse_date)

        # Finding Null's
        #null_summary = df.isnull().sum()
        #print(f"Null values summary by column:\n {null_summary}")

        #null_rows = df[df.isnull().any(axis=1)]
        #print(f"Rows with any null values;\n {null_rows}")

        #null_details = df.isnull().stack()
        #print("Detailed view of null values:\n", null_details[null_details])

        # Filling Null's

        #df = handle_nulls(df)

        # Initial Sanity Checks
        num_rows, num_columns = df.shape
        if df.shape[0] == 0 or df.shape[1] == 0:
            return False, "No data or columns found", start_date, end_date, num_rows, num_columns

        # Check for Null Values
        if df.isnull().sum().any() and start_date != '(Other)':
            return False, "Null values found", start_date, end_date, num_rows, num_columns

        # Data Type Validation
        try:
            df['ga:date'] = pd.to_datetime(df['ga:date'], format='%Y-%m-%d')
        except Exception as e:
            return False, f"Date format issue: {e}", start_date, end_date, num_rows, num_columns

        # Extract metric names from numeric_metrics
        metric_names = [metric['expression'] for metric in numeric_metrics]

        for metric in metric_names:
            if metric in df.columns and not pd.api.types.is_numeric_dtype(df[metric]):
                return False, f"{metric} is not numeric", start_date, end_date, num_rows, num_columns

        # Range Checks
        if 'ga:users' in df.columns and (df['ga:users'] < 0).any():
            return False, "Negative values found in ga:users", start_date, end_date, num_rows, num_columns
        if 'ga:sessions' in df.columns and (df['ga:sessions'] < 0).any():
            return False, "Negative values found in ga:sessions", start_date, end_date, num_rows, num_columns
        if 'ga:bounceRate' in df.columns and not ((df['ga:bounceRate'] >= 0) & (df['ga:bounceRate'] <= 100)).all():
            return False, "Bounce rate out of range", start_date, end_date, num_rows, num_columns

        return True, "Validation passed", start_date, end_date, num_rows, num_columns
    except Exception as e:
        return False, f"Error processing file: {e}", start_date, end_date, num_rows, num_columns

def main():
    report_type = ['Page Dimensions report', 'Date and Source Dimensions only', 'Event Dimensions report']

    properties_df = pd.read_excel('properties.xlsx')
    report = []

    for _, row in properties_df.iterrows():
        property_name = row['property_name']
        view_id = str(row['view_id'])
        base_dir = Path(f"C:/Users/e012413/OneDrive - OneAmerica Financial Partners, Inc/Documents/Google Analytics/BackUp/")
        property_name_dir = base_dir / property_name

        for type in report_type:
            report_dir = property_name_dir / type

            if type in ['Page Dimensions report', 'Date and Source Dimensions only']:
                numeric_metrics = [
                    {'expression': 'ga:users'},
                    {'expression': 'ga:newUsers'},
                    {'expression': 'ga:pageviews'},
                    {'expression': 'ga:uniquePageviews'},
                    {'expression': 'ga:sessions'},
                    {'expression': 'ga:avgSessionDuration'},
                    {'expression': 'ga:bounces'},
                    {'expression': 'ga:bounceRate'},
                    {'expression': 'ga:avgTimeOnPage'}
                ]
            else:
                numeric_metrics = [
                    {'expression': 'ga:users'},
                    {'expression': 'ga:newUsers'},
                    {'expression': 'ga:pageviews'},
                    {'expression': 'ga:sessions'},
                    {'expression': 'ga:avgSessionDuration'}
                ]

            if not report_dir.exists():
                print(f"{property_name} {type} doesn't exist.")
                report.append((property_name, type, None, "N/A", False, "Reports not available","N/A", "N/A", None, None))
                continue

            for csv_file in report_dir.glob("*.csv"):
                df = pd.read_csv(report_dir/csv_file.name)

                #print(df.map(cell_contains_nested_dict))

                #print(df.dtypes)

                #print(df.map(inspect_cell))

                start_date = df['ga:date'].min()
                end_date = df['ga:date'].max()
                year = (str(csv_file.name)[5:9])
                valid, message, start_date, end_date, num_rows, num_columns = validate_data(csv_file, numeric_metrics, start_date, end_date)
                report.append((property_name, type, year, csv_file.name, valid, message, start_date, end_date, num_rows, num_columns))
                    #report.append((property_name, type, year, "N/A", False, "Report not available", "N/A", "N/A", None))

    # Save detailed report to a CSV file
    detailed_report_df = pd.DataFrame(report, columns=['Property', 'Report Type', 'Year', 'File', 'Valid', 'Message', 'start_date', 'end_date', 'num_rows', 'num_columns'])
    detailed_report_df.to_csv('detailed_validation_report.csv', index=False)

    # Generate summary report
    #detailed_report_df['date'] = pd.to_datetime(detailed_report_df['date'])

    summary_report = detailed_report_df.groupby(['Property', 'Report Type']).agg(
        total_files=pd.NamedAgg(column='Property', aggfunc='count'),
        valid_files=pd.NamedAgg(column='Valid', aggfunc=lambda x: (x == True).sum()),
        invalid_files=pd.NamedAgg(column='Valid', aggfunc=lambda x: (x == False).sum()),
        first_day=pd.NamedAgg(column='start_date', aggfunc='min'),
        last_day=pd.NamedAgg(column='end_date', aggfunc='max'),
        number_of_rows=pd.NamedAgg(column = 'num_rows', aggfunc= "sum"),
        avg_number_of_rows=pd.NamedAgg(column ='num_rows', aggfunc='mean'),
        min_number_of_rows=pd.NamedAgg(column ='num_rows', aggfunc='min'),
        max_number_of_rows=pd.NamedAgg(column ='num_rows', aggfunc='max')
    ).reset_index()

    summary_report.to_csv('summary_validation_report.csv', index=False)
    print("Validation completed. Reports generated: detailed_validation_report.csv and summary_validation_report.csv")

if __name__ == '__main__':
    main()

