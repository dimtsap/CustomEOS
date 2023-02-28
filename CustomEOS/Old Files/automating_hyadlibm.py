"""Connor and Dimitris' first attempt at automating Hyades EOS install using hyadlibm command. September 7, 2022"""
import os
import subprocess

def create_custom_eos(sample=None):
    eos_id=345

    print_installed_tables_to_file()
    exists = check_if_eos_id_exists(eos_id)
    

    filename = create_eos_file()
    add_eos_to_hyades(filename)

    run_hyades()
    output = read_hyades_output()

    exists = check_if_eos_id_exists()
    if exists:
        remove_eos_from_hyades(eos_id)
    
    return output




def read_hyades_output():
    pass

def create_eos_file(eos_id):
    # Should we run REODP here?
    pass    

def run_hyades():

    pass

def check_if_eos_id_exists(eos_id):
    """Reads list of already installed EOS and returns true if the eos_id to be installed already exists."""
    with open('list.txt') as f:
        lines = f.readlines()
    ids = [int(line.split()[0]) for line in lines[21:]]
    return eos_id in ids

def print_installed_tables_to_file():
    """Uses hyadlibm command to open current """
    command = bytes('hyadlibm', 'utf-8')
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    hyadlibm_inputs = ''.join(['1\n', '5\n', "list.txt"+'\n', '7\n'])
    input = bytes(hyadlibm_inputs, 'utf-8')
    stdout, stderr = p.communicate(input=input)

    return stdout.decode('utf-8'), stderr.decode('utf-8')

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
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

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
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    hyadlibm_inputs = ''.join(['1\n', '3\n', EOS_ID+'\n', '\n', '7\n'])
    input = bytes(hyadlibm_inputs, 'utf-8')
    stdout, stderr = p.communicate(input=input)

    return stdout.decode('utf-8'), stderr.decode('utf-8')


if __name__ == '__main__':
    filename = 'QEOS_345.DAT'
    EOS_ID = '345'

    message, error = add_eos_to_hyades(filename)
    print(message.decode('utf-8'))  # outputs of functions need to be decoded to print as strings
