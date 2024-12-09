'''
Created on Jun 17, 2024

@author: cdcoonce
'''

import os
import time
import random
from pathlib import Path
from urllib import response
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

def initialize_analyticsreporting(key_file_location, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes)
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    return analytics

def file_exists(directory, file_name):
    file_join = os.path.join(directory, file_name)
    return os.path.isfile(file_join)

## Event Report Functions

def get_event_report(analytics, view_id, start_date, end_date, is_yearly, page_token=None):
    dimensions = [
        {'name': 'ga:date'},
        {'name': 'ga:browser'},
        {'name': 'ga:deviceCategory'},
        {'name': 'ga:region'},
        {'name': 'ga:source'},
        {'name': 'ga:pageTitle'},
        {'name': 'ga:eventCategory'},
        {'name': 'ga:eventAction'},
        {'name': 'ga:eventLabel'}
        ]
   
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                'viewId': view_id,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': [
                    {'expression': 'ga:users'},
                    {'expression': 'ga:newUsers'},
                    {'expression': 'ga:pageviews'},
                    #{'expression': 'ga:uniquePageviews'},
                    {'expression': 'ga:sessions'},
                    {'expression': 'ga:avgSessionDuration'},
                    #{'expression': 'ga:bounces'},
                    #{'expression': 'ga:bounceRate'},
                    #{'expression': 'ga:avgTimeOnPage'}
                ],
                'dimensions': dimensions,
                'pageSize': 10000,
                'pageToken': page_token,
                'samplingLevel': 'LARGE'
                }
            ]
        }
    ).execute()

def fetch_event_data(key_file_location, view_id, property_name, start_date, end_date, max_rows_per_file=100000):
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    analytics = initialize_analyticsreporting(key_file_location, scopes)
    data = []
    page_token = None
    is_yearly = True
    file_index = 1
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    num_rows = 0

    print(f"               ***")
    print(f"Fetching event data for {start_date} to {end_date}.\n")

    try:
        while True:
            num_rows += 10000
            print(f"Up to {num_rows} rows read.")

            response = get_event_report(analytics, view_id, start_date, end_date, is_yearly, page_token)
     
            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

                for row in report.get('data', {}).get('rows', []):
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    row_data = dimensions

                    for values in dateRangeValues:
                        row_data.extend(values.get('values'))

                    data.append(row_data)

                    if len(data) >= max_rows_per_file:
                        save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
                        data = []
                        file_index += 1
            page_token = response.get('reports', [])[0].get('nextPageToken')

            if not page_token:
                break
            
        if data and len(data) <= 30000:
            print(f"\n               ***")
            print(f"Less than 30,000 Rows for {start_date} to {end_date}.\n Switching to yearly report.\n")
            response = yearly_fetch_event_data(key_file_location, view_id, property_name, start_date, end_date)
            return response
        
        if data:
            save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)

        return response

    except HttpError as er:
        print(f"An error occured:\n {er}")

def RateLimited_fetch_event_data(key_file_location, view_id, property_name, start_date, end_date, max_retries = 2):
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    specific_date = pd.to_datetime('2022-04-02')    
    directory = Path(f"MonthlyBackUp/{property_name}/{year}/Event Dimensions report/")
    file_name = f'Month_{month}_Year_{year}_events_part_1.csv'

    file_found = file_exists(directory, file_name)

    if file_found:
        print(f"Monthly file found, skipping Month {month} year {year}\n")
        return
    
    for i in range(max_retries):
        response = fetch_event_data(key_file_location, view_id, property_name, start_date, end_date)
        if response:
            return response
        else:
            delay = (2 ** i) + (random.random())

            print(f"\n               ***")
            print(f"Retry {i + 1} of {max_retries} after {delay:.2f} seconds\n")

            time.sleep(delay)
    print(f"\n               ***")
    print(f"Maximum retries reached. Exiting...\n")

