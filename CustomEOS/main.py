import os
from EosCustomizer import EosCustomizer
from EosTablesIO.EosTable import EosTable

from HyadesRunners.StrengthRunner.HyadesStrengthRunner import HyadesStrengthRunner
from EosDataGenerators.ReodpEosGenerator.ReodpEosGenerator import ReodpEosGenerator
from EosTablesIO.readingEOS import EOSTable
from EosTablesIO.writingEOS import *

path_to_hyades_eos_folder="./EosTablesIO/data"
sesame_eos_file="eos_341.dat"
file_path=os.path.join(path_to_hyades_eos_folder, sesame_eos_file)

eos_table = EosTable.from_fixed_width_hyades_eos(filename=file_path)

reodp_eos_generator = ReodpEosGenerator(eos_table)
hyades_strength_runner = HyadesStrengthRunner()

eos_customizer=EosCustomizer(eos_generator=reodp_eos_generator, 
                             hyades_runner=hyades_strength_runner, 
                             eos_id=345)

eos_customizer.run_customized_hyades(n_runs=1)

output = eos_customizer.custom_hyades_output