#Simulates everything for the Hybrid Rocket

import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox
from rocketpy import Environment, SolidMotor, Rocket, Flight
# motor can be SolidMotor, LiquidMotor, or HybridMotor
from rocketpy import Fluid, CylindricalTank, MassFlowRateBasedTank, HybridMotor, MassBasedTank

# necessary methods for a Hybrid Motor

# Create a hidden root window (for user inputs)
root = tk.Tk()
root.withdraw()

target_year = simpledialog.askinteger("Input", "Enter year:")
target_month = simpledialog.askinteger("Input", "Enter month:")
target_day = simpledialog.askinteger("Input", "Enter day:")

today = datetime.today()
date = datetime(target_year, target_month, target_day, hour=12)

## ENVIRONMENT

# Location has been set to the location from last years

if date < today:
    print("Using past data...")
    # Atmospheric Model data import
    env = Environment(
        date=(target_year, target_month, target_day, 12),  # Date
        latitude=39.389700, longitude=-8.288964, elevation=123.9,  # Location
    )

    filename = "../data/weather/data_stream-oper_stepType-instant.nc"

    env.set_atmospheric_model(
        type="Reanalysis", file=filename, dictionary="ECMWF",
    )
else:
    print("Predicting weather data...")
    # Launch site location:
    env = Environment(
        date=(target_year, target_month, target_day, 0),  # Date (Y, M, D, Hr)
        latitude=39.389700, longitude=-8.288964, elevation=123.9,  # Location
    )
    env.set_atmospheric_model(
        type="ensemble",
        file="GEFS"
    )
    #Using ensemble and GEFS for Monte Carlo
    #Can use Forecast and GFS instead for a simple analysis

## MOTOR
motor_type = simpledialog.askstring("Motor Type", "Please insert motor type (Hybrid/Solid). Defaults to solid")

if motor_type == "Solid":
    Pro75M1670 = SolidMotor(
        thrust_source="../data/motors/cesaroni/Cesaroni_M1670.eng",
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
    motor = Pro75M1670
else:  # Hybrid Motor
    # Define the fluids
    oxidizer_liq = Fluid(name="N2O_l", density=828.2592)
    oxidizer_gas = Fluid(name="N2O_g", density=131.7148)

    # Define tank geometry
    tank_shape = CylindricalTank(0.074, 0.591)

    # Define tank
    oxidizer_tank = MassFlowRateBasedTank(
       name="oxidizer tank",
       geometry=tank_shape,
       flux_time=5.2,
       initial_liquid_mass=4.11,
       initial_gas_mass=0,
       liquid_mass_flow_rate_in=0,
       liquid_mass_flow_rate_out=(4.11 - 0.5) / 5.2,
       gas_mass_flow_rate_in=0,
       gas_mass_flow_rate_out=0,
       liquid=oxidizer_liq,
       gas=oxidizer_gas,
     )

    example_hybrid = HybridMotor(
        thrust_source=lambda t: 2000 - (2000 - 1400) / 5.2 * t,
        #Thrust source can be any function, constant, or CSV/eng file
        dry_mass=3.11,
        dry_inertia=(0.125, 0.125, 0.002),
        nozzle_radius=0.014,
        grain_number=1,
        grain_separation=0,
        grain_outer_radius=0.038,
        grain_initial_inner_radius=0.0211354,
        grain_initial_height=0.2531922,
        grain_density=920,
        grains_center_of_mass_position=0.28427,
        center_of_dry_mass_position=0.28427,
        nozzle_position=0,
        burn_time=7.43,
        throat_radius=0.012,
    )

    # Add oxidizer tank to Hybrid motor
    example_hybrid.add_tank(
        tank=oxidizer_tank, position=1.11305
    )
    motor = example_hybrid

## ROCKET

# Create rocket object
rocket = Rocket(
    radius=0.0805,
    mass=25.025,
    inertia=(16.33, 16.33, 0.099),
    power_off_drag="../data/rockets/calisto/powerOffDragCurve.csv",
    power_on_drag="../data/rockets/calisto/powerOnDragCurve.csv",
    center_of_mass_without_motor=1.23903,
    coordinate_system_orientation="tail_to_nose",
)

#Add motor object
rocket.add_motor(motor, position=0.0736)

#Add (optional) rail guides
rail_buttons = rocket.set_rail_buttons(
    upper_button_position=0.1818,
    lower_button_position=0.8182,
    angular_position=45,
)

#Add aerodynamic components:
nose_cone = rocket.add_nose(
    length=0.5528, kind="parabolic", position=2.99
)

# Fins
fin_set = rocket.add_trapezoidal_fins(
    n=3,  #number of fins
    root_chord=0.302,
    tip_chord=0.13,
    span=0.202,
    position=0.3756,
    cant_angle=0,
    #airfoil=("../data/airfoils/NACA0012-radians.txt", "radians"), # Removed to simulate last years
)

#top radius is body radius
tail = rocket.add_tail(
    top_radius=0.0805, bottom_radius=0.058, length=0.0736, position=0
)

#add (optional) parachutes
main = rocket.add_parachute(  #Main parachute
    name="main",
    cd_s=10.0,
    trigger=800,  # ejection altitude in meters
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

drogue = rocket.add_parachute(  #Drogue parachute
    name="drogue",
    cd_s=1.0,
    trigger="apogee",  # ejection at apogee
    sampling_rate=105,
    lag=1.5,
    noise=(0, 8.3, 0.5),
)

# Payload related information
Payload = Rocket(
    radius=127 / 2000,
    mass=1,
    inertia=(0.1, 0.1, 0.001),
    power_off_drag=0.5,
    power_on_drag=0.5,
    center_of_mass_without_motor=0,
)

Payload_main = Payload.add_parachute(
    name="Main",
    cd_s = 2.2*0.1379511112,
    trigger= "apogee",  # ejection altitude in meters
)

fly = messagebox.askyesno("Flight?", "Run flight simulation?")

if fly:
    test_flight = Flight(
        rocket=rocket, environment=env, rail_length=5.2, inclination=85, heading=0
    )
    # This saves all information about the flight.

    if __name__ == "__main__":
        test_flight.all_info()  # all plots
        test_flight.info()  # all prints

## PLOTS
if __name__ == "__main__":  # Don't show if another script is calling this
    print("ENV INFO")
    env.info()  # Environment info
    env.all_info()  # Environment-related plots
    print("MOTOR INFO")
    motor.info()  # Motor info
    motor.all_info()  # Motor-related plots

    rocket.plots.static_margin()  #Plot static margin to check stability
    #sim will fail if negative, or too high

    rocket.draw()  # Draw rocket
    #this helps check that all components are in right position
    #print("ENSEMBLE STUFF")
    #env.select_ensemble_member(2) #selects ensemble 2
    #env.info() #prints ensemble 2 info
    #env.all_info()
