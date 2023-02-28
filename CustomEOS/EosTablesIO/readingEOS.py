"""Class to read Equations of State from either the Hyades or Excel format"""
import re
import os
import datetime
import numpy as np
import pandas as pd


class EOSTable:
    """Store all the data required by a Hyades EOS table in a single class

    Todo:
        - add material name to the info section so it can be written out later

    Note:
        This parser can read the fixed-width .dat EOS Tables, the hyadlibm printed EOS tables, or the excel format

    Attributes:
        filename (string): Name and location of the EOS file
        info (dictionary): General material properties and notes from the EOS
        pressure_eos (pandas.DataFrame): Table of Pressures in Gigapascals.
            Rows are temperatures in degrees Kelvin, columns are densities in grams per cubic centimeter.
        energy_eos (pandas.DataFrame): Table of energies in erg/g.
            Rows are temperatures in degrees Kelvin, columns are densities in grams per cubic centimeter.
        temperatures (numpy.array): Temperatures in the Pressure and Energy tables in degrees Kelvin.
            Temperatures are the DataFrame.index, which are the rows, of pressure_eos and energy_eos
        densities (numpy.array): Densities in the Pressure and Energy tables in grams per cubic centimeter
            Densities are the DataFrame.columns, which are the columns, of pressure_eos and energy_eos

    """

    def __init__(self, filename, file_type=None):
        """Constructor method to assign attributes to self

        Note:
            Attempts to identify the format of the EOS table as excel, printed from hyadlibm, or the fixed-width
            Hyades format. The identification check is not perfect, and your file may
            work even if the identification fails. If the identification fails and you believe your file
            is correctly formatted, try specifying the file type using the file_type= excel, hyadlibm, or fixed width.
        """
        self.filename = filename
        self.material_name = ''
        self.info = {
            'Ambient Density': np.nan,
            'Average Atomic Mass': np.nan,
            'Average Atomic Number': np.nan,
            'Date Created': '',
            'EOS Number': np.nan,
            'Material Name': '',
            'Notes': ''
        }
        self.pressure_eos = None
        self.energy_eos = None
        self.temperatures = None
        self.densities = None

        # Attempt to identify file format
        if not file_type:  # Check for Excel file type
            if self.filename.endswith('.xlsx') or self.filename.endswith('.xls'):
                file_type = 'excel'

        if not file_type:  # Check if file came from hyadlibm print EOS function
            with open(self.filename) as f:
                lines = f.readlines()
            if lines[2].strip() == 'The HYADES Equation-of-State Library':
                file_type = 'hyadlibm'

        if not file_type:  # Check if file is fixed-width Hyades format
            with open(self.filename) as f:
                lines = f.readlines()
            line_lengths = [len(line) for line in lines[2:10]]
            if all([length == 76 for length in line_lengths]):  # if the first few data lines match fixed-width format
                file_type = 'fixed width'

        if not file_type:
            error_string = f'Failed to identify {self.filename} as an excel EOS, hyadlibm EOS, or fixed-width EOS.' \
                           f'\nIf you believe your table is correctly formatted, try specifying the file type using' \
                           f'file_type= \'excel\', \'hyadlibm\', or \'fixed width\'.'
            raise Exception(error_string)

        # Begin read statements based on file_type
        if file_type == 'excel':
            p, e = self.read_excel_eos()
            self.pressure_eos = p
            self.energy_eos = e
        elif file_type == 'hyadlibm':
            raw_df = self.read_hyadlibm_eos()
            pressure_eos = raw_df.pivot_table(values='Pressure', index='Temperature', columns='Density')
            pressure_eos.index.rename('Temperature (K)', inplace=True)
            pressure_eos.columns.rename('Density (g/cc)', inplace=True)
            self.pressure_eos = pressure_eos
            energy_eos = raw_df.pivot_table(values='Energy', index='Temperature', columns='Density')
            energy_eos.index.rename('Temperature (K)', inplace=True)
            energy_eos.columns.rename('Density (g/cc)', inplace=True)
            self.energy_eos = energy_eos
        elif file_type == 'fixed width':
            self.get_fixed_width_eos_info()
            temperatures, densities, df_pressure, df_energy = self.read_fixed_width_eos()
            self.temperatures = temperatures
            self.densities = densities
            self.pressure_eos = df_pressure
            self.energy_eos = df_energy

        if file_type == 'excel' or file_type == 'hyadlibm':
            self.temperatures = self.pressure_eos.index.to_numpy()
            self.densities = self.pressure_eos.columns.to_numpy()

    @staticmethod
    def is_float(string):
        """Returns true if a string can be converted to a float, otherwise False"""
        try:
            float(string)
            return True
        except ValueError:
            return False

    def get_hyadlibm_eos_info(self):
        """Loads all the descriptive information from the hyadlibm printed EOS file into the class
        Todo:
            - I don't think hyadlibm files contain the material name, idk how to get
            - is it worth writing up my own cheap dictionary with EOS number lookups?

        Return:
            info (dict): Keys are variables, values are entries

        """
        with open(self.filename) as f:
            lines = f.readlines()
        string = lines[7]

        self.info['Date Created'] = string.split()[0]

        pattern_eos = r'EOS\s+\d+'
        match = re.search(pattern_eos, string)
        self.info['EOS Number'] = int(match.group().split()[-1])

        pattern_zbar = r'ZBAR\s+=\s+\d+\.\d{4}E.\d{2}'
        match = re.search(pattern_zbar, string)
        self.info['Average Atomic Number'] = float(match.group().split()[-1])

        pattern_abar = r'ABAR\s+=\s+\d+\.\d{4}E.\d{2}'
        match = re.search(pattern_abar, string)
        self.info['Average Atomic Mass'] = float(match.group().split()[-1])

        pattern_den = r'DEN\s+=\s+\d+\.\d{4}E.\d{2}'
        match = re.search(pattern_den, string)
        self.info['Ambient Density'] = float(match.group().split()[-1])

        return self.info

    def get_fixed_width_eos_info(self):
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
        with open(self.filename) as f:
            lines = f.readlines()

        self.material_name = lines[0].split()[0]  # Material name is usually the first word in the fixed width file

        self.info['Notes'] = lines[0].replace('\n', '')
        info_line = lines[1].split()
        self.info['EOS Number'] = int(info_line[0])
        self.info['Average Atomic Number'] = float(info_line[1])
        self.info['Average Atomic Mass'] = float(info_line[2])
        self.info['Ambient Density'] = float(info_line[3])

        return self.info

    def read_fixed_width_eos(self):
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
        with open(self.filename) as f:
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

    def read_hyadlibm_eos(self):
        """Read an eos table from the Hyades hyadlibm formatting

        Returns:
            df (Pandas DataFrame): columns for the Density, Temperature, Pressure, and Energy of the Material

        """
        self.get_hyadlibm_eos_info()

        with open(self.filename) as f:
            lines = f.readlines()

        df = pd.DataFrame(columns=['Density', 'Temperature', 'Pressure', 'Energy'])
        mode = None
        for line in lines:
            if not line.split():  # skip blank lines
                continue

            first_word = line.split()[0]  # first_word could be a string or a float
            if first_word == 'Pressure':
                mode = 'Pressure'
            elif first_word == 'Energy':
                mode = 'Energy'

            if len(line.split()) >= 2:  # skip lines that have only one word
                if line.split()[1] == 'T=':
                    temps = line.split()[2:]
                    temps = [float(i) for i in temps]

            if self.is_float(first_word):
                '''
                The entries in the EOS file are ten 11-character long numbers with no separation (example on next line)
                4.5277E-01   -1.2495E+10-1.2271E+10-1.2027E+10-1.1761E+10-1.1470E+10-1.1153E+10-1.0807E+10-1.0429E+10-1.0017E+10-9.5660E+09
                4.0000E+00    1.5688E+10 2.3015E+10 3.5635E+10 4.9448E+10 6.4563E+10 8.1169E+10 9.9564E+10 1.2008E+11 1.4340E+11 1.7026E+11
                The number before the space is the density, then every 11 characters is a new entry in the table
                Note in some lines of the file there is no "-", there is a space to represent positive values
                '''
                den = [float(first_word) for i in range(len(temps))]  # copy the density 10 times
                values = [float(line[15+i*11: 15+(i+1)*11]) for i in range(len(temps))]

                if mode == 'Pressure':
                    new_data = pd.DataFrame({'Density': den,
                                             'Temperature': temps,
                                             'Pressure': values
                                             })
                elif mode == 'Energy':
                    new_data = pd.DataFrame({'Density': den,
                                             'Temperature': temps,
                                             'Energy': values
                                             })

                df = df.append(new_data, ignore_index=True)

        df.loc[:, 'Temperature'] = df['Temperature'] * 11605 * 1000  # convert KeV to Kelvin
        df.loc[:, 'Pressure'] = df['Pressure'] * 1e-10  # convert hyades units to GPa
        # energy is in erg/g, I think 1 erg = 1e-10 joules but where does the gram come from
        # density is already in g/cc

        return df

    def read_excel_eos(self):
        """Loads the EOSTable class with eos data from a neatly formatted excel file

        Returns:
            pressure_eos (Numpy Array), energy_eos (Numpy Array)

        """
        pressure_eos = pd.read_excel(self.filename, index_col=0, sheet_name='Pressure')
        energy_eos = pd.read_excel(self.filename, index_col=0, sheet_name='Energy')

        df_info = pd.read_excel(self.filename, index_col=0, sheet_name='Info')
        self.material_name = df_info.loc['Material Name'][0]
        for k in self.info:  # Check the excel file for a row named after each key in the info dictionary
            i = df_info.loc[k][0]
            if isinstance(i, datetime.date):
                self.info[k] = '{:%m/%d/%Y}'.format(i)
            else:
                self.info[k] = i

        self.info['Notes'] = f"Created by {df_info.loc['Author'][0]} on {self.info['Date Created']} {self.info['Notes']}"

        return pressure_eos, energy_eos


if __name__ == '__main__':
    filename = 'data/REODP/REODP_diamond_eos-Detailed_AllPhases.xlsx'
    eos_table = EOSTable(filename)
    for key in eos_table.info:
        print(key, eos_table.info[key])
    print(f'{len(eos_table.densities)} density values. '
          f'Min: {eos_table.densities.min()} Max: {eos_table.densities.max()}')
    print(eos_table.densities)
    print(f'{len(eos_table.temperatures)} temperature values. '
          f'Min: {eos_table.temperatures.min()} Max: {eos_table.temperatures.max()}')
    print(eos_table.temperatures)


# df.applymap(np.isreal).all(1)) # returns a list of booleans, one per row. True if all entries in a row are real numbers
# mask = df.applymap(np.isreal).all(1)
# print(df[~mask])
# print(df.Temperature.unique())
