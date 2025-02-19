from COTS_montecarlo import test_dispersion, env
from rocketpy.tools import load_monte_carlo_data
from rocketpy.sensitivity import SensitivityModel
print("RESULTS")

#Data
print(test_dispersion.num_of_loaded_sims) #prints number of simulations ran

test_dispersion.prints.all() # Shows all info

test_dispersion.plots.ellipses(xlim=(-500, 4000), ylim=(-500, 3000)) # simulation result

test_dispersion.plots.all() #all plots

#Save as KML
"""
print("SAVING AS KML")
test_dispersion.export_ellipses_to_kml(
    filename="MonteCarlo/MonteCarlo.kml",
    origin_lat=env.latitude,
    origin_lon=env.longitude,
    type="impact",
)
"""
print("MONTE CARLO COMPLETE")
## Sensitivity Analysis
# Used to measure variability due to instrument measurement uncertainty
print("SENSITIVITY ANALYSIS")
analysis_parameters = {
    # Rocket
    "mass": {"mean": 14.426, "std": 0.5},
    "radius": {"mean": 127 / 2000, "std": 1 / 1000},
    # Motor
    "motors_dry_mass": {"mean": 1.815, "std": 1 / 100},
    "motors_grain_density": {"mean": 1815, "std": 50},
    "motors_total_impulse": {"mean": 5700, "std": 50},
    "motors_burn_out_time": {"mean": 3.9, "std": 0.2},
    "motors_nozzle_radius": {"mean": 33 / 1000, "std": 0.5 / 1000},
    "motors_grain_separation": {"mean": 5 / 1000, "std": 1 / 1000},
    "motors_grain_initial_height": {"mean": 120 / 1000, "std": 1 / 100},
    "motors_grain_initial_inner_radius": {"mean": 15 / 1000, "std": 0.375 / 1000},
    "motors_grain_outer_radius": {"mean": 33 / 1000, "std": 0.375 / 1000},
    # Parachutes
    "parachutes_cd_s": {"mean": 10, "std": 0.1},
    "parachutes_lag": {"mean": 1.5, "std": 0.1},
    # Flight
    "heading": {"mean": 53, "std": 2},
    "inclination": {"mean": 84.7, "std": 1},
}

target_variables = ["apogee"]
parameters = list(analysis_parameters.keys())

parameters_matrix, target_variables_matrix = load_monte_carlo_data(
    input_filename="MonteCarlo/SensitivityData.inputs.txt",
    output_filename="MonteCarlo/SensitivityData.outputs.txt",
    parameters_list=parameters,
    target_variables_list=target_variables,
)
# The elevation (ASL) at the launch-site
elevation = 180
# The apogee was saved as ASL, we need to remove the launch site elevation
target_variables_matrix -= elevation

model = SensitivityModel(parameters, target_variables)

parameters_nominal_mean = [
    analysis_parameters[parameter_name]["mean"]
    for parameter_name in analysis_parameters.keys()
]
parameters_nominal_sd = [
    analysis_parameters[parameter_name]["std"]
    for parameter_name in analysis_parameters.keys()
]
#Can also pass the target nominal values, or predict them if not given, such as in this example
model.set_parameters_nominal(parameters_nominal_mean, parameters_nominal_sd)

# Fit model by passing parameters and target variables
model.fit(parameters_matrix, target_variables_matrix)

## Sensitiviy Analysis Results
model.plots.bar_plot()
model.prints.all()