import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox
from rocketpy import Environment, SolidMotor, Rocket, Flight
# motor can be SolidMotor, LiquidMotor, or HybridMotor
from rocketpy import Fluid, CylindricalTank, MassFlowRateBasedTank, HybridMotor

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


if date < today:
    print("Using past data...")
    # Atmospheric Model data import
    env = Environment(
        date=(target_year, target_month, target_day, 12),  # Date
        latitude=39.389700, longitude=-8.288964, elevation=180,  # Location
    )

    filename = "data/weather/data_stream-oper_stepType-instant.nc"

    env.set_atmospheric_model(
        type="Reanalysis", file=filename, dictionary="ECMWF",
    )
else:
    print("Predicting weather data...")
    # Launch site location:
    env = Environment(
        date=(target_year, target_month, target_day, 0),  # Date (Y, M, D, Hr)
        latitude=39.389700, longitude=-8.288964, elevation=180,  # Location
    )
    env.set_atmospheric_model(
        type="Ensemble",
        file="GEFS"
    )
    #Using ensemble and GEFS for Monte Carlo
    #Can use Forecast and GFS instead for a simple analysis

## MOTOR
motor_type = simpledialog.askstring("Motor Type", "Please insert motor type (Hybrid/Solid). Defaults to solid")

if motor_type == "Solid":
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
    motor = Pro75M1670
else:  # Hybrid Motor
    # Define the fluids
    oxidizer_liq = Fluid(name="N2O_l", density=1220)
    oxidizer_gas = Fluid(name="N2O_g", density=1.9277)

    # Define tank geometry
    tank_shape = CylindricalTank(115 / 2000, 0.705)

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
        dry_mass=2,
        dry_inertia=(0.125, 0.125, 0.002),
        nozzle_radius=63.36 / 2000,
        grain_number=4,
        grain_separation=0,
        grain_outer_radius=0.0575,
        grain_initial_inner_radius=0.025,
        grain_initial_height=0.1375,
        grain_density=900,
        grains_center_of_mass_position=0.384,
        center_of_dry_mass_position=0.284,
        nozzle_position=0,
        burn_time=5.2,
        throat_radius=26 / 2000,
    )

    # Add oxidizer tank to Hybrid motor
    example_hybrid.add_tank(
        tank=oxidizer_tank, position=1.0615
    )
    motor = example_hybrid

## ROCKET

# Create rocket object
rocket = Rocket(
    radius=127 / 2000,
    mass=14.426,
    inertia=(6.321, 6.321, 0.034),
    power_off_drag="data/rockets/calisto/powerOffDragCurve.csv",
    power_on_drag="data/rockets/calisto/powerOnDragCurve.csv",
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
)

#Add motor object
rocket.add_motor(motor, position=-1.255)

#Add (optional) rail guides
rail_buttons = rocket.set_rail_buttons(
    upper_button_position=0.0818,
    lower_button_position=-0.6182,
    angular_position=45,
)

#Add aerodynamic components:
nose_cone = rocket.add_nose(
    length=0.55829, kind="von karman", position=1.278
)

# Fins
fin_set = rocket.add_trapezoidal_fins(
    n=4,  #number of fins
    root_chord=0.120,
    tip_chord=0.060,
    span=0.110,
    position=-1.04956,
    cant_angle=0.5,
    airfoil=("data/airfoils/NACA0012-radians.txt", "radians"),
)

#top radius is body radius
tail = rocket.add_tail(
    top_radius=0.0635, bottom_radius=0.0435, length=0.060, position=-1.194656
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
    print("ENSEMBLE STUFF")
    env.select_ensemble_member(2) #selects ensemble 2
    env.info() #prints ensemble 2 info
    env.all_info()
