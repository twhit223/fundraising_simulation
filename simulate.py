from startup import Startup
from wat import wat

# This is the main function that runs the simulation of the startup. It takes in an initialized Startup object, and returns an updated Startup object. The updated Startup object will either have raised a Series A or failed. 
def simulate(startup):

  # Check if either of the end conditions are met. If so, return the startup. Otherwise, move the startup forward in the simulation. 
  while not (startup.state == 'series_a-success' or startup.state == 'die'):
    # wat()
    startup.advance()
    print('The startup is in state {}. It has value {}. The current funding round is {} and it has raised a total of {}'.format(startup.state, startup.value, startup.round, startup.amt_raised))

  return startup

test = Startup(.5,.5)
simulate(test)  

# wat()

