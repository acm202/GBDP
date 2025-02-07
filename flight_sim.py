from rocketpy import Flight
#Import rocket data
from rocket import calisto, env

#Specify environment, rail length, inclination, and heading
test_flight = Flight(
    rocket=calisto, environment=env, rail_length=5.2, inclination=85, heading=0
    )
#This saves all information about the flight.

if __name__ == "__main__":
    test_flight.all_info() #all plots
    test_flight.info() #all prints