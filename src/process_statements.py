"""Process HSBC statements

Process statements and produce convenient usable csv files for analysis

Arguments:
root_path -- where account summary and investment files are stored

Steps:
1. Perform pre-requisite steps from the readme doc
2. Run jupyter notebook specifying folder location as argument
3. Populate 'Stmt_Balance_Notebook_Balance_Reconciled' if TRUE
   , if not investigate
4. (optional) Load file from /<year>/4-ynab/ into YNAB

"""

import pandas as pd
import numpy as np
import copy
import os