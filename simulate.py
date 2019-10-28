from startup import Startup

# This is the main function that runs the simulation of the startup. It takes in an initialized Startup object, and returns an updated Startup object. The updated Startup object will either have raised a Series A or failed. 
def simulate(startup):

  # Check if either of the end conditions are met. If so, return the startup. Otherwise, move the startup forward in the simulation. 
  while startup.round != 3 or startup.state != 'die':
    startup.advance()

  return startup

  

