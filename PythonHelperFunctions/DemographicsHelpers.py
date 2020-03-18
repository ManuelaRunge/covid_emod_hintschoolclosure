import numpy as np
import math
import scipy.sparse        as sp
import scipy.sparse.linalg as la
import pandas as pd
from copy import deepcopy
from dtk.tools.demographics.Node import Node
from dtk.tools.demographics.DemographicsFile import DemographicsFile
from scipy.linalg import block_diag





def SetAgeDistribution(demoFile, surveyFile):

    df = pd.read_csv(surveyFile)
    df.drop(labels=['Unnamed: 0', 'name', 'Total'], axis=1, inplace=True)
    ds = df.sum(axis=0)
    ds = (ds/ds.sum()).cumsum()

    EMODAgeBins = [5*i for i in range(len(ds)+1)]

    EMODAgeDist = [0, *(ds.values)]
    demoFile.content['Defaults']['IndividualAttributes'].update(
        {"AgeDistribution": {
            "NumDistributionAxes": 0,
            "ResultUnits": "years",
            "ResultScaleFactor": 365,
            "ResultValues": EMODAgeBins,
            "DistributionValues": EMODAgeDist
            }
        })
    for key in ['AgeDistributionFlag', 'AgeDistribution1', 'AgeDistribution2']:
        demoFile.content['Defaults']['IndividualAttributes'].pop(key, None)

    return demoFile

def TransmissionMatrixFromAgeContactMatrix(filename):
    df = pd.read_excel(filename, sheet_name='United States of America', header=None)
    return np.array(df.values.tolist())

def SetPropertyDependentTransmission(demoFile,
                          TransmissionMatrix_pre, TransmissionMatrix_post, Time_start=40, Duration=2000):
    agedistbins = demoFile.content['Defaults']['IndividualAttributes']['AgeDistribution']['ResultValues'][:-3]
    agedistvals = np.diff(demoFile.content['Defaults']['IndividualAttributes']['AgeDistribution']['DistributionValues'][:-2]).tolist()
    agedistvals[len(agedistvals)-1]=1-sum(agedistvals[:-1])
    propvals = [str(i) + "_" + str(i + 4) + "_pre" for i in agedistbins]
    transitions = []
    for property in propvals:
        transitions.append({"From": property,
                            "To": property.replace("pre", "post"),
                            "Type": "At_Timestep",
                            "Coverage": 1,
                            "Timestep_Restriction": {
                                "Start": Time_start
                            },
                            "Age_In_Years_Restriction": {},
                            "Probability_Per_Timestep": 1,
                            "Timesteps_Until_Reversion": Duration
        })

    propvals = propvals + ([str(i) + "_" + str(i + 4) + "_post" for i in agedistbins])
    TransmissionMatrix = block_diag(TransmissionMatrix_pre, TransmissionMatrix_post)

    demoFile.content['Defaults']['IndividualProperties']= [{
        "Property": "Geographic",
        "Values": propvals,
        "Initial_Distribution": agedistvals+[0]*len(agedistvals),
        "Transitions": transitions,
        "TransmissionMatrix": {
            "Route": "Contact",
            "Matrix": TransmissionMatrix.tolist()
        }
    }]

    return demoFile