def save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month):
    headers = dimensionHeaders + [header['name'] for header in metricHeaders]
    df = pd.DataFrame(data, columns=headers)
   
    # Format Results
   
    if 'ga:date' in df.columns:
        df['ga:date'] = pd.to_datetime(df['ga:date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    if 'ga:avgTimeOnPage' in df.columns:
        df['ga:avgTimeOnPage (Excel - hh:mm:ss)'] = df['ga:avgTimeOnPage'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df['ga:avgSessionDuration (Excel - hh:mm:ss)'] = df['ga:avgSessionDuration'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df.rename(columns = {'ga:avgSessionDuration' : 'ga:avgSessionDuration (in seconds)'}, inplace = True)

    if 'ga:avgTimeOnPage' in df.columns:
        df.rename(columns = {'ga:avgTimeOnPage' : 'ga:avgTimeOnPage (in seconds)'}, inplace = True)

    if 'ga:bounceRate' in df.columns:
        df['ga:bounceRate'] = df['ga:bounceRate'].astype(float) / 100   

## Create output directory if one doesn't exist
    if file_index == 1:
        print(f"\n               ***")
        print(f"Locating output directory:\n")

    output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Event Dimensions report') 
    output_dir.mkdir(parents=True, exist_ok=True)
     
    output_file = output_dir /  f'Month_{month}_Year_{year}_events_part_{file_index}.csv'
    
    if file_index == 1:
        print(f"output directory:\n{output_dir}\n")
        print(f"Saving data...\n")

    df.to_csv(output_file, index=False)

    print(f"\n Monthly Event data for {property_name} from {month}_{year} saved to:\n {output_file}\n")

## Retry as Yearly Event Report

def yearly_fetch_event_data(key_file_location, view_id, property_name, start_date, end_date, max_rows_per_file=100000):
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    analytics = initialize_analyticsreporting(key_file_location, scopes)
    data = []
    page_token = None
    is_yearly = True
    file_index = 1
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    num_rows = 0

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    print(f"               ***")
    print(f"Trying yearly report from {start_date} to {end_date}.\n")

    try:
        while True:
            num_rows += 10000  
            print(f"Up to {num_rows} rows read.")

            response = get_event_report(analytics, view_id, start_date, end_date, is_yearly, page_token)
                 
            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

                for row in report.get('data', {}).get('rows', []):
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    row_data = dimensions

                    for values in dateRangeValues:
                        row_data.extend(values.get('values'))

                    data.append(row_data)

                    if len(data) >= max_rows_per_file:
                        yearly_save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
                        data = []
                        file_index += 1

            page_token = response.get('reports', [])[0].get('nextPageToken')

            if not page_token:
                break
            
        if data:
            yearly_save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
        
        return response

    except HttpError as er:
        print(f"An error occured:\n {er}")

def yearly_save_events_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month):
    headers = dimensionHeaders + [header['name'] for header in metricHeaders]
    df = pd.DataFrame(data, columns=headers)
   
    # Format Results
   
    if 'ga:date' in df.columns:
        df['ga:date'] = pd.to_datetime(df['ga:date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    if 'ga:avgTimeOnPage' in df.columns:
        df['ga:avgTimeOnPage (Excel - hh:mm:ss)'] = df['ga:avgTimeOnPage'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df['ga:avgSessionDuration (Excel - hh:mm:ss)'] = df['ga:avgSessionDuration'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df.rename(columns = {'ga:avgSessionDuration' : 'ga:avgSessionDuration (in seconds)'}, inplace = True)

    if 'ga:avgTimeOnPage' in df.columns:
        df.rename(columns = {'ga:avgTimeOnPage' : 'ga:avgTimeOnPage (in seconds)'}, inplace = True)

    if 'ga:bounceRate' in df.columns:
        df['ga:bounceRate'] = df['ga:bounceRate'].astype(float) / 100   

## Create output directory if one doesn't exist
    if file_index == 1:
        print(f"\n               ***")
        print(f"Locating output directory:\n")
   
    output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Event Dimensions report') 
    output_dir.mkdir(parents=True, exist_ok=True)
     
    output_file = output_dir /  f'Year_{year}_events_part_{file_index}.csv'
    
    if file_index == 1:
        print(f"output directory:\n{output_dir}\n")
        print(f"Saving data...\n")
    
    df.to_csv(output_file, index=False)

    print(f"Yearly Event data for {property_name} from {year} saved to:\n{output_file}\n")

## Page Dimensions Functions

def get_report(analytics, view_id, start_date, end_date, is_yearly, page_token=None):
    if is_yearly:
        specific_date = pd.to_datetime('2022-01-02')
    else:
        specific_date = pd.to_datetime('2022-04-02')    

    if pd.to_datetime(start_date) >= specific_date :
        dimensions = [
            {'name': 'ga:date'},
            {'name': 'ga:browser'},
            {'name': 'ga:deviceCategory'},
            {'name': 'ga:region'},
            {'name': 'ga:source'},
            {'name': 'ga:pageTitle'},
            {'name': 'ga:landingPagePath'},
            {'name': 'ga:exitPagePath'}
        ]
    else:
        dimensions = [
            {'name': 'ga:date'},
            {'name': 'ga:source'},
        ]

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                'viewId': view_id,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': [
                    {'expression': 'ga:users'},
                    {'expression': 'ga:newUsers'},
                    {'expression': 'ga:pageviews'},
                    {'expression': 'ga:uniquePageviews'},
                    {'expression': 'ga:sessions'},
                    {'expression': 'ga:avgSessionDuration'},
                    {'expression': 'ga:bounces'},
                    {'expression': 'ga:bounceRate'},
                    {'expression': 'ga:avgTimeOnPage'}
                ],
                'dimensions': dimensions,
                'pageSize': 10000,
                'pageToken': page_token,
                'samplingLevel': 'LARGE'
                }
            ]
        }
    ).execute()

def fetch_data(key_file_location, view_id, property_name, start_date, end_date, max_rows_per_file=100000):
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    analytics = initialize_analyticsreporting(key_file_location, scopes)
    data = []
    page_token = None
    file_index = 1
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    num_rows = 0
    is_yearly = False

    print(f"               ***")
    print(f"Fetching page data for {start_date} to {end_date}.\n")

    try:
        while True:
            response = get_report(analytics, view_id, start_date, end_date, is_yearly, page_token)
            num_rows += 10000
            print(f"Up to {num_rows} rows read.")
            
            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

                for row in report.get('data', {}).get('rows', []):
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    row_data = dimensions

                    for values in dateRangeValues:
                        row_data.extend(values.get('values'))

                    data.append(row_data)

                    if len(data) >= max_rows_per_file:
                        print(f"\n{max_rows_per_file} reached:\n Saving file as part{file_index}.\n")
                        save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
                        data = []
                        file_index += 1
                        print(f"Fetching data for part {file_index}.\n")

            page_token = response.get('reports', [])[0].get('nextPageToken')

            if not page_token:
                break

        if data and file_index == 1 and len(data) <= 30000:
            print(f"\n               ***")
            print(f"Less than 30,000 Rows for {start_date} to {end_date}. \nSwitching to yearly report.\n")
            response = yearly_fetch_data(key_file_location, view_id, property_name, start_date, end_date)
            return response

        if data:
            save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
        
        return response

    except HttpError as er:
        print(f"An error occured:\n {er}")

def RateLimited_fetch_data(key_file_location, view_id, property_name, start_date, end_date, max_retries = 2):
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    specific_date = pd.to_datetime('2022-04-02')
    if pd.to_datetime(start_date) >= specific_date:         
        directory = Path(f"MonthlyBackUp/{property_name}/{year}/Page Dimensions report/") ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Event Dimensions report')
        file_name = f'Month_{month}_Year_{year}_part_1.csv'
    else:
        directory = Path(f'MonthlyBackUp/{property_name}/{year}/Date and Source Dimensions only/') ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Event Dimensions report')
        file_name = f'Month_{month}_Year_{year}_part_1.csv'

    file_found = file_exists(directory, file_name)

    if file_found:
        print(f"Montly file found, skipping Month {month} year {year}\n")
        return

    for i in range(max_retries):
        response = fetch_data(key_file_location, view_id, property_name, start_date, end_date)
        if response:
            return response
        else:
            delay = (2 ** i) + (random.random())

            print(f"\n              ***")
            print(f"Retry {i + 1} of {max_retries} after {delay:.2f} seconds\n")

            time.sleep(delay)
    print(f"\n               ***")
    print(f"Maximum retries reached. Exiting...\n")   

def save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month):
    headers = dimensionHeaders + [header['name'] for header in metricHeaders]
    df = pd.DataFrame(data, columns=headers)

    # Format Results
   
    if 'ga:date' in df.columns:
        df['ga:date'] = pd.to_datetime(df['ga:date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    if 'ga:avgTimeOnPage' in df.columns:
        df['ga:avgTimeOnPage (Excel - hh:mm:ss)'] = df['ga:avgTimeOnPage'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df['ga:avgSessionDuration (Excel - hh:mm:ss)'] = df['ga:avgSessionDuration'].astype(float) / 86400
    
    specific_date = pd.to_datetime('2022-04-02')

    if pd.to_datetime(start_date) < specific_date :
        col = df.pop('ga:avgSessionDuration (Excel - hh:mm:ss)')
        df.insert(8, 'ga:avgSessionDuration (Excel - hh:mm:ss)', col)

    if pd.to_datetime(start_date) >= specific_date :
        col = df.pop('ga:avgSessionDuration (Excel - hh:mm:ss)')
        df.insert(14, 'ga:avgSessionDuration (Excel - hh:mm:ss)', col)

    if 'ga:avgSessionDuration' in df.columns:
        df.rename(columns = {'ga:avgSessionDuration' : 'ga:avgSessionDuration (in seconds)'}, inplace = True)

    if 'ga:avgTimeOnPage' in df.columns:
        df.rename(columns = {'ga:avgTimeOnPage' : 'ga:avgTimeOnPage (in seconds)'}, inplace = True)

    if 'ga:bounceRate' in df.columns:
        df['ga:bounceRate'] = df['ga:bounceRate'].astype(float) / 100      

## Create output directory if it doesn't exist 
    if file_index == 1:
        print(f"\n               ***")
        print(f"Locating output directory:\n")

    if pd.to_datetime(start_date) < specific_date :
        output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Date and Source Dimensions only') ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Date and Source Dimensions only')
        output_dir.mkdir(parents=True, exist_ok=True)      

        output_file = output_dir / f'Month_{month}_Year_{year}_part_{file_index}.csv'
    else:
        output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Page Dimensions report') ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Page Dimensions report')
        output_dir.mkdir(parents=True, exist_ok=True)      

        output_file = output_dir / f'Month_{month}_Year_{year}_part_{file_index}.csv'

    if file_index == 1:
        print(f"output directory:\n{output_dir}\n")
        print(f"Saving data...\n")

    df.to_csv(output_file, index=False)

    print(f"\nMonthly data for {property_name} from {month}_{year}_part{file_index} saved to:\n{output_file}\n")

## Retry as Yearly Report

def yearly_fetch_data(key_file_location, view_id, property_name, start_date, end_date, max_rows_per_file=100000):
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    analytics = initialize_analyticsreporting(key_file_location, scopes)
    data = []
    page_token = None
    is_yearly = True
    file_index = 1
    year = pd.to_datetime(start_date).year
    month = pd.to_datetime(start_date).month
    num_rows = 0

    if start_date == '2022-12-01':
        start_date = f"{year}-01-02"
        end_date = f"{year}-12-31"
    else:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

    print(f"Trying yearly report from {start_date} to {end_date}.\n")

    try:
        while True:
            response = get_report(analytics, view_id, start_date, end_date, is_yearly, page_token)
            num_rows += 10000

            print(f"Up to {num_rows} rows read.")

            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

                for row in report.get('data', {}).get('rows', []):
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    row_data = dimensions

                    for values in dateRangeValues:
                        row_data.extend(values.get('values'))

                    data.append(row_data)

                    if len(data) >= max_rows_per_file:
                        print(f"\n{max_rows_per_file} reached:\n Saving file as part{file_index}.\n")
                        yearly_save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)
                        data = []
                        file_index += 1
                        print(f"Fetching data for part {file_index}.\n")

            page_token = response.get('reports', [])[0].get('nextPageToken')
   
            if not page_token:
                break

        if data:
                yearly_save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month)        
        
        return response

    except HttpError as er:
        print(f"An error occured:\n {er}")

