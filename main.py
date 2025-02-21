import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load dataset (assuming it's a CSV with columns: 'Active', 'Recovered', 'Deaths')
df = pd.read_csv('day_wise.csv')

# Initial conditions
S0 = 17000000
I0 = df.at[0, 'Active']
print(I0)
R0 = df.at[0, 'Recovered']
D0 = df.at[0, 'Deaths']
N = S0 + I0 + R0 + D0

# Time steps
days = len(df)
S, I, R, D = np.zeros(days), np.zeros(days), np.zeros(days), np.zeros(days)
S[0], I[0], R[0], D[0] = S0, I0, R0, D0

# Function to update parameters dynamically
def update_parameters(day):
    if day > 1:
        new_recoveries = df['Recovered'].iloc[day] - df['Recovered'].iloc[day - 1]
        new_deaths = df['Deaths'].iloc[day] - df['Deaths'].iloc[day - 1]

        gamma = new_recoveries / I[day - 1] if I[day - 1] > 0 else 0
        mu = new_deaths / I[day - 1] if I[day - 1] > 0 else 0
        beta = (df['Active'].iloc[day] - df['Active'].iloc[day - 1] + mu * I[day - 1] + gamma * I[day - 1]) / (S[day - 1] * I[day - 1] / N) if S[day - 1] * I[day - 1] > 0 else 0
    else:
        beta, gamma, mu = 0, 0, 0
    return beta, gamma, mu

# Simulate the SIRD model
for t in range(1, days):
    beta, gamma, mu = update_parameters(t)
    alpha = 1/180  # Susceptibility rate (180 days immunity)
    dS = alpha * R[t-1] - beta * S[t-1] * I[t-1] / N
    dI = beta * S[t-1] * I[t-1] / N - mu * I[t-1] - gamma * I[t-1]
    dR = gamma * I[t-1] - alpha * R[t-1]
    dD = mu * I[t-1]
    
    S[t] = S[t-1] + dS
    I[t] = I[t-1] + dI
    R[t] = R[t-1] + dR
    D[t] = D[t-1] + dD

# Compute R0 (basic reproduction number)
R0_values = [update_parameters(t)[0] / update_parameters(t)[1] if update_parameters(t)[1] > 0 else 0 for t in range(1, days)]
average_R0 = sum(R0_values) / len(R0_values) 
print(f'Average R0: {average_R0:.2f}')


# Plot results
plt.figure(figsize=(12, 6))
plt.plot(S, label='Susceptible', color='blue')
plt.plot(I, label='Infected', color='red')
plt.plot(R, label='Recovered', color='green')
plt.plot(D, label='Deceased', color='black')
plt.xlabel('Days')
plt.ylabel('Population')
plt.title('SIRD Model Over Time')
plt.legend()
plt.show()

# Plot R0
plt.figure(figsize=(10, 5))
plt.plot(R0_values, label='$R_0$', color='purple')
plt.xlabel('Days')
plt.ylabel('Basic Reproduction Number ($R_0$)')
plt.legend()
plt.title('Estimated $R_0$ Over Time')
plt.show()


# hey! 

#Trial Syb


