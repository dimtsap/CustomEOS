"""
Connor Krill August 25, 2021
Attempting to write custom EOS tables for Hyades
---
HYADES EOS Format
Taken from 'Appendix II - Equation of State Binary Library File Format' in the 'Hyades User's Guide'
The first line is not used by Hyades, and any notes can be left in the first line
All of the following are word numbers in the file that begin on the second line

1 equation of state number - NUMEOS
2 average atomic number - ZBAR
3 average atomic weight - ABAR
4 normal density - DEN
5 - 6 not used
7 number of density points - NR
8 number of temperature points - NT
9 - NR+8 array of densities (g/cm3)
NR+9 - NR+NT+8 array of temperatures (keV)
NR+NT+9 - NR+NT+NR*NT+8 matrix of pressures (dyne/cm2)
NR+NT+NR*NT+9 - NR+NT+2*NR*NT+8 matrix of specific energies (erg/g)

All floats are formatted ' 0.12345678E+00' for positive values and '-0.12345678E+00' for negative values
The above formatting ensures all floats are 15 characters long
There are 5 floats per line, for a width of 75 characters
"""

from .readingEOS import EOSTable
from datetime import date

def float2eosstr(array):
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


def write_eos(filename, out_filename, verbose=False):
    """Function to read in one EOS file and output a new EOS formatted for use with Hyades

    Args:
        filename (string): Name of input file to be converted
        out_filename (string): Name to write the new EOS to
        verbose (boolean, optional): Toggle to print EOS information during file creation. Does not affect EOS Table.
    """
    eos = EOSTable(filename)
    NT = len(eos.temperatures)
    NR = len(eos.densities)
    if verbose:
        print(f'Loaded EOS {filename!r}')
        print(f'EOS defined for {NR} densities ranging from {eos.densities.min()} to {eos.densities.max()}')
        print(f'EOS defined for {NT} temperatures ranging from {eos.temperatures.min()} to {eos.temperatures.max()}')
    total_data_length = (2 * NR * NT) + NR + NT + 2

    if eos.info['Notes']:
        header_info = eos.info['Notes']
    else:
        header_info = f"EOS Table created on {date.today().strftime('%b-%d-%Y')}"

    header_info = eos.info['Material Name'] + ' ' + header_info
    if verbose:
        print(f'Header Information: {header_info!r}')

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
    error_string = f"EOS Number {eos.info['EOS Number']} is too large, it must be 5 digits or fewer " \
                   f"according to Appendix III of the Hyades User Guide."
    assert len(str(eos.info['EOS Number'])) <= 5, error_string
    error_string = f"The total number of data points {total_data_length} is too large. It must be " \
                   f"5 digits (99999 data points) or fewer according to Appendix III of the Hyades User Guide."
    assert len(str(total_data_length)) <= 5, error_string
    formatted_eos_number = str(eos.info['EOS Number']).rjust(5, ' ')
    formatted_material_properties = f" {eos.info['Average Atomic Number']:.8E}" \
                                    f" {eos.info['Average Atomic Mass']:.8E}" \
                                    f" {eos.info['Ambient Density']:.8E}"
    formatted_data_length = str(total_data_length).rjust(5, ' ')

    data_info = f" {formatted_eos_number}   {formatted_material_properties}    {formatted_data_length}"

    output = f' {NR:.8E} {NT:.8E}'  # add number of densities and number of temperatures
    output += float2eosstr(eos.pressure_eos.columns)  # add array of densities, already in correct units of g/cc
    output += float2eosstr(eos.pressure_eos.index / (11605 * 1000))  # add array of temperatures & convert Kelvin to KeV
    output += float2eosstr(eos.pressure_eos.values * 1e10)  # add matrix of pressures and convert GPa to dynes/cm^2
    # add matrix of specific energies and convert but idk the conversion and never switched it out
    output += float2eosstr(eos.energy_eos.values * 1)

    # a float value in the EOS table is 15 characters long and there are 5 floats per line, for a width of 75 characters
    n = 15 * 5
    lines = [output[i:i+n]+'\n' for i in range(0, len(output), n)]

    with open(out_filename, 'w') as f:
        f.write(header_info + '\n')
        f.write(data_info + '\n')
        f.writelines(lines)
    if verbose:
        print(f'Converted {filename!r} to EOS formatted for Hyades - Hyades EOS is {out_filename!r}')


if __name__ == '__main__':
    filename = 'data/REODP/REODP_diamond_eos-Detailed_AllPhases.xlsx'
    out_filename = 'data/REODP/REODP_diamond_eos_all_phases.txt'
    write_eos(filename, out_filename, verbose=True)



