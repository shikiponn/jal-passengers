import logging
from typing import Optional

import pandas as pd
from patsy import dmatrix
import pymc3 as pm
from tqdm.notebook import tqdm

logger = logging.getLogger(__name__)

def read_data(fpath: str, column_y: str='旅客数（人）') -> pd.DataFrame:
    df = (pd.read_excel(fpath, skiprows=2)[::-1]
             .assign(date=lambda df: pd.to_datetime(df['date']))
             .reset_index(drop=True))
    # import pdb; pdb.set_trace()
    df = df.rename(columns={'旅客数（人）.1': '国内線旅客数（人）'})
    # yのバリエーションを作る
    df['diff'] = df[column_y].diff(1)
    df['pct_change'] = df[column_y].pct_change() + 1
    # 説明変数
    df['month'] = df['date'].astype(str).str.split('-').str[1]
    # その他変数を作成
    df['date'] = pd.to_datetime(df['date'], unit='M')
    # df['num_holiday'] = df['date'].apply(utils.num_holiday_in_month)
    df['yoy_prev'] = df.groupby('month')['pct_change'].pct_change().fillna(0)
    # df['d_num_holiday'] = df['num_holiday'] - 8
    # df['d_num_holiday'] = (df['date'].apply(num_sanren_in_month) - 3).replace({-1: 0})
    df_seasonality = (pd.get_dummies(df['date'].astype(str)
                                               .str.split('-')
                                               .str[1]
                                     , drop_first=True))
    df_seasonality.columns = [f'month_{col}' for col in df_seasonality.columns]
    df = pd.concat([df, df_seasonality], 1)
    return df

def train_test_split(df, test_start_date: str):
    test_start_date = pd.to_datetime(test_start_date)
    df_train = df[df['date'] < test_start_date]
    df_test = df[df['date'] >= test_start_date]
    return df_train, df_test

def get_params(trace: pm.backends.base.MultiTrace) -> pd.DataFrame:
    li = getattr(trace, 'varnames')
    logger.debug(f"varnames in `trace`: {li}")
    dic = {}
    for colname in li[:-2]:
        dic[colname] = trace[colname]

    params = pd.DataFrame(dic)
    logger.debug(f"explanatory variables: {params.columns.tolist()}")
    return params

def struct_test_data(df_test: pd.DataFrame, formula: str) -> pd.DataFrame:
    # Create feature using formula
    dmat_test = dmatrix(formula, df_test)
    colnames = dmat_test.design_info.column_names
    X_test = pd.DataFrame(dmat_test, columns=colnames, index=df_test['date'])
    # Drop intercept because it is constant
    X_test = X_test.drop('Intercept', 1)
    return X_test

def predict_posterior(params, X_test, yoy_prev_latest:Optional[int]=None):
    """
    Predict posterior for each observation
    """
    if yoy_prev_latest:
        logger.info("Adjust prediction using yoy of the latest month in train")

    li = []
    # Predict all observation using each set of param
    for i, row in tqdm(params.iterrows(), total=len(params)):
        res = row['Intercept'] + (X_test * row).sum(1)
        if yoy_prev_latest:
            # Adjust prediction
            res = res * (yoy_prev_latest + 1)
        li.append(res)
    return pd.DataFrame(li, columns=X_test.index)

def transform_to_num_of_passengers(df_train, posterior_sample):
    last_obs =  df_train['旅客数（人）'].iloc[-1]
    dic = {}
    for i, row in posterior_sample.iteritems():
        dic[i] = row * last_obs
        last_obs = dic[i]

    posterior_sample_abs = pd.DataFrame(dic)
    return posterior_sample_abs

