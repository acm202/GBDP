import datetime
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight
#Import rocket data
from rocket import calisto
from rocket import env

#Specify environment, rail length, inclination, and heading
test_flight = Flight(
    rocket=calisto, environment=env, rail_length=5.2, inclination=85, heading=0
    )
#This saves all information about the flight.
# Has prints and plots attributes (test_flight.prints)
# Can also use (test_flight.all_info()) for all the plots, or just info() for numerical results

## All the following can be accessed from test_flight.info():

# Initial conditions
test_flight.prints.initial_conditions()
test_flight.prints.surface_wind_conditions()
test_flight.prints.launch_rail_conditions()

# out of rail state
test_flight.prints.out_of_rail_conditions()

#burnout time
test_flight.prints.burn_out_conditions()

#apogee conditions
test_flight.prints.apogee_conditions()

#Check parachute ejection
test_flight.prints.events_registered()

#Impact
test_flight.prints.impact_conditions()

test_flight.prints.maximum_values()

## Plotting results
# uses the .plots attribute

test_flight.plots.trajectory_3d()
test_flight.plots.linear_kinematics_data()

test_flight.plots.flight_path_angle_data() 
# Flight Path Angle: angle between rocket velocity and horizontal.
# Attitude Angle: rocket axis vs horizontal plane angle (should be close to flight path for a stable rocket)
# Lateral Attitude Angle: rocket axis vs. launch rail plane, deviation from original heading.

## Rocket Orientation or Attitude
test_flight.plots.attitude_data() # Euler parameters (Euler angles or Quaternions)
# Angular Velocity and Acceleration
test_flight.plots.angular_kinematics_data() #expect sudden change at burnout

#Aerodynamic forces
test_flight.plots.aerodynamic_forces() # Lift is decomposed in two directions perpendicular to drag

#Forces applied to rail buttons
test_flight.plots.rail_buttons_forces()

#Energies and power
test_flight.plots.energy_data()

#Fluid mechanics parameters
test_flight.plots.fluid_mechanics_data()

#stability margin and frequency response
test_flight.plots.stability_and_control_data()

## Other things

# Exporting trajectory to Google Earth
test_flight.export_kml(
    file_name="trajectory.kml",
    extrude=True,
    altitude_mode="relative_to_ground",
)

# speed up to time of first parachute deployment (apogee)
test_flight.speed.plot(0, test_flight.apogee_time)

#array of speed of entire flight in form ([time1,speed1],...)
test_flight.speed.source()

## Exporting data as CSV, using the rocketpy.Flight.export_data() method

#exporting rocketpy.Flight.angle_of_attack() and .mach_number()
test_flight.export_data(
    "calisto_flight_data.csv", #file name
    "angle_of_attack", #attribute to export
    "mach_number",
    time_step=1.0, #sets sampling rate, if left empty defaults to every instance of the solver
)

## Saving and storing plots (can be as png, jpg, pdf, and more)

#store rocket drawing
calisto.draw(filename="calisto_drawing.png")
#speed plot
test_flight.speed.plot(filename="speed_plot.jpg")
#trajectory plot
test_flight.plots.trajectory_3d(filename="trajectory_plot.jpg")

## Further Analysis
# Results can be used for Monte Carlo Dispersion Analysis
#importing used utilities
from rocketpy.utilities import apogee_by_mass
from rocketpy.utilities import liftoff_speed_by_mass

#Apogee as a Function of Mass
apogee_by_mass(
    flight=test_flight, min_mass=5, max_mass=20, points=10, plot=True
)

# Out of Rail Speed by Mass
liftoff_speed_by_mass(
    flight=test_flight, min_mass=5, max_mass=20, points=10, plot=True
)


## Dynamic Stability Analysis

# Check how static stability affects dynamic stability 
# Exploring how dynamic stability of this rocket varies if we change fins span

# import helper class
from rocketpy import Function
import copy

# Prepare a copy of the rocket
calisto2 = copy.deepcopy(calisto)

# Prepare Environment Class
custom_env = Environment()
custom_env.set_atmospheric_model(type="custom_atmosphere", wind_v=-5)

# Simulate Different Static Margins by Varying Fin Position
simulation_results = []

for factor in [-0.5, -0.2, 0.1, 0.4, 0.7]:
    # Modify rocket fin set by removing previous one and adding new one
    calisto2.aerodynamic_surfaces.pop(-1)

    fin_set = calisto2.add_trapezoidal_fins(
        n=4,
        root_chord=0.120,
        tip_chord=0.040,
        span=0.100,
        position=-1.04956 * factor,
    )
    # Simulate
    test_flight = Flight(
        rocket=calisto2,
        environment=custom_env,
        rail_length=5.2,
        inclination=90,
        heading=0,
        max_time_step=0.01,
        max_time=5,
        terminate_on_apogee=True,
        verbose=False,
    )
    # Store Results
    static_margin_at_ignition = calisto2.static_margin(0) #indexed by time
    static_margin_at_out_of_rail = calisto2.static_margin(test_flight.out_of_rail_time)
    static_margin_at_steady_state = calisto2.static_margin(test_flight.t_final)
    simulation_results += [
        (
            test_flight.attitude_angle, #first element of tuple
            "{:1.2f} c | {:1.2f} c | {:1.2f} c".format( #second element of tuple - formatted string
                static_margin_at_ignition, #unique value found above
                static_margin_at_out_of_rail, #unique value found above
                static_margin_at_steady_state, #unique value found above
            ),
        )
    ]
    #explaining the above:
    # contained within "" is a formatted string, gathering information from the arguments of the .format() function
    # 1.2f means float with 2 decimal places

Function.compare_plots(
    simulation_results,
    lower=0,
    upper=1.5,
    xlabel="Time (s)",
    ylabel="Attitude Angle (deg)",
)