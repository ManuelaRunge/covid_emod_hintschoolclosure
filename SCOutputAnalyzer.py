from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
import pickle, os


class SCOutputAnalyzer(BaseAnalyzer):
    def __init__(self, filenames = None, output_path=None):
        super().__init__(filenames=filenames)
        self.output_path = output_path or "output"

    def select_simulation_data(self, data, simulation):
        # Apply is called for every simulations included into the experiment
        # We are simply storing the population data in the pop_data dictionary
        selected_data = {}
        selected_data['insetChart'] = data[self.filenames[0]]
        selected_data['sim_id'] = simulation.id
        if simulation.tags.get('__sample_index__') is not None:
            selected_data['sample'] = simulation.tags.get('__sample_index__')
        else:
            selected_data['sample'] = simulation.id
        selected_data['tags'] = simulation.tags
        selected_data['propertyReport'] = data[self.filenames[1]]
        return selected_data

    def finalize(self, all_data):
        with open(os.path.join(self.output_path, 'results.pkl'), 'wb') as pklfile:
            pickle.dump(all_data, pklfile)


# This code will analyze the latest experiment ran with the PopulationAnalyzer
if __name__ == "__main__":
    am = AnalyzeManager('latest', analyzers=SCOutputAnalyzer())
    am.analyze()
