from definitions import FUNDRAISING_MAP, PRE_SEED_VALUE, SEED_VALUE, FUNDING_HISTORY_INITIALIZER, CAP_TABLE_INITIALIZER
import pandas as pd

# Thie Startup class contains the primary object that will be passed through the simulation. It contains all relevant information regarding the startup, and will be updated as the startup progresses through time.
class Startup:
  def __init__(self, control_pref, quality):
    self.control_pref = control_pref
    self.quality = quality
    self.age = 0
    self.value = 0  # UPDATE!!!. Should be some normalized random distribution based on quality. 
    self.amt_raised = 0.0
    self.round = 0
    self.cap_table = CAP_TABLE_INITIALIZER
    self.funding_history = FUNDING_HISTORY_INITIALIZER
    self.growth_rate = 0.0 # UPDATE!!!. Should be some function of quality. 

  def grow(self):
    # Update the value based on the current value and growth rate
    self.value = self.value ** (1 + self.growth_rate)

  # This function calls the functions get_round() and pitch() to determine what happens in a fundraising event. Based on the output of pitch, it updates the necessary field in the Startup object. 
  def fundraise(self):
    # Run the get round function
    raise_round = self.get_fundraising_round()

    # Run the pitch function
    pitch = self.pitch(raise_round)

    # Update the startup properties based on the pitch
    self.update_funding(pitch)

  # This function selects the fundraising round to seek investment for based on the current value. It returns a value corresponding with the proper fundraising round Recall that the fundraising rounds are mapped in the FUNDRAISING_MAP dict.
  def get_fundraising_round(self):
    if self.value < PRE_SEED_VALUE: # Set the pre_seed_value and the seed_value in DEFINITIONS
      return 1
    elif self.value < SEED_VALUE:
      return 2
    else
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
    
    amt_raised = 0
    pre_money = 0
    post_money = 0
    pct_sold = 0

    # Do something to determine if the pitch is successful
    ### UPDATE!!!

    # If the pitch is successful, determine how much is raised and at what value
    ### UPDATE!!!

    # Return the result
    pitch = pd.DataFrame.from_dict({FUNDRAISING_MAP[raise_round]: [success, raise_round,  pre_money, post_money, amt_raised, pct_sold]}, orient = 'index', columns = ['active','round','pre_money','post_money','amt_raised','pct_sold'])
    return pitch

  # This function udpates the funding_history based on the outcome of the pitch. If that pitch was successful, it makes a call to update_cap_table to update those numbers. 
  def update_funding(self, pitch):

    # Check if the pitch was successful. If it was not, then no need to update. If it was, then update funding_history and cap_table. 
    if pitch['active'] == 0:
      return
    else:
      self.funding_history.update(pitch) # This is the built in pandas dataframe update
      self.update_cap_table(pitch)
      self.value = pitch['post_money'].values[0]
      self.round = pitch['round'].values[0]
      self.amt_raised = self.amt_raised + pitch['amt_raised'].values[0]
      return

  # This function uses the successful pitch to calculate updates to the capitalization for each of the parties invested in the startup. It updates the cap_table table. 
  def update_cap_table(self, pitch):

    # Update the round of funding that the pitch was successful for
    self.cap_table.loc[pitch.index.values[0], 'active'] = pitch['active'].values[0]
    self.cap_table.loc[pitch.index.values[0], 'pct_owned'] = pitch['pct_sold'].values[0]

    # Update the previous rounds' pct_owned values
    for i in range(0, pitch['round'].values[0]):
      self.cap_table.loc[self.cap_table['round'] == i, 'pct_owned'] = self.cap_table.loc[self.cap_table['round'] == i, 'pct_owned'].values[0] * (1 - pitch['pct_sold'].values[0])

    # Check that the pct_owned adds up to 1
    ownership_check = sum(self.cap_table['pct_owned'])
    if ownership_check != 1.0:
      raise Exception('The total ownership should add up to 1. The sum of all ownerhsip percecentages was: {}. The cap table is as follows: \n {}'.format(ownership_check, self.cap_table))

    # Update the values based on the new post_money
    self.cap_table['value'] = self.cap_table['pct_owned'] * pitch['post_money'].values[0]

    
      






