# HSBC statements
This solution and repository contains python objects for processing HSBC bank statements and prepare csv files for analysis on YNAB and other software packages.

#### Steps -

1. Install tabula from this path: https://tabula.technology/
2. (optional) Install/get subscription for YNAB: https://www.youneedabudget.com/
3. Create folder path like so:
    
    \root\
    \root\<year>\1-tabula-output\
    \root\<year>\2-cleaned\
    \root\<year>\3-processed\
    \root\<year>\4-ynab\

4. Download pdf statement and put in \<year>\0-pdf\
5. Open tabula, and generate csv, paste in \<year>\1-tabula-output\
6. Open file from step 2, and clean up as follows
  - no header needed
  - 6 columns: date, transaction type, payee, outflow, inflow, balance
  - some columns may have shifted... adjust them
  - sometimes strange characters in first row etc... remove them
  - save file
7. Open \Balances.csv
  - Confirm date column is yyyy-mm-dd
  - Add new row for current month
  - Populate opening, closing balance from pdf
  - Drag-fill 'ThisMonth_Closing_NextMonth_Opening_Reconciled' for previous row and confirm it is TRUE
8. Run jupyter notebook
9. Populate 'Stmt_Balance_Notebook_Balance_Reconciled' if TRUE, if not investigate
10. Load file from \<year>\4-ynab\ into YNAB