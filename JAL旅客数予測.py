#%%

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from tqdm.notebook import tqdm

import pymc3 as pm
import statsmodels.api as sm

from hub_airport.passenger.preprocessing import read_data
FPATH = '/home/gungelion/workspace/jal-passengers/JAL旅客数.xlsx'

#%%
df = read_data(FPATH)
df_train, df_test = df.loc[:44], df.loc[45:]
df_train

#%%
df_test
#%%

# プロット
fig = px.line(df_train, x="date", y="旅客数（人）",  title='Actual', render_mode="svg")
fig.show()