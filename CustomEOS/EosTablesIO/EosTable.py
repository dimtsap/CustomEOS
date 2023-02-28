import re
import os
import datetime
import string
import numpy as np
import pandas as pd
from datetime import date


class EosTable:

    def __init__(self, material_name:string, info:dict, 
                 pressure_eos:pd.DataFrame, energy_eos:pd.DataFrame, 
                 temperatures:list, densities:list) -> None:
        self.material_name=material_name
        self.info=info
        self.pressure_eos=pressure_eos
        self.energy_eos=energy_eos
        self.temperatures=temperatures
        self.densities=densities

    @classmethod
    def from_excel_file(cls, filename):
        #check if file exists
        if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
            raise ValueError()
        material_name, info, pressure_eos, energy_eos = EosTable._read_excel_eos()
        temperatures = pressure_eos.index.to_numpy()
        densities = pressure_eos.columns.to_numpy()
        return cls(material_name=material_name,
                   info=info,
                   pressure_eos=pressure_eos,
                   energy_eos=energy_eos,
                   temperatures=temperatures,
                   densities=densities)

    def _read_excel_eos(filename):
        """Loads the EOSTable class with eos data from a neatly formatted excel file

        Returns:
            pressure_eos (Numpy Array), energy_eos (Numpy Array)

        """
        pressure_eos = pd.read_excel(filename, index_col=0, sheet_name='Pressure')
        energy_eos = pd.read_excel(filename, index_col=0, sheet_name='Energy')

        info = {
            'Ambient Density': np.nan,
            'Average Atomic Mass': np.nan,
            'Average Atomic Number': np.nan,
            'Date Created': '',
            'EOS Number': np.nan,
            'Material Name': '',
            'Notes': ''
        }

        df_info = pd.read_excel(filename, index_col=0, sheet_name='Info')
        material_name = df_info.loc['Material Name'][0]
        for k in info:  # Check the excel file for a row named after each key in the info dictionary
            i = df_info.loc[k][0]
            if isinstance(i, datetime.date):
                info[k] = '{:%m/%d/%Y}'.format(i)
            else:
                info[k] = i

        info['Notes'] = f"Created by {df_info.loc['Author'][0]} on {info['Date Created']} {info['Notes']}"

        return material_name, info, pressure_eos, energy_eos

    @classmethod
    def from_fixed_width_hyades_eos(cls, filename):
        #check if file exists
        with open(filename) as f:
            lines = f.readlines()
        line_lengths = [len(line) for line in lines[2:10]]
        if not (all([length == 76 for length in line_lengths])):  # if the first few data lines match fixed-width format
            raise ValueError()

        material_name, info = EosTable.get_fixed_width_eos_info(filename)
        temperatures, densities, pressure_eos, energy_eos = EosTable.read_fixed_width_eos(filename)
        return cls(material_name=material_name,
                   info=info,
                   pressure_eos=pressure_eos,
                   energy_eos=energy_eos,
                   temperatures=temperatures,
                   densities=densities)

    def get_fixed_width_eos_info(filename):
        """Reads the material information from a fixed-width Hyades EOS format and assigns self.info dictionary

        Todo:
            - I know there is a Lithium Flouride eos that lists the material name as "Lithium Flouride"
              so  grabbing the first word as the material name will not always work

        HYADES EOS Format
            Taken from 'Appendix II - Equation of State Binary Library File Format' in the 'Hyades User's Guide'
            The first line is not used by Hyades, and any notes can be left in the first line
            All of the following are word numbers in the file that begin on the second line

            1 equation of state number - NUMEOS
            2 average atomic number - ZBAR
            3 average atomic weight - ABAR
            4 normal density - DEN
            5 not used
            6 not used

        Returns:

        """
        with open(filename) as f:
            lines = f.readlines()

        info = {
            'Ambient Density': np.nan,
            'Average Atomic Mass': np.nan,
            'Average Atomic Number': np.nan,
            'Date Created': '',
            'EOS Number': np.nan,
            'Material Name': '',
            'Notes': ''
        }

        material_name = lines[0].split()[0]  # Material name is usually the first word in the fixed width file

        info['Notes'] = lines[0].replace('\n', '')
        info_line = lines[1].split()
        info['EOS Number'] = int(info_line[0])
        info['Average Atomic Number'] = float(info_line[1])
        info['Average Atomic Mass'] = float(info_line[2])
        info['Ambient Density'] = float(info_line[3])

        return material_name, info

    def read_fixed_width_eos(filename):
        """Reads the EOS table info from a fixed-width EOS table.

        Note:
            This is the format that Hyades takes in as an EOS table.

        HYADES EOS Format
            Taken from 'Appendix II - Equation of State Binary Library File Format' in the 'Hyades User's Guide'
            The first line is not used by Hyades, and any notes can be left in the first line
            All of the following are word numbers in the file that begin on the second line

            1 equation of state number - NUMEOS
            2 average atomic number - ZBAR
            3 average atomic weight - ABAR
            4 normal density - DEN
            5 not used
            6 not used
            7 number of density points - NR
            8 number of temperature points - NT
            9 - NR+8 array of densities (g/cm3)
            NR+9 - NR+NT+8 array of temperatures (keV)
            NR+NT+9 - NR+NT+NR*NT+8 matrix of pressures (dyne/cm2)
            NR+NT+NR*NT+9 - NR+NT+2*NR*NT+8 matrix of specific energies (erg/g)

            All floats are formatted ' 0.12345678E+00' for positive values and '-0.12345678E+00' for negative values
            The above formatting ensures all floats are 15 characters long
            There are 5 floats per line, for a line width of 75 characters

        Returns:
            temperatures (numpy array), densities (numpy array), pressures (Pandas DataFrame), energies (Pandas DataFrame)
        """
        with open(filename) as f:
            lines = f.readlines()

        all_data = ''.join(lines[2:])
        all_data = all_data.replace('\n', '')
        words = [all_data[i:i+15] for i in range(0, len(all_data), 15)]
        number_of_densities = int(float(words[0]))  # int() can't handle the scientific notation so use float() first
        number_of_temperatures = int(float(words[1]))

        # Densities start at 2 and there are number_of_densities of them
        # Densities are already in g/cc, no unit conversion needed
        start = 2
        stop = 2 + number_of_densities
        densities = np.array([float(i) for i in words[start:stop]])

        # Temperatures start where densities end and there are number_of_temperatures of them
        temperature_unit_conversion = 11605 * 1000  # Convert KeV to Kelvin
        start = stop
        stop = stop + number_of_temperatures
        temperatures = [float(i) * temperature_unit_conversion for i in words[start: stop]]
        temperatures = np.array(temperatures)

        # Pressures start where temperatures end and there are (number_of_densities * number_of_temperatures) of them
        pressure_unit_conversion = 1e-10  # Convert dynes/cm^2 to Gigapascals
        start = stop
        stop = stop + (number_of_densities * number_of_temperatures)
        pressures = [float(i) * pressure_unit_conversion for i in words[start:stop]]
        pressures = np.array(pressures).reshape(number_of_temperatures, number_of_densities)

        # Energies start where pressures end and there are (number_of_densities * number_of_temperatures) of them
        energy_unit_conversion = 1  # Energies are in erg/g, not sure if these need converting
        start = stop
        stop = stop + (number_of_densities * number_of_temperatures)
        energies = [float(i) * energy_unit_conversion for i in words[start:stop]]
        energies = np.array(energies).reshape(number_of_temperatures, number_of_densities)

        df_pressure = pd.DataFrame(data=pressures, columns=densities, index=temperatures)
        df_pressure.index.rename('Temperature (K)', inplace=True)
        df_pressure.columns.rename('Density (g/cc)', inplace=True)
        df_energy = pd.DataFrame(data=energies, columns=densities, index=temperatures)
        df_energy.index.rename('Temperatures (K)', inplace=True)
        df_energy.columns.rename('Density (g/cc)', inplace=True)

        return temperatures, densities, df_pressure, df_energy


    def write_eos(self, output_filename, verbose=False):
        """Function to read in one EOS file and output a new EOS formatted for use with Hyades

        Args:
            filename (string): Name of input file to be converted
            out_filename (string): Name to write the new EOS to
            verbose (boolean, optional): Toggle to print EOS information during file creation. Does not affect EOS Table.
        """
        NT = len(self.temperatures)
        NR = len(self.densities)
        total_data_length = (2 * NR * NT) + NR + NT + 2

        if self.info['Notes']:
            header_info = self.info['Notes']
        else:
            header_info = f"EOS Table created on {date.today().strftime('%b-%d-%Y')}"

        header_info = self.info['Material Name'] + ' ' + header_info

        # This line was replaced in Jan 2022 by the more thorough and correct approach below
        # The order of the data_info line is EOS ZBAR ABAR DEN SIZE
        # data_info = f"   {eos.info['EOS Number']}      {eos.info['Average Atomic Number']:.8E}" \
        #             f" {eos.info['Average Atomic Mass']:.8E}" \
        #             f" {eos.info['Ambient Density']:.8E}   {total_data_length}"

        '''
        A note about the formatting of the data_info string, which is the second line in the EOS file:
        From Appendix II - Equation of State ASCII Material File Format in the Hyades User Guide
        The format of the second line in the EOS is 1x,i5,4x,1p3e15.8,3x,i5.
        Using https://www.obliquity.com/computer/fortran/format.html we figured out this is Fortran Notation for
        1x - a single space
        i5 - an right-justified integer with a total width of 5 characters, using spaces to pad
            Example: 123 would become '  123' and 56789 would stay '56789'
        4x - four spaces
        1p3e15.8 - three scientific notation floats 15 characters wide including 8 after the decimal each multiplied by 10^1
            Single Example: 31.4159 would become ' 3.14159000E+01' and -1234.5678 would become '-1.23456780E+01'
            Complete Example: 1.23 45.6 7.89 would become ' 1.23000000E+00 4.56000000E+01 7.89000000E+00'
                            notice that the spaces between numbers are counted as a part of the 15 character width.
            Note: The p1 at the beginning of this format is supposed to denote multiplying the value by 10^1,
                but some EOS tables in Hyades have exponents of E+00, seemingly disagreeing with the notation.
                As of January 2022 I have no explanation for this.
        3x - three spaces
        i5 - another right-justified integer with a total width of 5 characters, using spaces to pad
        '''
        error_string = f"EOS Number {self.info['EOS Number']} is too large, it must be 5 digits or fewer " \
                    f"according to Appendix III of the Hyades User Guide."
        assert len(str(self.info['EOS Number'])) <= 5, error_string
        error_string = f"The total number of data points {total_data_length} is too large. It must be " \
                    f"5 digits (99999 data points) or fewer according to Appendix III of the Hyades User Guide."
        assert len(str(total_data_length)) <= 5, error_string
        formatted_eos_number = str(self.info['EOS Number']).rjust(5, ' ')
        formatted_material_properties = f" {self.info['Average Atomic Number']:.8E}" \
                                        f" {self.info['Average Atomic Mass']:.8E}" \
                                        f" {self.info['Ambient Density']:.8E}"
        formatted_data_length = str(total_data_length).rjust(5, ' ')

        data_info = f" {formatted_eos_number}   {formatted_material_properties}    {formatted_data_length}"

        output = f' {NR:.8E} {NT:.8E}'  # add number of densities and number of temperatures
        output += EosTable._float2eosstr(self.pressure_eos.columns)  # add array of densities, already in correct units of g/cc
        output += EosTable._float2eosstr(self.pressure_eos.index / (11605 * 1000))  # add array of temperatures & convert Kelvin to KeV
        output += EosTable._float2eosstr(self.pressure_eos.values * 1e10)  # add matrix of pressures and convert GPa to dynes/cm^2
        # add matrix of specific energies and convert but idk the conversion and never switched it out
        output += EosTable._float2eosstr(self.energy_eos.values * 1)

        # a float value in the EOS table is 15 characters long and there are 5 floats per line, for a width of 75 characters
        n = 15 * 5
        lines = [output[i:i+n]+'\n' for i in range(0, len(output), n)]

        with open(output_filename, 'w') as f:
            f.write(header_info + '\n')
            f.write(data_info + '\n')
            f.writelines(lines)

    def _float2eosstr(array):
        """Converts a numpy array of floats to a hyades EOS formatted string
        Does a lazy attempt to flatten multi dimensional arrays into 1-D.
        All floats are formatted ' 0.12345678E+00' for positive values and '-0.12345678E+00' for negative values
        Args:
            array (numpy array):

        Returns:
            output (string): a long string with all your floats formatted for hyades EOS

        """
        if len(array.shape) > 1:
            try:
                array = array.reshape(-1,)
            except ValueError:
                raise Exception(f'Tried and failed to reshape the {len(array.shape)}-D input array to a 1-D array')

        s = [f'{i:.8E}' if i < 0 else f' {i:.8E}' for i in array]
        return ''.join(s)

    