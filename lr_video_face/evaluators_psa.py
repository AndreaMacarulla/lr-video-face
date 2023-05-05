# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_evaluators.ipynb.

# %% auto 0
__all__ = ['ExperimentEvaluator', 'GlobalEvaluator']

# %% ../nbs/05_evaluators.ipynb 3
import os
from typing import List, Iterator, Dict, Union, Tuple, Optional
import lir
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from tqdm import tqdm
from collections import defaultdict
from statistics import mean

from lr_video_face.experiments import Experiment, ExperimentalSetup
from lr_video_face.plots import *



# %% ../nbs/05_evaluators.ipynb 4
class ExperimentEvaluator:
    def __init__(self, 
    experiment: Experiment,
    cllr_expert_per_year: Dict[int, list],
    results: Dict[str, list],
    save_plots: bool = True
    ):

        self.experiment = experiment
        self.cllr_expert_per_year = cllr_expert_per_year
        self.results = results
        self.save_plots = save_plots

        self.experiment_directory = self.experiment.output_dir
        self.years = [pair.first.year for pair in self.results["test_pairs"]]

        
        self.cllr_auto_per_year = self.get_cllr_auto_per_year()
        self.results_2015 = self._get_results_2015(self.results, self.years)
        self.drop_zero_results = self._get_drop_zero_results(self.results)
        self.cllrs_2015 = self._get_cllrs_2015(self.results_2015)
    

    def make_plots(self):
        #if 2015 in self.experiment.enfsi_years:

        df = pd.DataFrame({'Results':self.drop_zero_results})
        df.to_pickle(os.path.join(self.experiment_directory,'drop_zero_results.pd'))

        plot_lr_distributions(self.drop_zero_results, self.experiment_directory, self.save_plots)
        plot_ROC_curve(self.drop_zero_results, self.experiment_directory, self.save_plots)
        plot_tippett(self.drop_zero_results, self.experiment_directory, self.save_plots)
        plot_ece(self.drop_zero_results, self.experiment_directory, self.save_plots)
        plot_cllr(self.drop_zero_results, self.experiment_directory, self.experiment.enfsi_years, 
            self.cllr_expert_per_year, self.cllr_auto_per_year, self.experiment.embeddingModel, self.save_plots)

        if 2015 in self.years:
            plot_cllr_per_qualitydrop(self.cllrs_2015, self.cllr_expert_per_year, self.experiment_directory, self.save_plots)
            plot_cllr_per_common_attributes(self.results_2015, self.cllr_expert_per_year, self.experiment_directory, self.save_plots)

            plot_new(self.results_2015, self.cllr_expert_per_year, self.experiment_directory, self.save_plots)
    
    
    
    
    @staticmethod
    def _get_drop_zero_results(results:Dict[str, list])->Dict[str, list]:
        drop_zero_results = {}
        dropouts = results["quality_drops"]

        for key, values in results.items():
            drop_zero_results[key] = [value for value, dropout \
                                        in zip(values, dropouts)\
                                        if dropout == 1 ]

        #incluimos las imagenes promedio como dropout = 1
        for key in ["lrs_predicted_2015","y_test_2015"]:
            drop_zero_results[key] = results[key] 
            
        return drop_zero_results

    @staticmethod
    def _get_results_2015(results:Dict[str, list], years:List[int])->Dict[str, list]:
        results_2015 = {}
        for key, values in results.items():
            results_2015[key] = [value for value, year \
                                        in zip(values, years)\
                                        if year == 2015]

        #incluimos las imagenes promedio 
        for key in ["lrs_predicted_2015","y_test_2015"]:
            results_2015[key] = results[key] 
        return results_2015


    def get_cllr_auto_per_year(self):
        # years = [pair.first.year for pair in self.results["test_pairs"]]
        lrs_predicted = self.results["lrs_predicted"]
        y_test = self.results["y_test"]

        data_per_year = zip(self.years, lrs_predicted, y_test)

        lrs_predicted_per_year = defaultdict(list)
        y_test_per_year = defaultdict(list)

        for year, lr, y in data_per_year:
            lrs_predicted_per_year[year].append(lr)
            y_test_per_year[year].append(y)

        cllr_auto_per_year = {}

        for year in np.unique(self.years):
            cllr_auto_per_year[year] = lir.metrics.cllr(np.asarray(lrs_predicted_per_year[year]),
                                                        np.asarray(y_test_per_year[year]))

        return cllr_auto_per_year

    
    @staticmethod
    def _get_cllrs_2015(results_2015:Dict[str, list])->Dict[float, float]:

        lrs_predicted = results_2015["lrs_predicted"]
        y_test = results_2015["y_test"]
        dropouts = results_2015["quality_drops"]

        data_per_dropout = zip(dropouts, lrs_predicted, y_test)

        lrs_predicted_per_dropout = defaultdict(list)
        y_test_per_dropout = defaultdict(list)
        
        for dropout, lr, y in data_per_dropout:
            lrs_predicted_per_dropout[dropout].append(lr)
            y_test_per_dropout[dropout].append(y)


        cllr_per_dropout = {}

        for dropout in set(dropouts):
            cllr_per_dropout[dropout] = lir.metrics.cllr(np.asarray(lrs_predicted_per_dropout[dropout]),
                                                        np.asarray(y_test_per_dropout[dropout]))
        
        return cllr_per_dropout


