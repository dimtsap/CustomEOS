import subprocess
from EosDataGenerators.EosGenerator import EosGenerator
from HyadesRunners.HyadesRunner import HyadesRunner


class EosCustomizer:
    def __init__(self, eos_generator: EosGenerator, 
                 hyades_runner:HyadesRunner,
                 eos_id) -> None:
        self.eos_generator = eos_generator
        self.hyades_runner = hyades_runner
        self.eos_id=eos_id
        self.custom_hyades_output=[]

    def run_customized_hyades(self, n_runs=2):
        for _ in range(n_runs):
            # EosCustomizer.print_installed_tables_to_file()
            # exists = EosCustomizer.check_if_eos_id_exists(eos_id=self.eos_id)
            # EosCustomizer.remove_installed_tables_file()

            filename = self.eos_generator.run_once_and_generate_eos_file()

            # self.check_if_custom_eos_file_has_correct_id(filename=filename, eos_id=self.eos_id)
            # self.add_eos_to_hyades(filename=filename)

            # output=self.hyades_runner.run_once()
            # self.custom_hyades_output.append(output)

            # EosCustomizer.print_installed_tables_to_file()
            # exists = EosCustomizer.check_if_eos_id_exists(eos_id=self.eos_id)
            
            # if exists:
            #     EosCustomizer.remove_eos_from_hyades(self.eos_id)
            # EosCustomizer.remove_installed_tables_file()

    def print_installed_tables_to_file():
        """Uses hyadlibm command to open current """
        command = bytes('hyadlibm', 'utf-8')
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        hyadlibm_inputs = ''.join(['1\n', '5\n', "list.txt"+'\n', '7\n'])
        input = bytes(hyadlibm_inputs, 'utf-8')
        stdout, stderr = p.communicate(input=input)

        return stdout.decode('utf-8'), stderr.decode('utf-8')

    def check_if_eos_id_exists(eos_id):
        """Reads list of already installed EOS and returns true if the eos_id to be installed already exists."""
        with open('list.txt') as f:
            lines = f.readlines()
        ids = [int(line.split()[0]) for line in lines[21:]]
        exists = eos_id in ids

        if exists:
            raise ValueError(f"The EOS with Id-{eos_id} that you are trying to install, already exists")

        return exists

    def check_if_custom_eos_file_has_correct_id(self, filename, eos_id):
        raise NotImplementedError()

    def remove_installed_tables_file():
        raise NotImplementedError()

    def add_eos_to_hyades(self, filename):
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

    def remove_eos_from_hyades(eos_id):
        """Removes an installed EOS table from hyades using hyadlibm

        Note:
        This function only works on computers with Hyades locally installed.

        To remove an EOS table using hyadlibm, several keyboard inputs are needed after 'hyadlibm'.
        Each input and a short description of its purpose is below.
        1\n         | Select option 1, c:\Hyades\data\eoslib.lbf, then press enter
        3\n         | Select option 2, Delete a material from the library , then press enter
        eos_id+'\n' | Enter the EOS ID then press enter
        \n          | Press enter to scroll past a menu displaying current EOS tables.
        7\n         | Select option 7, Quit, and then press enter

        ToDo:
            - Throw an error if the EOS ID you want to remove is not currently in hyadlibm

        :param string eos_id: EOS ID (AKA Hyades Table Number) to be removed
        :return: terminal output, terminal error
        """
        if isinstance(eos_id, int):  # lazy check if user input eos_id as int instead of str
            eos_id = str(eos_id)

        command = bytes('hyadlibm', 'utf-8')  # subprocess library requires commands as bytes, not strings
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        hyadlibm_inputs = ''.join(['1\n', '3\n', eos_id+'\n', '\n', '7\n'])
        input = bytes(hyadlibm_inputs, 'utf-8')
        stdout, stderr = p.communicate(input=input)

        return stdout.decode('utf-8'), stderr.decode('utf-8')
