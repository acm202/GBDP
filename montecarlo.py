import tkinter as tk
from tkinter import simpledialog
from rocketpy import MonteCarlo
from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticSolidMotor,
    StochasticRocket,
    StochasticFlight,
    StochasticNoseCone,
    StochasticTail,
    StochasticTrapezoidalFins,
    StochasticParachute,
    StochasticRailButtons,
)
from sim import rocket, env, motor, nose_cone, fin_set, rail_buttons, tail, main, drogue, test_flight

# Create a hidden root window (for user inputs)
root = tk.Tk()
root.withdraw()

## Set Stochastic Environment
stochastic_env = StochasticEnvironment(
    environment=env,
    ensemble_member=list(range(env.num_ensemble_members)),
    elevation=20,
)

## Set Stochastic Motor
stochastic_motor = StochasticSolidMotor(
    solid_motor=motor,
    burn_start_time=(0, 0.1, "binomial"), # binomial uncertainty (mean, deviation, type)
    grains_center_of_mass_position=0.001, # linear uncertainties
    grain_density=50,
    grain_separation=1 / 1000,
    grain_initial_height=1 / 1000,
    grain_initial_inner_radius=0.375 / 1000,
    grain_outer_radius=0.375 / 1000,
    total_impulse=(6500, 1000), # normally distributed uncertainty (mean, deviation)
    throat_radius=0.5 / 1000,
    nozzle_radius=0.5 / 1000,
    nozzle_position=0.001,
)

## Set Stochastic Rocket
stochastic_rocket = StochasticRocket(
    rocket=rocket,
    radius=0.0127 / 2000,
    mass=(15.426, 0.5, "normal"),
    inertia_11=(6.321, 0),
    inertia_22=0.01,
    inertia_33=0.01,
    center_of_mass_without_motor=0,
)

## OPTIONAL stochastic models for aerodynamic surfaces
stochastic_nose_cone = StochasticNoseCone(
    nosecone=nose_cone,
    length=0.001,
)

stochastic_fin_set = StochasticTrapezoidalFins(
    trapezoidal_fins=fin_set,
    root_chord=0.0005,
    tip_chord=0.0005,
    span=0.0005,
)

stochastic_tail = StochasticTail(
    tail=tail,
    top_radius=0.001,
    bottom_radius=0.001,
    length=0.001,
)

stochastic_rail_buttons = StochasticRailButtons(
    rail_buttons=rail_buttons, buttons_distance=0.001
)

stochastic_main = StochasticParachute(
    parachute=main,
    cd_s=0.1,
    lag=0.1,
)

stochastic_drogue = StochasticParachute(
    parachute=drogue,
    cd_s=0.07,
    lag=0.2,
)
# Add them to stochastic rocket
stochastic_rocket.add_motor(stochastic_motor, position=0.001)
stochastic_rocket.add_nose(stochastic_nose_cone, position=(1.134, 0.001))
stochastic_rocket.add_trapezoidal_fins(stochastic_fin_set, position=(0.001, "normal"))
stochastic_rocket.add_tail(stochastic_tail)
stochastic_rocket.set_rail_buttons(
    stochastic_rail_buttons, lower_button_position=(0.001, "normal")
)
stochastic_rocket.add_parachute(stochastic_main)
stochastic_rocket.add_parachute(stochastic_drogue)

## FLIGHT
stochastic_flight = StochasticFlight(
    flight=test_flight,
    inclination=(84.7, 1),  # (mean, std)
    heading=(53, 2),  # (mean, std)
)

## MONTE CARLO
test_dispersion = MonteCarlo(
    filename="MonteCarlo/MonteCarlo", #either save or load to/from this file
    environment=stochastic_env,
    rocket=stochastic_rocket,
    flight=stochastic_flight,
)
# Simulate flights
sim_qty = simpledialog.askinteger("Input", "How many simulations would you like to run?")
test_dispersion.simulate(
    number_of_simulations=sim_qty, append=False, include_function_data=True
)

## INFO
if __name__ == "__main__":
    print("STOCHASTIC ENV")
    stochastic_env.visualize_attributes()
    print("STOCHASTIC MOTOR")
    stochastic_motor.visualize_attributes()
    print("STOCHASTIC ROCKET")
    stochastic_rocket.visualize_attributes()
    print("STOCHASTIC FLIGHT")
    stochastic_flight.visualize_attributes()

