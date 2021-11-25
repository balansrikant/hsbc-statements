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
import pandas as pd


def get_file_paths(root_path: str, year_path: str):
    """Get folder locations

    Keyword arguments:
    :root_path - path of HSBC files
    :year_path - year to evaluate

    Returns:
    :accounts - list of dicts (accounts)
    """
    tabula_path = os.path.join(root_path, year_path, '1-tabula-output')
    cleaned_path = os.path.join(root_path, year_path, '2-cleaned')
    processed_path = os.path.join(root_path, year_path, '3-processed')
    ynab_path = os.path.join(root_path, year_path, '4-ynab')
    balances_file = os.path.join(root_path, 'Balances.csv')

    return tabula_path, cleaned_path, processed_path, ynab_path, balances_file


def get_tabula_file_list(tabula_path: str) -> list:
    """Get list of files to be processed

    Keyword arguments:
    :tabula_path - folder containing files generated from tabula

    Returns:
    :result - list of dicts (statement_date, filename, full path)
    """
    result = [{'statement_date': f[0:10],
               'filename': f,
               'original_full_path': os.path.join(dp, f)
               }
              for dp, dn, filenames in os.walk(tabula_path)
              for f in filenames
              if (os.path.splitext(f)[1] == '.csv')
              and ('_processed' not in os.path.splitext(f)[0])
              and ('_ynab' not in os.path.splitext(f)[0])]

    return result


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


def clean_tabula_df(df_in: pd.DataFrame) -> pd.DataFrame:
    """Clean raw tabula dataframe

    Keyword arguments:
    :df_in - raw tabula dataframe

    Returns:
    :df_out - cleaned up tabula dataframe
    """
    header_cols = ['date',
                   'transaction_type',
                   'payee',
                   'outflow',
                   'inflow',
                   'balance',
                   ]
    df_out = df_in[header_cols]
    df_out[['payee', 'outflow', 'inflow', 'balance']] = \
        df_out[['payee', 'outflow', 'inflow', 'balance']].astype(str)
    df_out['date'] = pd.to_datetime(
        df_out['date'].str[:2]
        + '-'
        + df_out['date'].str[3:6]
        + '-'
        + '20' + df_out['date'].str[-2:]
    )

    # remove unneeded columns
    cols = ['date', 'payee', 'outflow', 'inflow', 'balance']
    df_out = df_out[cols]
    df_out.reset_index(drop=True, inplace=True)

    # change data types
    df_out.loc[:, 'balance'] = df_out['balance'].str.replace(',', '')
    df_out.loc[:, 'outflow'] = df_out['outflow'].str.replace(',', '')
    df_out.loc[:, 'inflow'] = df_out['inflow'].str.replace(',', '')
    df_out.loc[df_out['outflow'] == '.', 'outflow'] = 0.0
    df_out = df_out.astype({'outflow': float,
                            'inflow': float,
                            'balance': float,
                            })

    df_out['outflow'].fillna(0, inplace=True)
    df_out['inflow'].fillna(0, inplace=True)
    df_out['balance'].fillna(0, inplace=True)

    # remove balance carried forward rows within dataset
    df_temp = df_out.iloc[1:-1, :]
    idx = df_temp.loc[df_temp['payee'].str.contains('(?i)balance'), :].index
    df_out.drop(idx, inplace=True)

    # combine multi-line payees
    for idx, row in df_out.iterrows():
        if ((df_out.loc[idx, 'outflow'] == 0.0)
           and (df_out.loc[idx, 'inflow'] == 0.0)
           and (df_out.loc[idx, 'balance'] == 0.0)):
            df_out.loc[idx+1, 'payee'] = df_out.loc[idx, 'payee'] \
                                         + ' ' \
                                         + df_out.loc[idx+1, 'payee']
        df_out.loc[idx+1, 'date'] = df_out.loc[idx, 'date']

    df_out.drop(df_out[(df_out['outflow'] == 0.0)
                & (df_out['inflow'] == 0.0)
                & (df_out['balance'] == 0.0)].index, inplace=True)
    df_out['date'].fillna(method='ffill', inplace=True)

    return df_out


def get_clean_file_list(tabula_csvs: list, cleaned_path: str):
    """Process all tabula csvs and generate clean csvs

    Keyword arguments:
    :tabula_csvs - list of dicts containing tabula csvs
    :cleaned_path - path where cleaned csvs will be generated

    Returns:
    :cleaned_result - list (paths) of cleaned up csvs
    """
    for file in tabula_csvs:
        original_full_path = file['original_full_path']
        print('Processing file: [{filename}]'
              .format(filename=original_full_path))

        df_in = pd.read_csv(original_full_path, header=None)
        df = clean_tabula_df(df_in)
        file_name = os.path.basename(original_full_path)
        cleaned_df_filename = os.path.splitext(file_name)[0] + '_cleaned.csv'
        cleaned_df_full_path = os.path.join(cleaned_path, cleaned_df_filename)
        file['cleaned_full_path'] = cleaned_df_full_path
        df.to_csv(cleaned_df_full_path, index=False)
        print('Cleaning up complete: [{filename}]'
              .format(filename=cleaned_df_full_path))

    cleaned_result = [os.path.join(dp, f)
                      for dp, dn, filenames in os.walk(cleaned_path)
                      for f in filenames
                      if (os.path.splitext(f)[1] == '.csv')]
    return cleaned_result


# def validate_files(df_param):
#     for file in result:
#         processed_full_path = file['processed_full_path']

#     print('Validating file: [{filename}]'
#           .format(filename=processed_full_path))
#     df_in = pd.read_csv(processed_full_path)
#     opening_balance, closing_balance = validate_df(df_in)

#     file['opening_balance'] = opening_balance
#     file['closing_balance'] = closing_balance

#     # validate transactions, by comparing balances
#     opening_balance = df.loc[df['payee'].str.upper() == \
# 'BALANCE BROUGHT FORWARD', 'balance'].values[0]

#     df = df.loc[(df['payee'].str.upper() != 'BALANCE BROUGHT FORWARD')
#                 & (df['payee'].str.upper() != 'BALANCE CARRIED FORWARD'), :]

#     df_datewise = df.groupby('date').sum(['amount', 'balance'])
#     df_datewise.reset_index(inplace=True)
#     for idx, row in df_datewise.iterrows():
#         if idx <= len(df_datewise.index) - 2:
#             df_datewise.loc[idx+1, 'calculated_balance'] = \
# df_datewise.loc[idx, 'balance'] + df_datewise.loc[idx+1, 'amount']

#     closing_balance = df_datewise.loc[len(df_datewise.index)-1
# , 'calculated_balance']

#     return opening_balance, closing_balance


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT_PATH = sys.argv[1]
        YEAR_PATH = sys.argv[2]
    else:
        ROOT_PATH = '../HSBC/'
        YEAR_PATH = '2021'

    # get folders
    tabula_path,\
        cleaned_path, \
        processed_path, \
        ynab_path, \
        balances_file = get_file_paths(ROOT_PATH, YEAR_PATH)
    print('tabula path: ' + tabula_path)
    
    tabula_list = get_tabula_file_list(tabula_path)
    print(tabula_list)
