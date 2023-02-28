from EosDataGenerators.EosGenerator import EosGenerator
from UQpy.distributions import Uniform
from UQpy.sampling.stratified_sampling import LatinHypercubeSampling
from UQpy.run_model.model_execution import ThirdPartyModel
from UQpy.run_model.RunModel import RunModel
import os
import shutil
import numpy as np
from EosTablesIO.readingEOS import EOSTable


class ReodpEosGenerator(EosGenerator):
    def __init__(self, eos_table: EOSTable) -> None:
        self.eos_table=eos_table
        
        self._min_temperature=min(eos_table.temperatures) if min(eos_table.temperatures)>0 else 1.0
        self._max_temperature=max(eos_table.temperatures)
        self._n_temperatures=len(eos_table.temperatures)
        
        self._min_density=min(eos_table.densities)
        self._max_density=max(eos_table.densities)
        self._n_densities=len(eos_table.densities)
        # num_points between Volume 1.0 & 5.7
        # index of points between 1.0 & 5.7


        # Cold parameters for Vinet EOS
        phi0_nominal = -7.5
        B0_nominal = 51.11
        V0_nominal = 8.596
        Bprime_nominal = 5.848
        # Breakpoint1
        Vb1_nominal = 3.9
        a1_nominal = -5.0
        b1_nominal = 5.0
        n1_nominal = 3.0
        # Breakpoint2
        Vb2_nominal = 2.7
        a2_nominal = 10.0
        b2_nominal = 3.0
        n2_nominal = 3.0
        # Breakpoint3
        Vb3_nominal = 1.9
        a3_nominal = -40.0
        b3_nominal = 5.0
        n3_nominal = 2.0
        # Breakpoint4
        Vb4_nominal = 1.13
        a4_nominal = 80.0
        b4_nominal = 5.0
        n4_nominal = 3.0
        # Quasi-harmonic ion-thermal parameters for EOS
        Vp_nominal = 6.695
        thetA_nominal = 520.0
        AA_nominal = 0.0
        BA_nominal = 0.84
        thetB_nominal = 520.0
        AB_nominal = 0.0
        BB_nominal = 0.84
        thet1_nominal = 520.0
        A1_nominal = 0.0
        B1_nominal = 0.84

        # Create marginals
        dist_phi0 = Uniform(loc=1.1 * phi0_nominal, scale=-0.2 * phi0_nominal)
        dist_B0 = Uniform(loc=0.9 * B0_nominal, scale=0.2 * B0_nominal)
        dist_V0 = Uniform(loc=0.9 * V0_nominal, scale=0.2 * V0_nominal)
        dist_Bprime = Uniform(loc=0.9 * Bprime_nominal, scale=0.2 * Bprime_nominal)

        dist_Vp = Uniform(loc=0.9 * Vp_nominal, scale=0.2 * Vp_nominal)
        dist_thetA = Uniform(loc=0.9 * thetA_nominal, scale=0.2 * thetA_nominal)
        dist_AA=Uniform(loc=0.0, scale=0.2)
        dist_BA=Uniform(loc=0.9 * BA_nominal, scale=0.2 * BA_nominal)

        dist_thetB = Uniform(loc=0.9 * thetB_nominal, scale=0.2 * thetB_nominal)
        dist_AB=Uniform(loc=0.0, scale=0.2)
        dist_BB=Uniform(loc=0.9 * BB_nominal, scale=0.2 * BB_nominal)

        dist_thet1 = Uniform(loc=0.9 * thet1_nominal, scale=0.2 * thet1_nominal)
        dist_A1=Uniform(loc=0.0, scale=0.2)
        dist_B1=Uniform(loc=0.9 * B1_nominal, scale=0.2 * B1_nominal)

        dist_Vb1=Uniform(loc=0.9 * Vb1_nominal, scale=0.2 * Vb1_nominal)
        dist_a1=Uniform(loc=1.1 * a1_nominal, scale=-0.2 * a1_nominal)
        dist_b1=Uniform(loc=0.9 * b1_nominal, scale=0.2 * b1_nominal)
        dist_n1=Uniform(loc=0.9 * n1_nominal, scale=0.2 * n1_nominal)

        dist_Vb2=Uniform(loc=0.9 * Vb2_nominal, scale=0.2 * Vb2_nominal)
        dist_a2=Uniform(loc=0.9 * a2_nominal, scale=0.2 * a2_nominal)
        dist_b2=Uniform(loc=0.9 * b2_nominal, scale=0.2 * b2_nominal)
        dist_n2=Uniform(loc=0.9 * n2_nominal, scale=0.2 * n2_nominal)

        dist_Vb3=Uniform(loc=0.9 * Vb3_nominal, scale=0.2 * Vb3_nominal)
        dist_a3=Uniform(loc=1.1 * a3_nominal, scale=-0.2 * a3_nominal)
        dist_b3=Uniform(loc=0.9 * b3_nominal, scale=0.2 * b3_nominal)
        dist_n3=Uniform(loc=0.9 * n3_nominal, scale=0.2 * n3_nominal)

        dist_Vb4=Uniform(loc=0.9 * Vb4_nominal, scale=0.2 * Vb4_nominal)
        dist_a4=Uniform(loc=0.9 * a4_nominal, scale=0.2 * a4_nominal)
        dist_b4=Uniform(loc=0.9 * b4_nominal, scale=0.2 * b4_nominal)
        dist_n4=Uniform(loc=0.9 * n4_nominal, scale=0.2 * n4_nominal)

        marginals = [dist_phi0, dist_B0, dist_V0, dist_Bprime, 
                    dist_Vb1, dist_a1, dist_b1, dist_n1,
                    dist_Vb2, dist_a2, dist_b2, dist_n2,
                    dist_Vb3, dist_a3, dist_b3, dist_n3,
                    dist_Vb4, dist_a4, dist_b4, dist_n4,
                    dist_Vp, dist_thetA, dist_AA, dist_BA,
                    dist_thetB, dist_AB, dist_BB,
                    dist_thet1, dist_A1, dist_B1]

        self.sampling = LatinHypercubeSampling(nsamples=1, distributions=marginals)

        folder_path = os.path.dirname(os.path.abspath(__file__))
        exists = os.path.exists(os.path.join(folder_path,'reodp_runner.py'))
        shutil.copyfile(os.path.join(folder_path,'reodp_runner.py'), os.path.join(os.getcwd(), 'reodp_runner.py'))
        shutil.copyfile(os.path.join(folder_path,'process_output.py'), os.path.join(os.getcwd(), 'process_output.py'))
        shutil.copyfile(os.path.join(folder_path,'Initial.dat'), os.path.join(os.getcwd(), 'Initial.dat'))
        shutil.copyfile(os.path.join(folder_path,'REODP-v4.exe'), os.path.join(os.getcwd(), 'REODP-v4.exe'))
        if not os.path.exists('INDATA'):
            os.mkdir('INDATA')
        if not os.path.exists('OUTDATA'):
            os.mkdir('OUTDATA')


        reodp_model = ThirdPartyModel(input_template="Initial.dat", var_names=['phi0', 'B0', 'V0', 'Bprime', 
                                        'Vb1', 'a1', 'b1', 'n1', 'Vb2', 'a2', 'b2', 'n2', 'Vb3', 'a3', 'b3', 'n3', 'Vb4', 'a4', 'b4', 'n4',
                                        'Vp', 'thetA', 'AA', 'BA', 'thetB', 'AB', 'BB', 'thet1', 'A1', 'B1', 
                                        'n_temperatures', 'min_temperature', 'max_temperature', 'n_densities'],
                                      model_script='reodp_runner.py', 
                                      model_object_name='reodp_run',
                                      output_script="process_output.py",
                                      output_object_name='read_output', delete_files=False)
        self.run_reodp_model = RunModel(model=reodp_model)

    
    def run_once_and_generate_eos_file(self):
        self.sampling.run(nsamples=1)
        # Append min, max temp, density etc
        samples = self.sampling.samples.copy()
        samples = np.append(samples, [self._n_temperatures, self._min_temperature, self._max_temperature, self._n_densities])

        self.run_reodp_model.run(samples=samples)

        eos_data = self.run_reodp_model.qoi_list[-1]
        ## Add code to write to file
        



