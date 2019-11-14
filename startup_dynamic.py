from definitions import FUNDRAISING_MAP, PRE_SEED_VALUE, SEED_VALUE, FUNDING_HISTORY_INITIALIZER, CAP_TABLE_INITIALIZER, STARTUP_STATES
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
    self.state = STARTUP_STATES[0]
    self.age = 0
    self.round = 0
    self.value = self.initialize_value()
    self.amt_raised = 0.0
    self.state_history = [STARTUP_STATES[0]]
    self.value_history = [self.value] # Append at the end of a pitch or grow phase
    self.ownership_history = [1.0] # Append at the end of a pitch or grow phase
    self.amt_raised_history = [0.0] # Append at the end of a pitch or grow phase
    self.cap_table = CAP_TABLE_INITIALIZER.copy()
    self.funding_history = FUNDING_HISTORY_INITIALIZER.copy()
    self.growth_rate = self.initialize_growth_rate()
    self.transition_matrix = {'start': [0,1,0,0,0,0,0,0,0,0], 'grow': [0,0,self.live_transition_prob,self.die_transition_prob,0,0,0,0,0,0], 'live': [0,self.grow_transition_prob,0,0,self.pitch_transition_prob,0,0,0,0,0], 'die': [0,0,0,1,0,0,0,0,0,0], 'pre_seed-success': [0,1,0,0,0,0,0,0,0,0], 'pre_seed-fail': [0,0,self.live_transition_prob,self.die_transition_prob,0,0,0,0,0,0], 'seed-success': [0,1,0,0,0,0,0,0,0,0], 'seed-fail': [0,0,self.live_transition_prob,self.die_transition_prob,0,0,0,0,0,0], 'series_a-success': [0,0,0,0,0,0,0,0,1,0], 'series_a-fail': [0,0,self.live_transition_prob,self.die_transition_prob,0,0,0,0,0,0]} 

  # This function will generate an initial value based on the quality of the startup. 
  def initialize_value(self):
    # UPDATE!!! Should be some normalized random distribution based on quality. 
    return self.quality*5

  # This function will generate a growth rate based on the quality of the startup. 
  def initialize_growth_rate(self):
    # UPDATE!!! Should be some normalized random distribution based on quality. 
    # With this rate, a quality of 60 yields doubling annual growth, assuming 1 period is 1 month
    return (1.0 + self.quality/10)

  def live_transition_prob(self):
    # UPDATE!!! Should be a function based off of the age, value, and perhaps value/age
    return 0.99

  def die_transition_prob(self):
    return 1 - self.live_transition_prob()

  def grow_transition_prob(self):
    #UPDATE!!! Should be a funtion based off of the control preference (and perhaps value/age)
    return self.control_pref

  def pitch_transition_prob(self):
    return 1 - self.grow_transition_prob()

  def grow(self):
    # Update the value based on the current value and growth rate
    self.value = self.value * self.growth_rate
    self.value_history.append(self.value)
    self.ownership_history.append(self.cap_table.at[FUNDRAISING_MAP[0],'pct_owned'])
    self.amt_raised_history.append(self.amt_raised)

  # This function calls the functions get_round() and pitch() to determine what happens in a fundraising event. Based on the output of pitch, it updates the necessary field in the Startup object. 
  def fundraise(self, raise_round):

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
    if self.value < PRE_SEED_VALUE and self.round < 1: # Set the pre_seed_value and the seed_value in DEFINITIONS
      return 1
    elif self.value < SEED_VALUE and self.value > PRE_SEED_VALUE and self.round < 2:
      return 2
    elif self.value > SEED_VALUE and self.round < 3:
      return 3
    else:
      return 4 # This means the startup needs to grow more before trying to raise the next round. 

  """ This function conducts the pitch based on the round and the startup properties. It returns a dataframe containing the following information: 
    success: [0,1]
    raise_round: [1,2,3]
    amt_raised: [0,inf] 
    pre_money: [0,inf]
    post_money: [0, inf]
    pct_sold: [0,1]
  """
  def pitch(self, raise_round):
    
    # Determine how much value to raise
    ### UPDATE!!! For now, set the value to be raised to be 20% of current value. Later, add in noise and figure out how to base this off the round.
    if raise_round == 1:
      pct_sold = np.random.uniform(0.05,0.15)
      post_money = self.value/(1-pct_sold)
      amt_raised = post_money*pct_sold
      pre_money = self.value
    elif raise_round == 2:
      pct_sold = np.random.uniform(0.10,0.20)
      post_money = self.value/(1-pct_sold)
      amt_raised = post_money*pct_sold
      pre_money = self.value
    else:
      pct_sold = np.random.uniform(0.20,0.33)
      post_money = self.value/(1-pct_sold)
      amt_raised = post_money*pct_sold
      pre_money = self.value

    # Determine if the pitch is successful
    ### UPDATE!!! For now, just set the probability to be based off the quality. Later, add in a variable that accounts for the value trying to be raised for the given round type
    if random.random() < self.quality:
      success = 1
    else:
      success = 0

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
      raise Exception('The total ownership should add up to 1. The sum of all ownerhsip percecentages was: {}. The cap table is as follows (Entering Debug Mode): \n {}'.format(ownership_check, self.cap_table))


    # Update the values based on the new post_money
    self.cap_table['value'] = self.cap_table['pct_owned'] * pitch['post_money'].values[0]

  # This function moves the startup from the current state to the next state based on the transisition probabilities. It first calls any functions that are reqruired to be run in the current state. A
  def advance(self):

    if self.state == 'die' or self.state == 'series_a-succeed':
      raise Exception('The advance() function was called on a startup that has already reached end state {}.'.format(self.state))
    if self.state == 'grow':
      self.grow()
      self.age = self.age + 1
      transition_probabilities = self.get_transition_probabilities(self.state)
      new_state = np.random.choice(STARTUP_STATES, replace = True, p = transition_probabilities)
      self.state = new_state
    elif self.state == 'live':
      # Figure out if the startup will pitch or grow
      transition_probabilities = self.get_transition_probabilities(self.state)
      temp_state = np.random.choice(STARTUP_STATES, replace = True, p = transition_probabilities)
      if temp_state != 'grow':
        #Do the pitch and update the state 
        ### UPDATE!!! This needs to handle the new case where the startup is not old enough to be raising again
        # Run the get round function
        raise_round = self.get_fundraising_round()
        if raise_round == 4:
          self.grow()
          self.age = self.age + 1
          transition_probabilities = self.get_transition_probabilities(self.state)
          new_state = np.random.choice(STARTUP_STATES, replace = True, p = transition_probabilities)
          self.state = new_state
        else: 
          pitch = self.fundraise(raise_round)
          new_state = FUNDRAISING_MAP[pitch['round'].values[0]] + '-' + ('success' if pitch['active'].values[0] == 1 else 'fail')
          self.state = new_state
          # Add one to the age since the pitch has actually been completed and a check will be made for the series_a-success end condition
          self.age = self.age + 1
      else:
        # Set the new state to grow. Note: We do not add one to the age here since the age will be updated after grow()
        self.state = temp_state
    else:
      transition_probabilities = self.get_transition_probabilities(self.state)
      new_state = np.random.choice(STARTUP_STATES, replace = True, p = transition_probabilities)
      self.state = new_state

    # Append the current state to the path of the startup
    self.state_history.append(self.state)

  # This is a helper function that retrieves the transition probabilites from the transition matrix, which stores both ints and functions. It calls the functions to generate the transition probabilities based on the current startup properties
  def get_transition_probabilities(self, state):
    
    # Check that the state is valid
    if state not in STARTUP_STATES:
      raise Exception('The state passed in was invalid. The state supplied was: {}'.format(state))

    # Get the values and run any functions
    temp = self.transition_matrix[state]
    probs = [x() if callable(x) else x for x in temp]

    # Check that the probabilities sum to 1
    if not (1.0 - 10**-6 < sum(probs) < 1.0 + 10**-6):
      raise Exception('The probablities for state {} do not sum to 1. The sum was: {}'.format(state, sum(probs)))

    return probs 

  def plot(self):

    fig, host = plt.subplots()

    par1 = host.twinx()

    p1, = host.plot(range(0,self.age + 1), self.value_history, "b-", marker ="o", label="Value")
    p2, = par1.plot(range(0,self.age + 1), [x*100 for x in self.ownership_history],  "r-",  marker ="o", linestyle = "--", label="Founder Ownership %")

    host.set_xlim(0, self.age)
    host.set_ylim(0, self.value+1)
    par1.set_ylim(0, 101)

    host.set_xlabel("Age")
    host.set_ylabel("Value")
    par1.set_ylabel("Founder Ownership %")

    host.yaxis.label.set_color(p1.get_color())
    par1.yaxis.label.set_color(p2.get_color())

    tkw = dict(size=4, width=1.5)
    host.tick_params(axis='y', colors=p1.get_color(), **tkw)
    par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    host.tick_params(axis='x', **tkw)

    lines = [p1, p2]

    host.legend(lines, [l.get_label() for l in lines])
    fig.suptitle('Control Parameter = ' + str(self.control_pref) + ', Quality = ' + str(self.quality) + ', Final State = ' + self.state)

    plt.show()








