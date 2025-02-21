import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def create_figure(df):
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

def get_data_frame():
    path = '../../Downloads/day_wise.csv'
    df = pd.read_csv(path)
    df = df[['Date', 'Deaths', 'Recovered', 'New cases']]
    df['Date'] = pd.to_datetime(df['Date'])

    return df

def get_data_frame_sir():
    path = '../../Downloads/day_wise.csv'
    df = pd.read_csv(path)
    df = df[['Date', 'Deaths', 'Recovered', 'Active', 'New cases']]
    df['Date'] = pd.to_datetime(df['Date'])

    return df

def main1():
    df = get_data_frame()
    create_figure(df)
    figure_with_dates(df, ['2020-01-22'])

def figure_with_dates(df, data):
    data = pd.to_datetime(data)
    df2 = df[df['Date'].isin(data)]
    create_figure(df2)

def create_figure_sir(S, I, R, D):
    plt.figure(figsize=(12,6))
    plt.plot(S, label = 'Susceptible', color = 'blue')
    plt.plot(I, label = 'Infected', color = 'red')
    plt.plot(R, label = 'Recovered', color = 'green')
    plt.plot(D, label = 'Deceased', color = 'black')
    plt.xlabel('Days')
    plt.ylabel('Population')
    plt.legend()
    plt.title('Estimated $R_0$ Over Time')

def load_sir():
    df = get_data_frame_sir()
    S = []
    I = []
    R = []
    D = []

    # Parameters
    beta = 0.3  # infection rate
    gamma = 0.1  # recovery rate
    mu = 0.05  # mortality rate
    alpha = 0.0005 # 
    S0 = 17000000  # initial susceptible population
    I0 = df['Active'].iloc[0]   # initial infected population
    R0 = df['Recovered'].iloc[0]    # initial recovered population
    D0 = df['Deaths'].iloc[0]   # initial deceased population
    N = S0 + I0 + R0 + D0  # total population

    # Saving first entries to list
    S.append(S0)
    I.append(I0)
    R.append(R0)
    D.append(D0)

    # Solving equations
    i = 0
    for index in df.iterrows():
        delta_S = alpha*R[i] - beta*S[i]*I[i]/N
        S.append(S[i] + delta_S)
        delta_I = beta*S[i]*I[i]/N - mu*I[i] - gamma*I[i]
        I.append(I[i] + delta_I)
        delta_R = gamma*I[i] - alpha*R[i]
        R.append(R[i] + delta_R)
        delta_D = mu*I[i]
        D.append(D[i] + delta_D)
        i += 1

    # Plot results
    create_figure_sir(S,I,R,D)

main1()
load_sir() 
plt.show()



