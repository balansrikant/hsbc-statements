import pathlib
import os

import main


def test_get_file_paths_with_date():
    pwd = pathlib.Path().resolve()
    root_path = os.path.join(pwd, 'test_data')
    files, balances = main.get_file_paths(root_path, '2020')
    dates = [file['date'] for file in files]
    expected_dates = ['2021-01-25', '2021-02-25']
    assert dates == expected_dates


def test_get_file_paths_without_date():
    pwd = pathlib.Path().resolve()
    root_path = os.path.join(pwd, 'test_data')
    files, balances = main.get_file_paths(root_path, '')
    dates = [file['date'] for file in files]
    expected_dates = ['2021-01-25', '2021-02-25', '2021-03-25', '2021-04-25']
    assert dates == expected_dates
