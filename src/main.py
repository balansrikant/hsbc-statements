"""Process HSBC statements

Process statements and produce convenient usable csv files for analysis

Arguments:
root_path - where account summary and investment files are stored

Steps:
1. Perform pre-requisite steps from the readme doc
2. Run jupyter notebook specifying folder location as argument
3. Populate 'Stmt_Balance_Notebook_Balance_Reconciled' if TRUE
   , if not investigate
4. (optional) Load file from /<year>/4-ynab/ into YNAB

"""

import sys
import os
from numpy import NaN
import pandas as pd
import csv
import pathlib


def get_file_paths(root_path: str, year_path: str):
    """Get tabula file locations and balances file"""

    if year_path != "":
        tabula_path = os.path.join(root_path, 'tabula-output', year_path)
    else:
        tabula_path = os.path.join(root_path, 'tabula-output')
    balances_file = os.path.join(root_path, 'Balances.csv')

    tabula_files = [{'date': f[0:10],
                     'filename': f,
                     'path': os.path.join(dp, f)
                     }
                    for dp, dn, filenames in os.walk(tabula_path)
                    for f in filenames
                    if (os.path.splitext(f)[1] == '.csv')
                    and ('_processed' not in os.path.splitext(f)[0])
                    and ('_ynab' not in os.path.splitext(f)[0])]

    return tabula_files, balances_file


def get_balances(balances_file: str) -> pd.DataFrame:
    """Load balances from csv into dataframe

    Keyword arguments:
    :balances_file - path of balances csv file

    Returns:
    :df_balances - dataframe containing balances
    """
    df_balances = pd.read_csv(balances_file)
    cols = ['statement_date', 'opening_balance',
            'closing_balance',
            'thismonth_closing_nextmonth_opening_reconciled',
            'stmt_balance_notebook_balance_reconciled',
            ]
    df_balances.columns = cols
    cols = ['statement_date', 'opening_balance', 'closing_balance']
    df_balances = df_balances[cols]
    df_balances = df_balances.astype({"statement_date": 'datetime64',
                                      "opening_balance": 'float64',
                                      "closing_balance": 'float64',
                                      })
    return df_balances


def transform_floats(param: str) -> float:
    """Convert string into float"""
    param.replace(',', '')
    if param == '.':
        param = 0.0
    if param == NaN:
        param = 0
    param = float(param)

    return param


def transform_payee(param: str):
    """Convert payee into friendly name, category"""

    with open('/static/payee_mapping.csv') as f:
        mapping = [{k: str(v) for k, v in row.items()}
                   for row in csv.DictReader(f, skipinitialspace=True)]

    for search_string in mapping:
        if search_string['payee'] in param.lower():
            repl = search_string['repl']
            cat = search_string['category']

    return repl, cat


def process_tabula_csv(file: dict) -> pd.DataFrame:
    """Clean raw tabula dataframe"""

    date = file['date']
    cols = ['date', 'tr_type', 'payee', 'outflow', 'inflow', 'balance']
    df = pd.read_csv(file['path'], columns=cols)
    df = df[['date', 'payee', 'outflow', 'inflow', 'balance']]
    df['date'] = date

    # change data types
    df['date'] = pd.to_datetime(df['date'])
    for col in ['balance', 'outflow', 'inflow']:
        df[col] = df[col].apply(transform_floats).apply(pd.Series)

    # remove balance carried forward rows within dataset
    df_temp = df.iloc[1:-1, :]
    idx = df_temp.loc[df_temp['payee'].str.contains('balance'), :].index
    df.drop(idx, inplace=True)

    # combine multi-line payees
    for idx, row in df.iterrows():
        if ((df.loc[idx, 'outflow'] == 0.0)
           and (df.loc[idx, 'inflow'] == 0.0)
           and (df.loc[idx, 'balance'] == 0.0)):
            df.loc[idx+1, 'payee'] = df.loc[idx, 'payee'] \
                                         + ' ' \
                                         + df.loc[idx+1, 'payee']
        df.loc[idx+1, 'date'] = df.loc[idx, 'date']

    df.drop(df[(df['outflow'] == 0.0)
            & (df['inflow'] == 0.0)
            & (df['balance'] == 0.0)].index, inplace=True)
    df['date'].fillna(method='ffill', inplace=True)

    # transform payee
    df[['payee', 'category']] = df['payee'] \
        .apply(transform_payee).apply(pd.Series)

    return df


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT_PATH = sys.argv[1]
        YEAR_PATH = sys.argv[2]
    else:
        ROOT_PATH = '/data/'
        YEAR_PATH = '2021'

    # get folders
    tabula_files,\
        balances_file = get_file_paths(ROOT_PATH, YEAR_PATH)
