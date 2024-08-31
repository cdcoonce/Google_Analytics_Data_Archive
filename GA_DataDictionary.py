import pandas as pd
# Define the data dictionary structure
data_dict = {
   'Variable Name': [
       'ga:date', 'ga:browser', 'ga:deviceCategory', 'ga:region', 'ga:source',
       'ga:pageTitle', 'ga:landingPagePath', 'ga:exitPagePath', 'ga:eventCategory', 'ga:eventAction',
       'ga:eventLabel',
       'ga:users', 
       'ga:newUsers', 
       'ga:pageviews', 
       'ga:uniquePageviews',
       'ga:sessions', 
       'ga:avgSessionDuration (in seconds)',
       'ga:avgSessionDuration (Excel - hh:mm:ss)',
       'ga:bounces', 
       'ga:bounceRate',
       'ga:avgTimeOnPage (in seconds)', 
       'ga:avgTimeOnPage (Excel - hh:mm:ss)'
   ],
   'Description': [
       'Date of the data entry.', 
       'The name of users\' browsers (e.g., Chrome, Edge, Firefox, Internet Explorer, Safari).',
       'The type of device: (e.g., desktop, tablet, or mobile.',
       'The state from which the sessions\' IP references. Users\' region ID, derived from their IP addresses or Geographical IDs. In U.S., a region is a State.' ,
       'Source of the traffic (e.g., Google, Direct, Referral).',
       'How the developer named the page descriptively. Often many URLs can have the same Page Title if they are essentially the same content.',
       'The first page in users\' \'Session\'. Think of it as an Entrance Page.',
       'The last page in users\' \'Session\'. They are distinct from Bounces as Exits occur in all Sessions, but \'Bounces\' denote only a single page \'Session\'',
       'Category of the event (e.g., Video, Button Click).', 
       'Action of the event (e.g., Play, Submit).',
       'Label of the event (e.g., Video Name, Form ID).',
       'Number of users who visited the website.',
       'Number of new users who visited the website.', 
       'Total number of pageviews.',
       'Number of unique pageviews.', 
       'Number of sessions initiated by users.',
       'Average duration of a session in seconds.',
       'Average duration of a session in seconds.',
       'Number of bounces (single-page sessions).',
       'Percentage of single-page sessions.', 
       'Average time users spent on a single page.',
       'Average time users spent on a single page.'       
   ],
   'Google Analytics Type' : [
       'Dimension', 'Dimension', 'Dimension', 'Dimension', 'Dimension', 
       'Dimension', 'Dimension', 'Dimension', 'Dimension', 'Dimension', 
       'Dimension', 'Metric', 'Metric', 'Metric', 'Metric', 
       'Metric', 'Metric', 'Metric', 'Metric', 'Metric', 
       'Metric', 'Metric'
   ],
   'Data Type': [
       'Date', 'String', 'String', 'String', 'String', 
       'String', 'String', 'String', 'String', 'String', 
       'String', 'Integer', 'Integer', 'Integer', 'Integer', 
       'Integer', 'Float', 'Float', 'Integer', 'Float',
        'Float',  'Float'
   ],
   'Format': [
       'YYYY-MM-DD', '-', '-', '-', '-', '-', '-', '-', '-', '-',
        '-', '-', '-', '-', '-', '-', 'Time (saved as Float)', 'Time (saved as Float)', '-', 'Percentage (saved as Float 0.XX...)', 
        'Time (saved as Float)', 'Time (saved as Float)'
   ],
   'Possible Values/Range': [
       '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',
       '-', 'Non-negative integers', 'Non-negative integers', 'Non-negative integers',
       'Non-negative integers', 'Non-negative integers', 'Non-negative floats', 'Non-negative floats',
       'Non-negative integers', '0.00-1', 'Non-negative floats', 'Non-negative floats'
   ],
   'Source': [
       'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics',
       'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics',
       'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics',
       'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics', 'Google Analytics', 
       'Google Analytics', 'Google Analytics'
   ],
   'Notes': [
       'Uniform format `%Y-%m-%d`.', '-', '-', '-', '-', '-', 
       'Applicable for Page Dimensions Report.', 
       'Applicable for Page Dimensions Report.', 
       'Applicable for Event Dimensions Report.', 
       'Applicable for Event Dimensions Report.',
       'Applicable for Event Dimensions Report.',
       '-', '-', '-', '-', '-', '-', 
       'ga:avgSessionDuration (in Seconds) / 86240', '-', '-', 
       'ga:avgTimeOnPAge (in Seconds) / 86240', '-'       
   ]
}
# Create a DataFrame from the data dictionary
data_dict_df = pd.DataFrame(data_dict)
# Save the data dictionary to a CSV file
data_dict_df.to_csv('Google_Analytics/data_dictionary.csv', index=False)
print("Data dictionary generated and saved to 'data_dictionary.csv'")