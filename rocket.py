import datetime
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight
# motor can be SolidMotor, LiquidMotor, or HybridMotor

# Launch site location:
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
#environment uses the location to gather weather conditions from organisations such as NOAA and ECMWF

# Set the date
tomorrow = datetime.date.today() + datetime.timedelta(days=1)

env.set_date( # must use a tuple of year, month, day, hour
    (tomorrow.year, tomorrow.month, tomorrow.day, 12)
)  # Hour given in UTC time

# Set atmospheric model, using GFS forecasts
env.set_atmospheric_model(type="Forecast", file="GFS")

env.info() # this will let us know what the weather will look like, including plot

# Motor

Pro75M1670 = SolidMotor(
    thrust_source="data/motors/cesaroni/Cesaroni_M1670.eng",
    dry_mass=1.815,
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=33 / 1000,
    grain_number=5,
    grain_density=1815,
    grain_outer_radius=33 / 1000,
    grain_initial_inner_radius=15 / 1000,
    grain_initial_height=120 / 1000,
    grain_separation=5 / 1000,
    grains_center_of_mass_position=0.397,
    center_of_dry_mass_position=0.317,
    nozzle_position=0,
    burn_time=3.9,
    throat_radius=11 / 1000,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)

Pro75M1670.info() # Displays information about the motor, including plot

# Creating a Rocket

# Create rocket object
calisto = Rocket(
    radius=127 / 2000,
    mass=14.426,
    inertia=(6.321, 6.321, 0.034),
    power_off_drag="data/rockets/calisto/powerOffDragCurve.csv",
    power_on_drag="data/rockets/calisto/powerOnDragCurve.csv",
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
)

#Add motor object
calisto.add_motor(Pro75M1670, position=-1.255)

#Add (optional) rail guides
rail_buttons = calisto.set_rail_buttons(
    upper_button_position=0.0818,
    lower_button_position=-0.6182,
    angular_position=45,
)

#Add aerodynamic components:
nose_cone = calisto.add_nose(
    length=0.55829, kind="von karman", position=1.278
)

#4 fins
fin_set = calisto.add_trapezoidal_fins(
    n=4,
    root_chord=0.120,
    tip_chord=0.060,
    span=0.110,
    position=-1.04956,
    cant_angle=0.5,
    airfoil=("data/airfoils/NACA0012-radians.txt","radians"),
)

#top radius is body radius
tail = calisto.add_tail(
    top_radius=0.0635, bottom_radius=0.0435, length=0.060, position=-1.194656
)

#add (optional) parachutes
main = calisto.add_parachute(
    name="main",
    cd_s=10.0,
    trigger=800,      # ejection altitude in meters
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

drogue = calisto.add_parachute(
    name="drogue",
    cd_s=1.0,
    trigger="apogee",  # ejection at apogee
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

#Plot static margin to check stability
calisto.plots.static_margin() #sim will fail if negative, or too high

#Draw rocket
calisto.draw() #this helps check that all components are in right position

## Rocket has been defined, now we run the simulation.
# Going to try to run it in a separate file
# This is so we can define the rocket and ensure everything is correct without
#crashing the simulation, and then run the simulation when ready.