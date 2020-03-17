##
"""
Measles Ward Simulations: Sample demographic
"""
#
import os
import sys
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.SetupParser import SetupParser
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from dtk.utils.Campaign.CampaignClass import *
from dtk.tools.demographics.Node import Node
from dtk.tools.demographics.DemographicsFile import DemographicsFile
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import DownloadAnalyzer
from simtools.Utilities.COMPSUtilities import get_experiment_by_id
from COMPS.Data import QueryCriteria
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PythonHelperFunctions.DemographicsHelpers import *
from PythonHelperFunctions.utils import load_dropbox_path, load_output_path, load_input_path
from pyDOE import lhs
import numpy as np

#Run locally or on HPC
SetupParser.default_block = "HPC"
SetupParser.init(selected_block=SetupParser.default_block)

ScenarioName = "PerfectSchoolClosureForever"
# Set the path for DTK input files
BaseInputPath = load_input_path()
if not os.path.exists(BaseInputPath):
    os.mkdir(BaseInputPath)
OutputPath = os.path.join(load_output_path(), ScenarioName)
if not os.path.exists(OutputPath):
    os.mkdir(OutputPath)
if not os.path.exists(os.path.join(OutputPath, 'input_files')):
    os.mkdir(os.path.join(OutputPath, 'input_files'))
#Name the input files
DemoFile = os.path.join(BaseInputPath, 'demographics.json')
CampaignFile = os.path.join(BaseInputPath, 'campaign.json')
ConfigFile = os.path.join(BaseInputPath, 'config.json')


SimDurationInYears = 1
TotalPopulation = 5e5
cb = DTKConfigBuilder.from_files(ConfigFile, campaign_name=CampaignFile)
cb.set_param('Simulation_Duration', SimDurationInYears*365.0)


demoFile = DemographicsFile.from_file(DemoFile)
demoFile.content['Nodes'][0]['NodeAttributes']['InitialPopulation'] = TotalPopulation

#Fix this
if len(demoFile.nodes)==1:
    for node in demoFile.nodes.values():
        node.pop = TotalPopulation
else:
    raise ValueError('demographics.json assumed to have only one node')

demoFile = SetAgeDistribution(demoFile, os.path.join(load_dropbox_path(),
                'COVID-19','seattle_network','census','age distributions', 'puma_age_dists.csv'))

TotalTransmissionMatrix = TransmissionMatrixFromAgeContactMatrix(filename = os.path.join(load_dropbox_path(),
                'COVID-19','age_contact_matrices', 'MUestimates_all_locations_2.xlsx'))
SchoolTransmissionMatrix = TransmissionMatrixFromAgeContactMatrix(filename = os.path.join(load_dropbox_path(),
                'COVID-19','age_contact_matrices', 'MUestimates_school_2.xlsx'))
HomeTransmissionMatrix = TransmissionMatrixFromAgeContactMatrix(filename = os.path.join(load_dropbox_path(),
                'COVID-19','age_contact_matrices', 'MUestimates_home_2.xlsx'))
WorkTransmissionMatrix = TransmissionMatrixFromAgeContactMatrix(filename = os.path.join(load_dropbox_path(),
                'COVID-19','age_contact_matrices', 'MUestimates_work_2.xlsx'))



demoFile = SetPropertyDependentTransmission(demoFile, TransmissionMatrix_pre=TotalTransmissionMatrix,
                                            TransmissionMatrix_post=TotalTransmissionMatrix-SchoolTransmissionMatrix,
                                            Time_start=72, Duration=2000)  #Set up a bunch of default properties.

demoFile.generate_file(os.path.join(OutputPath, 'input_files', os.path.basename(DemoFile)))
cb.dump_files(working_directory=os.path.join(OutputPath, 'input_files'))
cb.set_param("Demographics_Filenames", [os.path.basename(DemoFile)])

#Add all of the necessary experiment files
cb.set_experiment_executable(path=os.path.join(BaseInputPath, 'Eradication.exe'))
cb.set_input_files_root(os.path.join(OutputPath, 'input_files'))
cb.set_dll_root(BaseInputPath)

#Define a sample point function for doing sweeps/sampling.  This function basically maps the sampled parameters, fed
# as a dictionary, to the configuration and campaign parameters that should be changed.
def sample_point_fn(CB, params_dict, sample_index):
    tags ={}

    for param, value in params_dict.items():
        if param.startswith('META'):
            None

        else:
            CB.set_param(param, value)
            tags[param] = value
    CB.set_param('Run_Number', sample_index)
    tags['__sample_index__']=sample_index
    return tags



if __name__ == "__main__":

    #A dictionary of parameters to sample, and the range to sample from
    sample_dimension_dict = {}
    sample_dimension_dict['Base_Infectivity_Constant'] = [0.3, 0.5]

    #Doing a parameter sweep uses a list of abstract functions, here contained in mod_fns.  These functions basically
    #change values in the "cb" object that contains the config and campaign files, as a dict and a class, respectively.
    mod_fns = []
    random.seed(12884)
    nSamples = 500
    samples = {}
    samples['Base_Infectivity_Constant'] = np.linspace(sample_dimension_dict['Base_Infectivity_Constant'][0],
                          sample_dimension_dict['Base_Infectivity_Constant'][1],
                          nSamples)

    for ix in range(nSamples):
        param_dict = {}
        currDim = 0
        for param, paramRange in sample_dimension_dict.items():
            param_dict[param] = samples[param][ix]
            currDim += 1
        mod_fns.append(ModFn(sample_point_fn, param_dict, ix))

    builder = ModBuilder.from_combos(mod_fns)

    exp_name = 'Perfect School Closure Forever'
    exp_manager = ExperimentManagerFactory.from_cb(cb)

    run_sim_args = {'config_builder': cb,
                    'exp_name': exp_name,
                    'exp_builder': builder}
    exp_manager.run_simulations(**run_sim_args)
    exp_list = pd.read_csv(os.path.join(load_output_path(), 'Experiment_tracking.csv'), index_col="Index")
    exp_list = exp_list.append(pd.Series({'Description':ScenarioName, 'Scenario': 1, 'Experiment ID': exp_manager.experiment.exp_id, 'Nsims': nSamples}, name=len(exp_list)))
    exp_list.to_csv(os.path.join(load_output_path(), 'Experiment_tracking.csv'))#    exp_manager.wait_for_finished(verbose=True)
#    am = AnalyzeManager('latest', analyzers=DownloadAnalyzer(filenames=['output/InsetChart.json', 'output/PropertyReport.json'], output_path=outputPath))
#    am.analyze()
