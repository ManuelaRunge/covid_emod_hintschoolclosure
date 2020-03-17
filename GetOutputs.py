##
"""
Measles Ward Simulations: Sample demographic
"""
#
import os, sys
import time
import pandas as pd
from simtools.SetupParser import SetupParser
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Utilities.COMPSUtilities import get_experiment_by_id
from COMPS.Data import QueryCriteria
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PythonHelperFunctions.utils import load_output_path
from SCOutputAnalyzer import SCOutputAnalyzer
SetupParser.default_block = "HPC"



if __name__ == "__main__":
    SetupParser.init()
    exp_list = pd.read_csv(os.path.join(load_output_path(), 'Experiment_tracking.csv'), index_col="Index")

    for index, row in exp_list.iterrows():

        exp = row['Experiment ID']
        print('Checking experiment ' + exp)
        tmp = get_experiment_by_id(exp, query_criteria=QueryCriteria().select_children(["tags"]))
        foldername = row['Description']
        outDir = os.path.join(load_output_path(), foldername, 'simOutputs')
        if not os.path.exists(outDir):
            os.mkdir(outDir)

        am = AnalyzeManager(exp, analyzers=SCOutputAnalyzer(filenames=['output/InsetChart.json', 'output/PropertyReport.json'], output_path=outDir))
        am.analyze()