# %% ../nbs/05_evaluators.ipynb 5
class GlobalEvaluator:

    def __init__(self, 
    experiments: ExperimentalSetup,
    save_plots: bool = True
    ):

        self.experiments = experiments
        self.save_plots = save_plots
        self.experiment_evaluators = self.get_experiment_evaluators(self.experiments)

    
    @staticmethod
    def get_experiment_evaluators(experiments: ExperimentalSetup) -> List[ExperimentEvaluator]:
        evaluators = []
        for experiment in tqdm(experiments):
            results = experiment.perform()
            evaluation = ExperimentEvaluator(experiment=experiment, results=results, cllr_expert_per_year=experiments.cllr_expert_per_year)
            evaluators.append(evaluation)
        return evaluators

    def make_experiment_plots(self):
        for evaluator in self.experiment_evaluators:
            evaluator.make_plots()


    def make_global_plot(self):
        experiment_df = pd.DataFrame(
            columns=['Year', 'Filters', 'Detector', 'Embedding Model', 'Calibrator', 'Cllr'])
        filters = self.experiments.image_filters + self.experiments.face_image_filters
        str_filters = ",".join(filters)
        for evaluator in self.experiment_evaluators:

            if isinstance(evaluator.experiment.calibrator, lir.IsotonicCalibrator):
                calibrator_name = 'Isotonic Calibrator'
            else:
                calibrator_name = str(evaluator.experiment.calibrator)

            for year in evaluator.experiment.enfsi_years:
                experiment_df = experiment_df.append(
                    {'Year': year, 'Filters': str_filters, 'Detector': evaluator.experiment.detector,
                     'Embedding Model': evaluator.experiment.embeddingModel,
                     'Calibrator': calibrator_name.split("(")[0],
                     'Cllr': evaluator.cllr_auto_per_year[year],
                     }, ignore_index=True)

        for year in self.experiments.enfsi_years:
            for detector in self.experiments.detectors:
                for calibrator in self.experiments.calibrators:

                    if isinstance(calibrator, lir.IsotonicCalibrator):
                        calibrator_name = 'Isotonic Calibrator'
                    else:
                        calibrator_name = str(calibrator)

                    experiment_df = experiment_df.append(
                        {'Year': year, 'Filters': str_filters, 'Detector': detector,
                         'Embedding Model': "Average Participants",
                         'Calibrator': calibrator_name.split("(")[0],
                         'Cllr': mean(self.experiments.cllr_expert_per_year[year])
                         }, ignore_index=True)

        experiment_df.to_excel(os.path.join(self.experiments.output_dir,
                                             f'results_file_ES{self.experiments.embedding_model_as_scorer}.xlsx'))

        sns.set_style("whitegrid")
        sns.catplot(data=experiment_df, x="Year", y="Cllr", hue="Embedding Model", row="Calibrator", col="Detector")
        savefig = os.path.join(self.experiments.output_dir,
                               f"cllr_summary_ES{self.experiments.embedding_model_as_scorer}")
        plt.savefig(savefig)
        plt.close() 

        #Esto es lo nuevo

        df0 = pd.DataFrame()
        for evaluator in self.experiment_evaluators:

            if isinstance(evaluator.experiment.calibrator, lir.IsotonicCalibrator):
                calibrator_name = 'Isotonic Calibrator'
            else:
                calibrator_name = str(evaluator.experiment.calibrator)

            df0 = df0.append({'Detector': evaluator.experiment.detector,
                        'Embedding Model': evaluator.experiment.embeddingModel,
                        'Quality Model': evaluator.experiment.qualityModel,
                        'Calibrator': calibrator_name.split("(")[0],
                        'Results': evaluator.results_2015,
                        'Cllr': evaluator.cllr_expert_per_year[2015]}, ignore_index=True)
                        
        datosgraph = os.path.join(self.experiments.output_dir,'datosgraph.pd')
        df0.to_pickle(datosgraph, compression='infer', protocol=5, storage_options=None)
        #Para ajustar el programa con datos grabados.
        #pandas.read_pickle(filepath_or_buffer, compression='infer', storage_options=None)

        if len(pd.unique(df0.Detector)) == 1 and len(pd.unique(df0.Calibrator)) == 1:

            rows = list(pd.unique(df0['Embedding Model']))
            cols = list(pd.unique(df0['Quality Model']))

            #generamos la gráfica con subplots
            fig,ax = plt.subplots(nrows = len(rows), ncols = len(cols), squeeze= False, figsize= (16,14))
            
            for index, df1 in df0.iterrows():

                row = rows.index(df1['Embedding Model'])
                col = cols.index(df1['Quality Model'])

                ax1 = ax[row][col]
                subplot_new(ax1,df1.Results, df1.Cllr)
                ax1.set_title ( f"Quality Model: {df1['Quality Model']}")                
                ax1.set(ylabel= f"Embedding Model: {df1['Embedding Model']}\n Cllr")
            plt.suptitle('$C_{llr}$ Values')
            fig.tight_layout()
           

            savefig = os.path.join(self.experiments.output_dir, f"cllr_summary_methods{self.experiments.embedding_model_as_scorer}")
            plt.savefig(savefig, dpi= 600)
            plt.close()                


