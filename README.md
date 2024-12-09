# Google Analytics 3 Data Archive

In March of 2022 Google Analytics 3 (Universal Analytics) announced the push to transition all it's users to Google Analytics 4. July 1, 2024 was the official end date for access to all historical data in Google Analytics 3.

At the end of May 2024, I was tasked with exporting all the historical data for 70 unique properties (sites or apps) to a previously determined location on enterprise servers. This required me to develop a course of action that would allow me to obtain all data points that the stakeholders required within a little over a month.

## 1. Initial Task

The list of properties that have been collecting website traffic and analytics from Google Analytics 3, also known as Universal Analytics was just a month away from being permanently deleted due to Google Analytics moving to the brand new Google Analytics 4.

## 2. Gathering Requirements

After researching what data was available to the stakeholder, We decided on specific sets of data that could be extracted into csv files seperated by year and month.

### Data Dictionary

[View as Spreadsheet](https://docs.google.com/spreadsheets/d/13eqFhGQ_bdxNRTU8BlooypEwH7F9-BJVKpy3hR-SzhQ/edit?usp=sharing)

![CSV Data](/Google_Analytics_Public/DataDictionary.png)

## 3. Extracting the Data

The first option for extracting the data for all these properties is to use the Google Analytics Dashboards and then export them to be saved as csv files. Testing this option made it clear it would take too long to export all the data this way.

I decided I would make a python script to connect to the properties remotely using the Google Analytics API to extract and format the data myself.

View the Code here: [main_v6.1.py](https://github.com/cdcoonce/Google_Analytics_Public/blob/master/main_v6.1_MonthYear.py)

## 4. Validation

I wanted to make sure the data was intact after automating the data retrieval process. I created python validation script to read through the newly created csv files and check for anomalies.

View the Code here: [GA_DataValidation_V1.2.py](https://github.com/cdcoonce/Google_Analytics_Public/blob/master/GA_DataValidation_%20V1.2.py)

## 5. Results

### Anonymized Property Names

To protect the privacy of the property owners who were part of this Data Move, I anonymized the property names using a third python script and token mapping.

View the Code here: [GA_Anon_Validation.py](https://github.com/cdcoonce/Google_Analytics_Public/blob/master/GA_Anon_Validation.py)

### Summary Validation Report

[View as Spreadsheet](https://docs.google.com/spreadsheets/d/1F05nZMdK5_r98D2E3aJOobeM-Fz4xS3M8UnuvmmGNoE/edit?usp=sharing)

![CSV Data](/Google_Analytics_Public/SumValidationReport.png)

### Detailed Validation Report

[View as Spreadsheet](https://docs.google.com/spreadsheets/d/1brbFTA92cjV2FmXa69LhpQHLT7anhESjWphB_XoY2Nc/edit?usp=sharing)

![CSV Data](/Google_Analytics_Public/DetValidationReport.png)