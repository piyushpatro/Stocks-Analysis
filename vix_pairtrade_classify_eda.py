# -*- coding: utf-8 -*-
"""VIX-PairTrade-Classify-EDA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NQMgXmCRZ70MPpIxjcWZkloPm1HWsECj
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

df=pd.read_csv('/content/drive/MyDrive/Copy of data.csv', parse_dates=True)
df['date']=pd.to_datetime(df['date'])

# Ranking the stocks using Volatility index of that stock by week

# Function to get the weekly vix of a given stock

def get_weekly_vix(df, stock_name):
    temp_df=df.loc[df['Name']==stock_name]
    temp_df['year']=temp_df['date'].dt.year
    temp_df['week']=temp_df['date'].dt.week
    temp_df.drop('date', inplace=True, axis=1)
    logic={'open':'first', 'high':'max', 'low':'min', 
           'close':'last','volume':'sum'}
    grouped_data=temp_df.groupby(['year', 'week']).agg(logic)
    grouped_data.reset_index(inplace=True)
    grouped_data.drop(index=0, inplace=True)
    year_week=[]
    std=[]
    for i in range(1, len(grouped_data)-1):
        year_week.append(str(grouped_data['year'][i])+'-'+str(grouped_data['week'][i]))
        std.append(np.std([grouped_data['high'][i], grouped_data['high'][i+1]]))
    return stock_name, year_week, np.round(std,2)


vix_list=[]
year_week_list=[]
name_list=[]
for stock_name in np.unique(df['Name']):
    vix_list.append(get_weekly_vix(df, stock_name)[2])   
    year_week_list.append(get_weekly_vix(df, stock_name)[1])
    name_list.append(stock_name)

vix_df=pd.DataFrame(data=vix_list, index=name_list)
vix_df=vix_df.transpose()

sub_1=[]
for i in range(len(vix_df)):
    sub_1.append(vix_df.iloc[i][:].sort_values(ascending=False).index)

sub_1_df=pd.DataFrame(sub_1)
sub_1_df=sub_1_df.transpose()
sub_1_df.columns=year_week_list[0]


# Finding the top 10 pair-trading stocks by year using ADF test

grouped_df = df.groupby(['date', 'Name']).sum()

weekly_df = grouped_df.groupby([pd.Grouper(freq='W', level='date'), 'Name'], sort=True).agg({'open':'first', 'high':'max', 
                                                                                             'low':'min', 'close':'last', 'volume':'sum'})
close_weekly_pivot_df=weekly_df.reset_index(level=1).pivot_table(columns='Name', values='close', index=weekly_df.index.get_level_values(0)).reset_index()

def calc_adf(df, year):
  p=[]
  name=[]
  for column in df.drop('date', axis=1).columns:
    if len(df.loc[df['date'].dt.year==year, column].dropna(axis=0))!=0:
      p.append(adfuller(df.loc[df['date'].dt.year==year, column].dropna(axis=0))[1])
      name.append(column)
  return np.round(p, 3), np.array(name)

p_2013, name_2013 = calc_adf(close_weekly_pivot_df, 2013)
p_2014, name_2014 = calc_adf(close_weekly_pivot_df, 2014)
p_2015, name_2015 = calc_adf(close_weekly_pivot_df, 2015)
p_2016, name_2016 = calc_adf(close_weekly_pivot_df, 2016)
p_2017, name_2017 = calc_adf(close_weekly_pivot_df, 2017)
p_2018, name_2018 = calc_adf(close_weekly_pivot_df, 2018)

df_2013_p=pd.DataFrame([name_2013[np.where(p_2013<=0.05)], p_2013[p_2013<=0.05]], columns=name_2013[np.where(p_2013<=0.05)]).drop(index=0)
df_2014_p=pd.DataFrame([name_2014[np.where(p_2014<=0.05)], p_2014[p_2014<=0.05]], columns=name_2014[np.where(p_2014<=0.05)]).drop(index=0)
df_2015_p=pd.DataFrame([name_2015[np.where(p_2015<=0.05)], p_2015[p_2015<=0.05]], columns=name_2015[np.where(p_2015<=0.05)]).drop(index=0)
df_2016_p=pd.DataFrame([name_2016[np.where(p_2016<=0.05)], p_2016[p_2016<=0.05]], columns=name_2016[np.where(p_2016<=0.05)]).drop(index=0)
df_2013_p=pd.DataFrame([name_2013[np.where(p_2013<=0.05)], p_2013[p_2013<=0.05]], columns=name_2013[np.where(p_2013<=0.05)]).drop(index=0)
df_2017_p=pd.DataFrame([name_2017[np.where(p_2017<=0.05)], p_2017[p_2017<=0.05]], columns=name_2017[np.where(p_2017<=0.05)]).drop(index=0)
df_2018_p=pd.DataFrame([name_2018[np.where(p_2018<=0.05)], p_2018[p_2018<=0.05]], columns=name_2018[np.where(p_2018<=0.05)]).drop(index=0)

df_2013=close_weekly_pivot_df[df_2013_p.columns]
df_2014=close_weekly_pivot_df[df_2014_p.columns]
df_2015=close_weekly_pivot_df[df_2015_p.columns]
df_2016=close_weekly_pivot_df[df_2016_p.columns]
df_2017=close_weekly_pivot_df[df_2017_p.columns]
df_2018=close_weekly_pivot_df[df_2018_p.columns]

def find_cointegrated(df, col1, col2):
    model_1=sm.OLS(df[col2], sm.add_constant(df[col1])).fit()
    pred=model_1.predict(sm.add_constant(df[col1]))
    residuals=pred-df[col2]
    delta=np.diff(residuals, n=1)
    model_2=sm.OLS(delta, sm.add_constant(residuals[0:-1])).fit()
    t=np.round(np.array(model_2.tvalues), 3)
    return {'col1':col1, 'co1':col2, 'intercept':model_1.params[0], 'slope':model_1.params[1], 'std. error':model_1.bse[1] ,'t-value':t[1]}

t_values_2014=[]
for y in df_2014.dropna(axis=1).columns:
  for column in df_2014.drop(y, axis=1).dropna(axis=1).columns:
    t_values_2014.append(find_cointegrated(df_2014, y, column))
t_values_2014 = pd.DataFrame(t_values_2014).sort_values(by='t-value')
t_values_2014['year']=2014

t_values_2015=[]
for y in df_2015.dropna(axis=1).columns:
  for column in df_2015.drop(y, axis=1).dropna(axis=1).columns:
    t_values_2015.append(find_cointegrated(df_2015, y, column))
t_values_2015 = pd.DataFrame(t_values_2015).sort_values(by='t-value')
t_values_2015['year']=2015

t_values_2016=[]
for y in df_2016.dropna(axis=1).columns:
  for column in df_2016.drop(y, axis=1).dropna(axis=1).columns:
    t_values_2016.append(find_cointegrated(df_2016, y, column))
t_values_2016 = pd.DataFrame(t_values_2016).sort_values(by='t-value')
t_values_2016['year']=2016

t_values_2017=[]
for y in df_2017.dropna(axis=1).columns:
  for column in df_2017.drop(y, axis=1).dropna(axis=1).columns:
    t_values_2017.append(find_cointegrated(df_2017, y, column))
t_values_2017 = pd.DataFrame(t_values_2017).sort_values(by='t-value')
t_values_2017['year']=2017

t_values_2018=[]
for y in df_2018.dropna(axis=1).columns:
  for column in df_2018.drop(y, axis=1).dropna(axis=1).columns:
    t_values_2018.append(find_cointegrated(df_2018, y, column))
t_values_2018 = pd.DataFrame(t_values_2018).sort_values(by='t-value')
t_values_2018['year']=2018

sub_2=pd.concat([t_values_2014.head(10), t_values_2015.head(10), t_values_2016.head(10), t_values_2017.head(10), t_values_2018.head(10)], axis=0).reset_index(drop=True)

sub_2

# Predicting red(0), green(1), No confidence(0.5) for the next day of the stock

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score

def Dataset(df, ticker):
  X=df.loc[df['Name']==ticker, :].drop(['Name', 'date'], axis=1)
  targets=[]
  for i in range(1, len(X)):
    if np.array(X['open'])[i] >= np.array(X['close'])[i-1]:
      targets.append(1)
    else:
        targets.append(0)
  return X.iloc[1:,:], np.array(targets)

X, y=Dataset(df, 'AAPL')
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=8, test_size=0.2, stratify=y)

scaler = StandardScaler()
kfolds=StratifiedKFold(n_splits=4)
classifier = RandomForestClassifier()
param_grid={}
scoring_metric='accuracy'

gs_classifier = GridSearchCV(estimator=classifier, param_grid=param_grid, scoring=scoring_metric, n_jobs=-1, cv=kfolds)
pipeline = Pipeline([('scaler', scaler), ('clasifier', gs_classifier)])

pipeline.fit(X_train, y_train)

proba = pipeline.predict_proba(X_test)

pred=[]
for prob in proba[:,0]:
  if prob>=0.75:
    pred.append(gs_classifier.classes_[0])
  elif prob<=0.25:
    pred.append(gs_classifier.classes_[1])
  else:
    pred.append(0.5)
    
sub_3=np.array(pred)

# EDA on any particular stock

import seaborn as sns
import plotly.graph_objects as go
from plotly import subplots

def get_data(df, ticker):
  X=df.loc[df['Name']==ticker, :]
  X.loc[:]['date']=pd.to_datetime(X.loc[:]['date'])
  return X.reset_index(drop=True).set_index('date')

apple = get_data(df, 'AAPL')

fig = subplots.make_subplots(1, 1)
fig.add_traces([go.Line(x=apple.index, y=apple['close'], name='Close'), go.Line(x=apple.index, y=apple['close'].rolling(window=30).mean(), name='30 Days Moving Avg.')])
fig.show()

fig = go.Figure(data=[go.Candlestick(x=apple.index,
                open=apple['open'],
                high=apple['high'],
                low=apple['low'],
                close=apple['close'])])

fig.show()

# As we can see that there is up and down trend from the candlestick graph for a while and the price keeps ranging between the same two values

apple['return']=apple['close'].pct_change()
plt.figure(figsize=(10, 5))
sns.histplot(apple['return'], kde=True)
plt.title('Distribution of Returns in %')
plt.show()

apple['sma'] = apple['close'].rolling(window=30).mean()
apple['sms'] = apple['close'].rolling(window=30).std()

apple['upper'] = apple['sma'] + (apple['sms']*2)
apple['lower'] = apple['sma'] - (apple['sms']*2)

plt.style.use('fivethirtyeight')
fig = plt.figure(figsize=(12,6))
ax = fig.add_subplot(111)

x_axis = apple.index
ax.fill_between(x_axis, apple['upper'], apple['lower'], color='grey')
ax.plot(x_axis, apple['close'], color='blue', lw=2, label='close')
ax.plot(x_axis, apple['sma'], color='black', lw=2, label='SMA')

ax.set_title('Bollinger Band For GOOG')
ax.set_xlabel('Date (Year/Month)')
ax.set_ylabel('Price(USD)')
ax.legend()
plt.show()
