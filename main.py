import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def createFigure(df):
    plt.figure(figsize=(12, 10))
    plt.subplot(3,1,1)
    plt.title('Deaths')
    plt.plot(df['Deaths'])
    plt.subplot(3, 1, 2)
    plt.title('Recovered')
    plt.plot(df['Recovered'])
    plt.subplot(3, 1, 3)
    plt.title('New cases')
    plt.plot(df['New cases'])
    plt.show()

def get_data_frame():
    path = '../../Downloads/day_wise.csv'
    df = pd.read_csv(path)
    df = df[['Date', 'Deaths', 'Recovered', 'New cases']]
    df['Date'] = pd.to_datetime(df['Date'])

    return df

def main():
    df = get_data_frame()
    createFigure(df)
    figure_with_dates(df, ['2020-01-22'])

def figure_with_dates(df, data):
    data = pd.to_datetime(data)
    df2 = df[df['Date'].isin(data)]
    createFigure(df2)

main()

