"""A quick example of how to convert the EOS Table output by the command Hyadlibm to an Excel file"""
import pandas as pd
from readingEOS import EOSTable

# Specify which file to load and the name of the Excel file to write
load_filename = './data/hyadlibm_diamond_341.txt'
out_filename = 'data/eos_341.xlsx/'

eos = EOSTable(load_filename)  # Load the existing EOS data using the EOSTable class

with pd.ExcelWriter(out_filename) as writer:  # Create a new excel file using pandas
    eos.pressure_eos.to_excel(writer, sheet_name='Pressure (Gpa)')  # Write the pressures to the excel file
    eos.energy_eos.to_excel(writer, sheet_name='Energy (erg/g)')  # Write the energies to the excel file

print(f'Converted {load_filename} to {out_filename}')  # Print confirmation
