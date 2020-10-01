#%%
import sys
sys.path.append('./jal-passengers')

#%%
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from tqdm.notebook import tqdm

import pymc3 as pm

from hub_airport.passenger.preprocessing import read_data, get_params, struct_test_data, predict_posterior, transform_to_num_of_passengers, train_test_split
from hub_airport.passenger.plot import plot_historical, plot_posterior, plot_traces, plot_posterior_num_of_passengers
from hub_airport.utils.logger import init_root_logger
from hub_airport.utils.util import load_config

#%%
logger = init_root_logger()

#%%
config = load_config('/home/gungelion/workspace/jal-passengers/config.yml')

# %%
# Enable only selected logger
for k, v in logger.Logger.manager.loggerDict.items():
    if k.startswith("hub_airport"):
        print(k)
        v.disabled = False
    else:
        v.disabled = True

# %%
df = read_data(config['FPATH'], config['COLUMN_Y'])
df_train, df_test = train_test_split(df, config['TEST_START_DATE'])

# %%
plot_historical(df_train)

# %%
# Create model
formula = 'pct_change ~ (month_02 + month_03\
                            + month_04 + month_05 + month_06 + month_07 \
                            + month_08 + month_09 + month_10 + month_11 + month_12)'

with pm.Model() as mdl:
    # formula docs
    # https://patsy.readthedocs.io/en/v0.1.0/formulas.html
    pm.glm.GLM.from_formula(formula, df_train)
    trace = pm.sample(5000, tune=1000, init='adapt_diag', cores=2)

# %%
plot_traces(trace)

# %%
params = get_params(trace)
formula_rhs = formula.split(" ~ ")[-1]
X_test = struct_test_data(df_test, formula_rhs)

#%%
posterior_sample = predict_posterior(params, X_test)

# 前月の対前年比で予測値を調整したもの
yoy_prev_latest = df_train['yoy_prev'].iloc[-1]
posterior_sample_with_adjustment = predict_posterior(params, X_test, yoy_prev_latest)

#%% 
plot_posterior(df_test, posterior_sample, "JAL # of passengers prediction")

plot_posterior(df_test, posterior_sample_with_adjustment, "JAL # of passengers prediction with adjustment")

#%%
posterior_abs = transform_to_num_of_passengers(df_train, posterior_sample)
posterior_abs_with_adjustment = transform_to_num_of_passengers(df_train, posterior_sample_with_adjustment)

#%%
plot_posterior_num_of_passengers(df_test, posterior_abs, '予測旅客数')
plot_posterior_num_of_passengers(df_test, posterior_abs_with_adjustment, '予測旅客数（調整後）')