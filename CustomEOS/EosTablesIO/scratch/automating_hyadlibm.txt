"""Connor and Dimitris' first attempt at automating Hyades EOS install using hyadlibm command. September 7, 2022"""
import os
import subprocess


def add_eos_to_hyades(filename):
    """Adds an EOS table assumed to be in C:\Hyades\EOS-Opacity\QEOS folder to Hyades using hyadlibm

    Note:
    This function only works on computers with Hyades locally installed.
    This function does *not* check if the EOS is correctly formatted.


    To install an EOS table using hyadlibm, several keyboard inputs are needed after 'hyadlibm'.
    Each input and a short description of its purpose is below.
    1\n           | Select option 1, c:\Hyades\data\eoslib.lbf, then press enter
    2\n           | Select option 2, Add a material to the library, then press enter
    filename+'\n' | Enter the filename with its absolute path then press enter
    7\n           | Select option 7, Quit, then press enter

    ToDo:
        - Throw an error if the EOS ID you want to install is currently in hyadlibm

    :param string filename: Name of the Hyades formatted EOS table
    :return: terminal output, terminal error
    """
    command = bytes('hyadlibm', 'utf-8')  # subprocess library requires commands as bytes, not strings
    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    path_to_eos_library = os.path.join('C:', os.sep, 'Hyades', 'EOS-Opacity', 'QEOS')  # Path to EOS library on Wicks Windows computer
    absolute_path = os.path.join(path_to_eos_library, filename)

    hyadlibm_inputs = ''.join(['1\n', '2\n', absolute_path+'\n', '7\n'])
    input = bytes(hyadlibm_inputs, 'utf-8')
    stdout, stderr = p.communicate(input=input)

    return stdout, stderr


def remove_eos_from_hyades(EOS_ID):
    """Removes an installed EOS table from hyades using hyadlibm

    Note:
    This function only works on computers with Hyades locally installed.

    To remove an EOS table using hyadlibm, several keyboard inputs are needed after 'hyadlibm'.
    Each input and a short description of its purpose is below.
    1\n         | Select option 1, c:\Hyades\data\eoslib.lbf, then press enter
    3\n         | Select option 2, Delete a material from the library , then press enter
    EOS_ID+'\n' | Enter the EOS ID then press enter
    \n          | Press enter to scroll past a menu displaying current EOS tables.
    7\n         | Select option 7, Quit, and then press enter

    ToDo:
        - Throw an error if the EOS ID you want to remove is not currently in hyadlibm

    :param string EOS_ID: EOS ID (AKA Hyades Table Number) to be removed
    :return: terminal output, terminal error
    """
    if isinstance(EOS_ID, int):  # lazy check if user input EOS_ID as int instead of str
        EOS_ID = str(EOS_ID)

    command = bytes('hyadlibm', 'utf-8')  # subprocess library requires commands as bytes, not strings
    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    hyadlibm_inputs = ''.join(['1\n', '3\n', EOS_ID+'\n', '\n', '7\n'])
    input = bytes(hyadlibm_inputs, 'utf-8')
    stdout, stderr = p.communicate(input=input)

    return stdout.decode('utf-8'), stderr.decode('utf-8')


if __name__ == '__main__':
    filename = 'QEOS_345.DAT'
    EOS_ID = '345'

    message, error = add_eos_to_hyades(filename)
    print(message.decode('utf-8'))  # outputs of functions need to be decoded to print as strings
