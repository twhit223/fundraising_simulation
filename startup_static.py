from definitions import FUNDRAISING_MAP, FUNDING_HISTORY_INITIALIZER, CAP_TABLE_INITIALIZER, STARTUP_STATES_STATIC
import pandas as pd
import numpy as np
import random
from wat import wat
import matplotlib.pyplot as plt

# Thie Startup class contains the primary object that will be passed through the simulation. It contains all relevant information regarding the startup, and will be updated as the startup progresses through time.
class Startup:
  def __init__(self, control_pref, quality):

    # Check that the supplied parameters are valid
    if control_pref > 1 or control_pref < 0:
      raise Exception('The control preference must be between 0 and 1. The control preference supplied was: {}'.format(control_pref))
    if quality > 1 or quality < 0:
      raise Exception('The quality must be between 0 and 1. The quality supplied was: {}'.format(quality))

    # Assign the initial startup properties
    self.control_pref = control_pref
    self.quality = quality
    self.state = STARTUP_STATES_STATIC[0]
    self.age = 0
    self.round = 0
    self.value = 0
    self.amt_raised = 0.0
    self.state_history = [STARTUP_STATES_STATIC[0]]
    self.value_history = [self.value] # Append at the end of a pitch or grow phase
    self.ownership_history = [1.0] # Append at the end of a pitch or grow phase
    self.amt_raised_history = [0.0] # Append at the end of a pitch or grow phase
    self.cap_table = CAP_TABLE_INITIALIZER.copy()
    self.funding_history = FUNDING_HISTORY_INITIALIZER.copy()

    # UPDATE!!! Consider adding in a quality factor that determines whether the company actually is able to transition to a successful pitch state. 
    self.transition_matrix = {'start': [0, 0.2 - quality/20.0, (1-(0.2 - quality/20.0))*(1 - control_pref), (1-(0.2 - quality/20.0))*control_pref, 0, 0, 0 ], 'die': [0, 1, 0, 0, 0, 0, 0], 'pre_seed': [0, (0.2 - quality/20.0)/2, 0, 0, (1-(0.2 - quality/20.0)/2)*(1 - control_pref), (1-(0.2 - quality/20.0)/2)*control_pref, 0], 'no_pre_seed': [0, 0.2 - quality/20.0, 0, 0, (1-(0.2 - quality/20.0))*(1 - control_pref), (1-(0.2 - quality/20.0))*control_pref, 0], 'seed': [0, (0.2 - quality/20.0)/4, 0, 0, 0, 0, 1 - (0.2 - quality/20.0)/4], 'no_seed': [0, (0.1 - quality/10.0), 0, 0, 0, 0, 1 - (0.1 - quality/10.0)], 'series_a': [0, 0, 0, 0, 0, 0, 1]} 

  # def grow(self):
  #   # Update the value based on the current value and growth rate
  #   self.value = self.value * self.growth_rate
  #   self.value_history.append(self.value)
  #   self.ownership_history.append(self.cap_table.at[FUNDRAISING_MAP[0],'pct_owned'])
  #   self.amt_raised_history.append(self.amt_raised)

  # This function calls the functions get_round() and pitch() to determine what happens in a fundraising event. Based on the output of pitch, it updates the necessary field in the Startup object. 
  def fundraise(self):
    
    # Get the fundraising round
    raise_round = self.get_fundraising_round()

    # Run the pitch function
    pitch = self.pitch(raise_round)

    # Update the startup properties based on the pitch
    self.update_funding(pitch)

    # Update the history of the startup
    self.value_history.append(self.value)
    self.ownership_history.append(self.cap_table.at[FUNDRAISING_MAP[0],'pct_owned'])
    self.amt_raised_history.append(self.amt_raised)

    return pitch

  # This function selects the fundraising round to seek investment for based on the current value. It returns a value corresponding with the proper fundraising round Recall that the fundraising rounds are mapped in the FUNDRAISING_MAP dict.
  def get_fundraising_round(self):
    if self.state == 'start': 
      return 1
    elif self.state == 'pre_seed' or self.state == 'no_pre_seed':
      return 2
    else:
      return 3

  """ This function conducts the pitch based on the round and the startup properties. It returns a dataframe containing the following information: 
    success: [0,1]
    raise_round: [1,2,3]
    amt_raised: [0,inf] 
    pre_money: [0,inf]
    post_money: [0, inf]
    pct_sold: [0,1]
  """
  def pitch(self, raise_round):
    ### UPDATE!!! Add in contingencies for previous raised rounds once this is operational
    if raise_round == 1:
      post_money = 1 + 4 * self.quality
      pct_sold = .05 + .10 * (1 - self.quality)
      amt_raised = post_money * pct_sold
      pre_money = post_money - amt_raised
    elif raise_round == 2:
      if 'pre_seed' in self.state_history:
        post_money = 10 + 10 * self.quality
        pct_sold = .10 + .10 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised
      else:
        post_money = 5 + 10 * self.quality
        pct_sold = .10 + .10 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised
    else:
      if 'pre_seed' and 'seed' in self.state_history:
        post_money = 40 + 40 * self.quality
        pct_sold = .20 + .13 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised
      elif 'pre_seed' in self.state_history and 'no_seed' in self.state_history:
        post_money = 25 + 40 * self.quality
        pct_sold = .20 + .13 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised
      elif 'no_pre_seed' in self.state_history and 'seed' in self.state_history:
        post_money = 35 + 40 * self.quality
        pct_sold = .20 + .13 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised
      else:
        post_money = 20 + 40 * self.quality
        pct_sold = .20 + .13 * (1 - self.quality)
        amt_raised = post_money * pct_sold
        pre_money = post_money - amt_raised        


    # If they transition to this state, then the pitch was successful.
    success = 1

    # Return the result
    key = FUNDRAISING_MAP[raise_round]
    pitch = pd.DataFrame.from_dict({key: [success, raise_round,  pre_money, post_money, amt_raised, pct_sold]}, orient = 'index', columns = ['active','round','pre_money','post_money','amt_raised','pct_sold'])
    return pitch

  # This function udpates the funding_history based on the outcome of the pitch. If that pitch was successful, it makes a call to update_cap_table to update those numbers. 
  def update_funding(self, pitch):

    # Check if the pitch was successful. If it was not, then no need to update. If it was, then update funding_history and cap_table. 
    if pitch['active'].values[0] == 0:
      # self.funding_history.update(pitch) -- Think about whether we want a funding history that is the complete # of fundraising attempts
      return
    else:
      self.funding_history.update(pitch) # This is the built in pandas dataframe update
      self.update_cap_table(pitch)
      self.value = pitch['post_money'].values[0]
      self.round = pitch['round'].values[0]
      self.amt_raised = self.amt_raised + pitch['amt_raised'].values[0]
      return

  # This function uses the successful pitch to calculate updates to the capitalization for each of the parties invested in the startup. It updates the cap_tablepit. 
  def update_cap_table(self, pitch):

    # Update the round of funding that the pitch was successful for
    self.cap_table.loc[pitch.index.values[0], 'active'] = pitch['active'].values[0]
    self.cap_table.loc[pitch.index.values[0], 'pct_owned'] = pitch['pct_sold'].values[0]

    # Update the previous rounds' pct_owned values
    for i in range(0, pitch['round'].values[0]):
      self.cap_table.loc[self.cap_table['round'] == i, 'pct_owned'] = self.cap_table.loc[self.cap_table['round'] == i, 'pct_owned'].values[0] * (1 - pitch['pct_sold'].values[0])

    # Check that the pct_owned adds up to 1
    ownership_check = sum(self.cap_table['pct_owned'])
    if not (1.0 - 10**-6 < ownership_check < 1.0 + 10**-6):
      print("ownership check issue")
      wat()
      raise Exception('The total ownership should add up to 1. The sum of all ownerhsip percecentages was: {}. The cap table is as follows (Entering Debug Mode): \n {}'.format(ownership_check, self.cap_table))


    # Update the values based on the new post_money
    self.cap_table['value'] = self.cap_table['pct_owned'] * pitch['post_money'].values[0]

  # This function moves the startup from the current state to the next state based on the transisition probabilities. It first calls any functions that are reqruired to be run in the current state. A
  def advance(self):

    if self.state == 'die' or self.state == 'series_a':
      raise Exception('The advance() function was called on a startup that has already reached end state {}.'.format(self.state))
    else:
      self.age = self.age + 1
      transition_probabilities = self.get_transition_probabilities(self.state)
      new_state = np.random.choice(STARTUP_STATES_STATIC, replace = True, p = transition_probabilities)

      if new_state == 'pre_seed' or new_state  == 'seed' or new_state == 'series_a':
        self.fundraise()
      else:
        self.value_history.append(self.value)
        self.ownership_history.append(self.cap_table.at[FUNDRAISING_MAP[0],'pct_owned'])
        self.amt_raised_history.append(self.amt_raised)
        
      self.state = new_state
      self.state_history.append(self.state)

  # This is a helper function that retrieves the transition probabilites from the transition matrix, which stores both ints and functions. It calls the functions to generate the transition probabilities based on the current startup properties
  def get_transition_probabilities(self, state):
    
    # Check that the state is valid
    if state not in STARTUP_STATES_STATIC:
      raise Exception('The state passed in was invalid. The state supplied was: {}'.format(state))

    # Get the values and run any functions
    temp = self.transition_matrix[state]
    probs = [x() if callable(x) else x for x in temp]

    # Check that the probabilities sum to 1
    if not (1.0 - 10**-6 < sum(probs) < 1.0 + 10**-6):
      print("Transition probabilities do not sum to 1.")
      wat()
      raise Exception('The probablities for state {} do not sum to 1. The sum was: {}'.format(state, sum(probs)))

    return probs 










