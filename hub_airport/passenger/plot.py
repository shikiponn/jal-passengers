import logging

import japanize_matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import pymc3 as pm

logger = logging.getLogger(__name__)

def plot_historical(df):
    fig = px.line(df, x="date", y="旅客数（人）", title='Actual', render_mode="svg")
    fig.show()
    fig = px.line(df, x="date", y="pct_change", title='増加率（前月比）', render_mode="svg")
    fig.show()
    return

def plot_traces(traces, retain=0):
    '''
    TODO: plotしているものの意味を確認する
    Convenience function:
    Plot traces with overlaid means and values
    '''

    ax = pm.traceplot(traces[-retain:],
                      lines=tuple([(k, {}, v['mean'])
                                   for k, v in pm.summary(traces[-retain:]).iterrows()]))

    for i, mn in enumerate(pm.summary(traces[-retain:])['mean']):
        ax[i,0].annotate('{:.3f}'.format(mn), xy=(mn,0), xycoords='data'
                    ,xytext=(5,10), textcoords='offset points', rotation=90
                    ,va='bottom', fontsize='large', color='#AA0022')

def plot_posterior(df_test, posterior_sample, title: str):
    fig, ax = plt.subplots(1, figsize=(15, 5))
    index_date = df_test['date'].astype(str).str.rsplit('-', 1).str[0]
    # plot mean of the prediction
    ax.plot(index_date, posterior_sample.mean().tolist(), lw=2, label='mean pred', color='blue')
    ax.fill_between(index_date, posterior_sample.quantile(q=0.25), posterior_sample.quantile(q=0.75), facecolor='blue', alpha=0.5)
    ax.fill_between(index_date, posterior_sample.quantile(q=0.05), posterior_sample.quantile(q=0.95), facecolor='blue', alpha=0.25)
    # plot actual
    ax.plot(index_date, df_test['pct_change'].tolist(), lw=2, label='true', color='orange')

    ax.set_title(title)
    plt.legend()
    plt.show()
    return


def plot_posterior_num_of_passengers(df_test, posterior_sample_abs, title):
    fig, ax = plt.subplots(1, figsize=(15, 5))
    index_date = df_test['date'].astype(str).str.rsplit('-', 1).str[0]
    ax.plot(index_date, posterior_sample_abs.mean().tolist(), lw=2, label='mean pred', color='blue')
    ax.fill_between(index_date, posterior_sample_abs.quantile(q=0.25),
                    posterior_sample_abs.quantile(q=0.75), facecolor='blue', alpha=0.25)
    ax.fill_between(index_date, posterior_sample_abs.quantile(q=0.05),
                    posterior_sample_abs.quantile(q=0.95), facecolor='blue', alpha=0.05)

    # plot true
    ax.plot(index_date, df_test['旅客数（人）'].tolist(), lw=2, label='true', color='orange')

    ax.legend(loc='upper left')
    ax.set_xlabel('Dates')
    ax.set_ylabel('旅客数（人）')
    ax.set_title(title)
    return ax