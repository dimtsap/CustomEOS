import os
import fire
from os.path import dirname
import os.path
from os import path
import subprocess

def reodp_run(index):
    ## Copy REODP Input file to the correct folder
    name_ = 'Initial_' + str(index) + '.dat'
    filename ='Initial.dat'

    current_dir = os.getcwd()

    initial_path = os.path.join(current_dir, 'InputFiles', name_)
    final_path = os.path.join(current_dir, 'INDATA', filename)

    copy_input_command = 'copy ' + initial_path + ' ' + final_path
    os.system(copy_input_command)

    ## Change REODP execution privileges
    # os.system("chmod +x REODP-v4.out")

    ## Execute REODP 
    print(f"Executing run #{index}")
    subprocess.call('REODP-v4.exe')
    # os.system("./REODP-v4.out")

    os.makedirs("OutputFiles", exist_ok=True)
    os.system(f"copy .\\OUTDATA\\TotalEOS.dat .\\OutputFiles\\TotalEOS_{index}.dat")

if __name__ == '__main__':
    fire.Fire(reodp_run)
