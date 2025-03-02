# Google Analytics 3 Data Archive

*A Data Preservation & Automation Project*

---

## Table of Contents

- [Google Analytics 3 Data Archive](#google-analytics-3-data-archive)
  - [Table of Contents](#table-of-contents)
  - [Overview \& Objectives](#overview--objectives)
  - [Project Requirements](#project-requirements)
  - [Data Dictionary](#data-dictionary)
  - [Data Extraction Process](#data-extraction-process)
    - [Why Not Use the GA Dashboard?](#why-not-use-the-ga-dashboard)
    - [Python to the Rescue](#python-to-the-rescue)
  - [Validation \& Data Integrity](#validation--data-integrity)
  - [Anonymizing Sensitive Data](#anonymizing-sensitive-data)
  - [Results \& Insights](#results--insights)
    - [Validation Reports](#validation-reports)
    - [Key Takeaways](#key-takeaways)
  - [Next Steps \& Final Thoughts](#next-steps--final-thoughts)

---

## Overview & Objectives

Google announced that **Google Analytics 3 (Universal Analytics)** would be deprecated by **July 1, 2024**, after which historical data would no longer be accessible. In **May 2024**, I was tasked with **exporting all historical analytics data** from **70 unique properties** (sites/apps) to an enterprise server, ensuring that stakeholders retained access to the data they needed—even after Universal Analytics was gone.

**Key Objectives**:

- **Identify** all 70 properties that needed data extraction.
- **Define** data requirements and metrics based on stakeholder needs.
- **Automate** the data extraction process to meet a tight deadline (a little over a month).
- **Validate & secure** the exported data to ensure data integrity.

---

## Project Requirements

1. **Transition Deadline**: Google Analytics 3 data would become permanently inaccessible after July 1, 2024.  
2. **Historical Scope**: We needed to capture monthly analytics from the earliest tracking date up to June 2024.  
3. **File Format**: Stakeholders requested the data in `.csv` format, separated by **year and month**.  
4. **Scalability**: The solution had to handle **70 properties**, each with potentially high volumes of monthly data.  
5. **Automation**: Manual exports through the Google Analytics dashboard would be impractical, so a scripting or API-based solution was necessary.

---

## Data Dictionary

To clarify what would be extracted and how, I developed and finalized a **Data Dictionary** with stackholders. It defines the metrics and dimensions required for each `.csv` file.

[**View the Data Dictionary Spreadsheet**](https://docs.google.com/spreadsheets/d/13eqFhGQ_bdxNRTU8BlooypEwH7F9-BJVKpy3hR-SzhQ/edit?usp=sharing)

![CSV Data Dictionary](/Google_Analytics_Public/assets/DataDictionary.png)

---

## Data Extraction Process

### Why Not Use the GA Dashboard?

Exporting data manually from the **Google Analytics** dashboard was **time-consuming** and **error-prone**, especially for 70 properties spanning multiple years. It became clear we needed an **automated** approach.

### Python to the Rescue

I developed a **Python script** to:

1. **Authenticate** with the Google Analytics API.
2. **Iterate** through each property.
3. **Extract & Transform** the data monthly and yearly as `.csv` files.
4. **Save** the `.csv` files to the specified enterprise server location.

[**View the Python Script**](https://github.com/cdcoonce/Google_Analytics_Data_Archive/blob/master/main_v6.1.py)

This script drastically reduced the time needed and minimized manual errors.

---

## Validation & Data Integrity

Once the extraction completed, I needed to ensure the resulting `.csv` files were **accurate** and **complete**.

1. **Automated Checks**: A Python validation script scanned each file, verifying record counts, date ranges, and expected column headers.  
2. **Anomaly Detection**: The script flagged any outliers or missing values for manual review.

[**View the Validation Code**](https://github.com/cdcoonce/Google_Analytics_Data_Archive/blob/master/GA_DataValidation_%20V1.2.py)

---

## Anonymizing Sensitive Data

I had concerns about sharing property names and other identifying attributes for this project. To address this:

1. I built a **token mapping** system using a third Python script.  
2. This script **replaced** sensitive property names with unique IDs before storing or sharing the files.

[**View the Anonymization Script**](https://github.com/cdcoonce/Google_Analytics_Data_Archive/blob/master/GA_Anon_Validation.py)

---

## Results & Insights

### Validation Reports

- **Summary Validation Report**: Provides a high-level overview of validation metrics, highlighting any issues that need further investigation.  
  [**View Spreadsheet**](https://docs.google.com/spreadsheets/d/1F05nZMdK5_r98D2E3aJOobeM-Fz4xS3M8UnuvmmGNoE/edit?usp=sharing)

  ![Summary Validation](/Google_Analytics_Public/assets/SumValidationReport.png)

- **Detailed Validation Report**: Delves deeper into any anomalies, listing potential errors by row or data category.  
  [**View Spreadsheet**](https://docs.google.com/spreadsheets/d/1brbFTA92cjV2FmXa69LhpQHLT7anhESjWphB_XoY2Nc/edit?usp=sharing)

  ![Detailed Validation](/Google_Analytics_Public/assets/DetValidationReport.png)

### Key Takeaways

- **Efficiency**: Automated scripting significantly reduced manual effort, meeting the tight month-long deadline.  
- **Accuracy**: Validation checks caught data discrepancies early, preserving data integrity.  
- **Security & Anonymity**: Sensitive data was protected via token-based anonymization.

---

## Next Steps & Final Thoughts

1. **Archival Strategy**: With all the `.csv` files successfully archived, an ongoing strategy is to integrate these historical data sets with **Google Analytics 4** or other BI tools for longitudinal analysis.  
2. **Further Automation**: Future improvements might include a **scheduled job** to handle incremental data exports or re-checks against anomalies.  
3. **Documentation**: Detailed documentation of the scripts and procedures ensures maintainability and helps onboard new team members.

**Overall**, this project highlights the importance of **planning, automation, and validation** in large-scale data extraction tasks. It demonstrates how Python and a well-organized workflow can make a monumental task—like backing up an entire organization’s Google Analytics history—manageable and accurate.