def yearly_save_to_csv(data, dimensionHeaders, metricHeaders, view_id, property_name, start_date, end_date, file_index, year, month):
    headers = dimensionHeaders + [header['name'] for header in metricHeaders]
    df = pd.DataFrame(data, columns=headers)

    # Format Results
   
    if 'ga:date' in df.columns:
        df['ga:date'] = pd.to_datetime(df['ga:date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    if 'ga:avgTimeOnPage' in df.columns:
        df['ga:avgTimeOnPage (Excel - hh:mm:ss)'] = df['ga:avgTimeOnPage'].astype(float) / 86400

    if 'ga:avgSessionDuration' in df.columns:
        df['ga:avgSessionDuration (Excel - hh:mm:ss)'] = df['ga:avgSessionDuration'].astype(float) / 86400
    
    specific_date = pd.to_datetime('2022-01-02')

    if pd.to_datetime(start_date) <= specific_date :
        col = df.pop('ga:avgSessionDuration (Excel - hh:mm:ss)')
        df.insert(8, 'ga:avgSessionDuration (Excel - hh:mm:ss)', col)

    if pd.to_datetime(start_date) >= specific_date :
        col = df.pop('ga:avgSessionDuration (Excel - hh:mm:ss)')
        df.insert(14, 'ga:avgSessionDuration (Excel - hh:mm:ss)', col)

    if 'ga:avgSessionDuration' in df.columns:
        df.rename(columns = {'ga:avgSessionDuration' : 'ga:avgSessionDuration (in seconds)'}, inplace = True)

    if 'ga:avgTimeOnPage' in df.columns:
        df.rename(columns = {'ga:avgTimeOnPage' : 'ga:avgTimeOnPage (in seconds)'}, inplace = True)

    if 'ga:bounceRate' in df.columns:
        df['ga:bounceRate'] = df['ga:bounceRate'].astype(float) / 100      

## Create output directory if it doesn't exist 
    #output_dir = Path(f'{property_name}/{year}/Page Dimensions report or .../ Data and Source Dimensions only')

    print(f"\n               ***")
    print(f"Locating Output directory:\n")

    if pd.to_datetime(start_date) <= pd.to_datetime('2022-01-01') :
        output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Date and Source Dimensions only')
        output_dir.mkdir(parents=True, exist_ok=True)      

        output_file = output_dir / f'Year_{year}_part_{file_index}.csv'
    else:
        output_dir = Path(f'MonthlyBackUp/{property_name}/{year}/Page Dimensions report')
        output_dir.mkdir(parents=True, exist_ok=True)      

        output_file = output_dir / f'Year_{year}_part_{file_index}.csv'

    print(f"output directory:\n{output_dir}\n")
    print(f"Saving data...\n")
    
    df.to_csv(output_file, index=False)

    print(f"Yearly data for {property_name} from {year}, part {file_index}, saved to: \n{output_file}\n")

## Main 

def main():
    key_file_location = 'KFL/*********-#######-#*##**######.json'

## Multiple Views  
  # Read property names and view IDs from Excel file
    properties_file = 'properties.xlsx'
    properties_df = pd.read_excel(properties_file)  
   
## Using Date Ranges from spreadsheet
    date_ranges_file = 'dateRanges_Monthly.xlsx'
    date_ranges_df = pd.read_excel(date_ranges_file)
    date_ranges_df['start_date'] = date_ranges_df['start_date'].dt.strftime('%Y-%m-%d')
    date_ranges_df['end_date'] = date_ranges_df['end_date'].dt.strftime('%Y-%m-%d')

    date_ranges_events_file = 'dateRanges_Monthly_Events.xlsx'
    date_ranges_events_df = pd.read_excel(date_ranges_events_file)
    date_ranges_events_df['start_event_date'] = date_ranges_events_df['start_event_date'].dt.strftime('%Y-%m-%d')
    date_ranges_events_df['end_event_date'] = date_ranges_events_df['end_event_date'].dt.strftime('%Y-%m-%d')  

    for _, row in properties_df.iterrows():
        property_name = row['property_name']
        property_id = row['property_id']
        view_id = str(row['view_id'])

        property_name = property_name + '_' + property_id

        print(f"\nWorking on:\nProperty {property_name}.\n")

        print(f"Iterating through monthly date ranges.\n")

        for _, row in date_ranges_df.iterrows():
            start_date = row['start_date']
            end_date = row['end_date']
            year = pd.to_datetime(start_date).year
            month = pd.to_datetime(start_date).month
            specific_date = pd.to_datetime('2022-04-02')

            if pd.to_datetime(start_date) >= specific_date:         
                directory = Path(f"MonthlyBackUp/{property_name}/{year}/Page Dimensions report/") ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Event Dimensions report')
                file_name = f'Year_{year}_part_1.csv'
            else:
                directory = Path(f'MonthlyBackUp/{property_name}/{year}/Date and Source Dimensions only/') ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Event Dimensions report')
                file_name = f'Year_{year}_part_1.csv'

            file_found = file_exists(directory, file_name)

            print(f"\n               ***")
            print(f"Checking for data from {start_date} to {end_date}.\n")

            print(f"Does a yearly file already exist?:   {file_found}\n")

            if file_found and start_date[:4] == str(year):
                print(f"Skipped Month {month} year {year} until {int(year) - 1}-12-31\n")
                continue
            else:
                RateLimited_fetch_data(key_file_location, view_id, property_name, start_date, end_date)
        
        print(f"\nIterating through monthly event date ranges.\n")

        for _, row in date_ranges_events_df.iterrows():
            start_date = row['start_event_date']
            end_date = row['end_event_date']
            year = pd.to_datetime(start_date).year
            month = pd.to_datetime(start_date).month

            directory = Path(f'MonthlyBackUp/{property_name}/{year}/Event Dimensions report/') ## Path(f'K:/Enterprise Marketing/Strategy and Insights/Web Analytics/Google Analytics 3 Back Up Data/{property_name}/{year}/Event Dimensions report') 
            file_name = f'Year_{year}_events_part_1.csv'

            file_found = file_exists(directory, file_name)

            print(f"\n               ***")
            print(f"Checking for event data from {start_date} to {end_date}.\n")

            print(f"Does a yearly event file already exist?:   {file_found}\n")

            if file_found and start_date[:4] == str(year):
                print(f"Skipped Month {month} year {year} until {int(year) - 1}-01-01\n")
                continue
            else:
                RateLimited_fetch_event_data(key_file_location, view_id, property_name, start_date, end_date)
        
        print(f"******\n Property {property_name} has been backed up to:\n {directory} \n\n******\n\nMoving to next property...\n")

if __name__ == '__main__':
    main()