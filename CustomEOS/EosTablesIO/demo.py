from readingEOS import EOSTable
from plotting_eos import plot_heatmap, plot_isochore, plot_isotherm
import matplotlib.pyplot as plt
plt.style.use('ggplot')


filename = 'data/hyadlibm_NaCl_755.txt'
eos = EOSTable(filename)

# Examples of data stored in EOS object
print(f'Loaded {eos.filename}. A summary is kept in the attribute eos.info as {type(eos.info)}:')
for var in eos.info:
    print('eos.info Key:', var, 'eos.info Value:', eos.info[var])

'''
EOS Tables are pressures and energies as functions of temperature and density.
The temperatures and densities are 1-D numpy arrays which may have different number of points.
The pressures and energies are Pandas DataFrames
'''
print(f'EOS contains {len(eos.temperatures)} temperatures from {min(eos.temperatures)} to {max(eos.temperatures)} degrees Kelvin')
print(f'EOS contains {len(eos.densities)} densities from {min(eos.densities)} to {max(eos.densities)} g/cc')


# Demo of plots showing entire EOS. The line below plots every point in EOS.
plot_heatmap(eos, 'pressure')
# Plot functions can be cropped in temperature or density space to narrow down the EOS region of interest
# This line limits temperatures from 0 - 8,000 degrees K and densities from half to double the ambient density
density_range = (eos.info['Ambient Density'] / 2, eos.info['Ambient Density'] * 2)
plot_heatmap(eos, 'energy', temperature_range=(0, 8000), density_range=density_range)
plt.show()

temperatures = (0, 298, 1000, 5000, 10000)
plot_isotherm(eos, temperatures)
densities = (1.5, 2.0, eos.info['Ambient Density'], 2.5, 3.0)
plot_isochore(eos, densities)
plt.show()

