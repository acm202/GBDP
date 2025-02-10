from montecarlo import test_dispersion, env

#Data
print(test_dispersion.num_of_loaded_sims) #prints number of simulations ran

test_dispersion.prints.all() # Shows all info

test_dispersion.plots.ellipses(xlim=(-200, 2000), ylim=(-200, 2000)) # simulation result

test_dispersion.plots.all() #all plots

#Save as KML
test_dispersion.export_ellipses_to_kml(
    filename="monte_carlo_analysis_outputs/monte_carlo_class_example.kml",
    origin_lat=env.latitude,
    origin_lon=env.longitude,
    type="impact",
)

# Sensitivity Analysis