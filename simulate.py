from startup import Startup
from definitions import STARTUP_STATES
from statistics import mean, stdev
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wat import wat


# This is the main function that runs the simulation of the startup. It takes in an initialized Startup object and performs various operations on it as specified by the model. The updated Startup object will either have raised a Series A or failed. 
def simulate(startup):
  
  # Check if either of the end conditions are met. If so, return the startup. Otherwise, move the startup forward in the simulation. 
  # print('The startup was initialized with control pref {} and quality {}. The initial value is {}. The initial round is {}. The funding history is below. {}'.format(startup.control_pref, startup.quality, startup.value, startup.round, startup.funding_history))
  while not (startup.state == 'series_a-success' or startup.state == 'die'):
    # wat()
    startup.advance()
    # print('The startup is in state {}. It has value {}. The current funding round is {} and it has raised a total of {}'.format(startup.state, startup.value, startup.round, startup.amt_raised))

  # print('The startup finished in state {}. It has value {}, and it has raised a total of {}. The funding history is below. {}'.format(startup.state, startup.value, startup.amt_raised, startup.funding_history))

  
  return startup


# This function creates a matrix of startups and simulates them. For each value of control_preference and quality (as specified by increment), the matrix contains a list of simulated startups (as specified by number_of_startups). It then returns the matrix of simulated startups. 
def initialize_startup_matrix(increment, number_of_startups):
  print("Initializing the startup matrix...")
  # Check that an integer mutliple of the increment equals 1.0 


  # Create the startup matrix as a list of list of lists. 
  data = []
  for quality in np.arange(0.0, 1.0+increment, increment):
    row = []
    for control_preference in np.arange(0.0, 1.0+increment, increment):
      cell = []
      for k in range(number_of_startups):
        cell.append(Startup(control_preference, quality))
      row.append(cell)
    data.append(row)

  print("Simulating startups...")
  # Simulate the startups in the list
  [[[simulate(s) for s in column] for column in row] for row in data]
  print("Startups simulated!")

  return data

# This function performs an analysis of the startups that have been simulated and returns a matrix containing a list of tuples for each combination of quality and control preference. The list is structured as follows: [(avg. value, 10th percentile, 90th percentile), (avg. ownership %, 10th percentile, 90th percentile), (avg. time to series A, 10th percentile, 90th percentile), % survived to series a]
def simulation_analysis(startup_matrix):

  analysis = []

  for i in range(0, len(startup_matrix)):
    row = []
    
    for j in range(0, len(startup_matrix[i])):
      cell =[]
      
      # For a certain quality and control pref, get all of the startups that were simulated
      startups = startup_matrix[i][j]

      # For those startups, calculate the following
      value = [s.value if s.state == STARTUP_STATES[8] else 0 for s in startups]
      ownership = [s.ownership_history[-1] for s in startups]
      time = [s.age for s in startups]
      survival = [1 if s.state == STARTUP_STATES[8] else 0 for s in startups]

      # Create a tuple based on the lists 
      avg_value = (mean(value), stdev(value))
      avg_ownership = (mean(ownership), stdev(ownership))
      avg_time = (mean(time), stdev(time))
      survival_pct = mean(survival)

      # Append the results to the cell
      cell.append(avg_value)
      cell.append(avg_ownership)
      cell.append(avg_time)
      cell.append(survival_pct)

      row.append(cell)
    
    analysis.append(row)
  
  return analysis


def plot_analysis(increment, analysis):

  fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)

  x = np.arange(0.0 ,1.0 + increment, increment)

  # Get the values and the stdev
  # The first row of the analysis is quality = 0


  # Plot the Value vs. Control Pref
  ax = axes[0,0]
  # For each level of quality, get the series to plot
  for i in range(0, len(x)):
    row = analysis[i]
    values = [data[0][0] for data in row]
    stdevs = [data[0][1] for data in row]
    ax.errorbar(x = x, y = values, yerr = None, label = "{0:.1f}".format(x[i]))
  ax.legend(title = 'Quality', loc='upper left', ncol=1)
  ax.set_title('Avg. Value vs. Control Preference')

  # Plot the Ownership vs. Control Pref
  ax = axes[0,1]
  # For each level of quality, get the series to plot
  for i in range(0, len(x)):
    row = analysis[i]
    values = [data[1][0] for data in row]
    stdevs = [data[1][1] for data in row]
    ax.errorbar(x = x, y = values, yerr = None, label = "{0:.1f}".format(x[i]))
  ax.legend(title = 'Quality', loc='upper left', ncol=1)
  ax.set_title('Avg. Ownership % vs. Control Preference')

  # Plot the Time to Series A vs. Control Pref
  ax = axes[1,0]
  # For each level of quality, get the series to plot
  for i in range(0, len(x)):
    row = analysis[i]
    values = [data[2][0] for data in row]
    stdevs = [data[2][1] for data in row]
    ax.errorbar(x = x, y = values, yerr = None, label = "{0:.1f}".format(x[i]))
  ax.legend(title = 'Quality', loc='upper left', ncol=1)
  ax.set_title('Avg. Age vs. Control Preference')

  # Plot the Probability of Survival to Series A vs. Control Pref
  ax = axes[1,1]
  # For each level of quality, get the series to plot
  for i in range(0, len(x)):
    row = analysis[i]
    values = [data[3] for data in row]
    ax.errorbar(x = x, y = values, yerr = None, label = "{0:.1f}".format(x[i]))
  ax.legend(title = 'Quality', loc='upper left', ncol=1)
  ax.set_title('P(Survival to Series A) vs. Control Preference')

  plt.show()

  wat()

  


  # Split the data up between the four plots we want: value, ownership, time, and prob survival



""" How do we conduct actual analysis:


--> The output I want from a simulation is a dataframe with control preference on one axes, quality on the other, and at each cell a list that contains N startups that have been simulated with those parameters. 
--> From this output, I will calculate the following: avg. value, avg. control, avg. time to series age, and probability of reaching series a (all with variances except the probability). This should be inserted into a dataframe with the same structure as the output from the simulation
--> Once I have these calculations, the idea will be to plot the following:
1.) X-axis: Control Preference, Y-axis: Avg. Value + error bars, plot a line for each level of quality (e.g. quality = 0.2, quality = 0.4, etc.)
2.) X-axis: Control Preference, Y-axis: Avg. Control + error bars, plot a line for each level of quality (e.g. quality = 0.2, quality = 0.4, etc.)
3.) X-axis: Control Preference, Y-axis: Avg. Time to Series A + error bars, plot a line for each level of quality (e.g. quality = 0.2, quality = 0.4, etc.).
4.) X-axis: Control Preference, Y-axis: Probability of successfully raising series A, plot a line for each level of quality (e.g. quality = 0.2, quality = 0.4, etc.).



--> To get to the final output, I need to have a dataframe with

"""
increment = 0.2
startup_matrix = initialize_startup_matrix(increment, 20)

analysis = simulation_analysis(startup_matrix)

plot_analysis(increment, analysis)





wat()


test = Startup(0.8,0.6)
simulate(test)  
test.plot()

# wat()





