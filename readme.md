# HSBC statements
This solution and repository contains python objects for processing HSBC bank statements and prepare csv files for analysis on YNAB and other software packages.

## Pre-requisite steps -
1. Install tabula from this path: https://tabula.technology/
2. (optional) Install/get subscription for YNAB: https://www.youneedabudget.com/
3. Create folder path like so:
    - \root_path\
    - \root_path\<year>\1-tabula-output\
    - \root_path\<year>\2-cleaned\
    - \root_path\<year>\3-processed\
    - \root_path\<year>\4-ynab\
4. Download pdf statement and put in \root_path\<year>\0-pdf\
5. Open tabula, and generate csv, paste in \root_path\<year>\1-tabula-output\
6. Open file from step 2, and clean up as follows
    - no header needed
    - 6 columns: date, transaction type, payee, outflow, inflow, balance
    - some columns may have shifted... adjust them
    - sometimes strange characters in first row etc... remove them
    - save file
7. Open \root_path\Balances.csv
    - Confirm date column is yyyy-mm-dd
    - Add new row for current month
    - Populate opening, closing balance from pdf
    - Drag-fill 'ThisMonth_Closing_NextMonth_Opening_Reconciled' for previous row and confirm it is TRUE

## Script steps -  
1. Execute python script/docker container with root_path as argument
2. Populate 'Stmt_Balance_Notebook_Balance_Reconciled' if TRUE, if not investigate
3. (optional)Load file from \root_path\<year>\4-ynab\ into YNAB