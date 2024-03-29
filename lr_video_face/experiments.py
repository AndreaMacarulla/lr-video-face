# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_experiments.ipynb.

# %% auto 0
__all__ = ['Experiment', 'ExperimentalSetup']

# %% ../nbs/02_experiments.ipynb 3
import os
import lir
import numpy as np
from itertools import chain

from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from typing import List, Iterator, Dict, Union, Tuple
from collections import defaultdict

from datetime import datetime

from lir import (LogitCalibrator,
                 NormalizedCalibrator,
                 ELUBbounder,
                 KDECalibrator,
                 FractionCalibrator,
                 IsotonicCalibrator,
                 DummyCalibrator, Xy_to_Xn)

from sql_face.tables import *
from lr_video_face.orm import ScorerModel
from lr_video_face.pairing import get_test_pairs_per_category
from lr_video_face.calibration import (get_calibration_pairs_per_category, 
                                        generate_lr_systems,
                                        predict_lr)

# %% ../nbs/02_experiments.ipynb 5
class Experiment:

    def __init__(self,
        detector: str,
        embeddingModel: str,
        qualityModel: str,
        scorer: BaseEstimator,
        calibrator: BaseEstimator,
        calibration_db: List[str],
        enfsi_years: List[int],
        
        # image_filters: List[str],        
        # face_image_filters: List[str],
        # quality_filters: List[str],
        filters,
        metrics: str,
        n_calibration_pairs: int,
        embedding_model_as_scorer: bool,
        root_output_dir: str,
        session,
        quality_dropout
        
        ):    
    

        self.detector = detector
        self.embeddingModel = embeddingModel
        self.qualityModel = qualityModel
        self.scorer = scorer
        self.calibrator = calibrator
        self.calibration_db = calibration_db
        self.enfsi_years = enfsi_years
        #new
        #self.image_filters = filters['image']
        #self.face_image_filters = filters['face_image']
        #self.quality_filters = filters['quality']
        self.filters = filters

        self.metrics = metrics
        self.n_calibration_pairs = n_calibration_pairs
        self.embedding_model_as_scorer = embedding_model_as_scorer
        self.root_output_dir = root_output_dir
        self.output_dir = self._get_output_dir()
        self.session = session
        self.quality_dropout = quality_dropout


    def _get_output_dir(self):
        if isinstance(self.calibrator, IsotonicCalibrator):
            calibrator = 'Isotonic Calibrator'
        else:
            calibrator = str(self.calibrator)

        if self.embedding_model_as_scorer:
            folder = f'{self.detector}_{self.embeddingModel}(emb=scorer)_{calibrator.split("(")[0]}'
        else:
            folder = f'{self.detector}_{self.embeddingModel}(emb<>scorer)_{calibrator.split("(")[0]}'

        output_dir = os.path.join(self.root_output_dir, folder)
        return output_dir
    
    
    def perform(self) -> Dict[str, float]:
        """
        Function to run a single experiment with pipeline:
        - Fit model on train data
        - Fit calibrator on calibrator data
        - Evaluate test set
        """

        # Create folder
        self.create_output_dir()

        # Get test pairs per category.
        test_pairs_per_category, df_pairs_2015 = get_test_pairs_per_category(self.session, 
                                                            #new                 
                                                            #self.image_filters, 
                                                            #self.face_image_filters, 
                                                            self.filters,

                                                            self.detector, 
                                                            self.embeddingModel,
                                                            self.qualityModel,
                                                            self.enfsi_years,
                                                            self.quality_dropout)
        # Get calibration pair per category.
        calibration_pairs_per_category = get_calibration_pairs_per_category(test_pairs_per_category.keys(),
                                                                            #new
                                                                            #self.image_filters, 
                                                                            #self.face_image_filters,
                                                                            # self.quality_filters,
                                                                            self.filters,

                                                                            self.detector,
                                                                            self.embeddingModel,
                                                                            self.qualityModel,
                                                                            self.calibration_db,
                                                                            self.n_calibration_pairs,
                                                                            self.session)

        # Generate lr_system per category.
        lr_systems, test_pairs_per_category = generate_lr_systems(self.embeddingModel,
                                                                        self.embedding_model_as_scorer,
                                                                        self.metrics,
                                                                        self.scorer,
                                                                        self.calibrator,
                                                                        calibration_pairs_per_category, 
                                                                        test_pairs_per_category,
                                                                        self.session)

        # Predict LR
        results = predict_lr(self.enfsi_years,
                                self.embeddingModel,
                                self.embedding_model_as_scorer,
                                self.metrics,
                                lr_systems, 
                                test_pairs_per_category,
                                df_pairs_2015, 
                                self.session)

        # todo: make necessary variables for graphs.
        return results

   
    def create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


    def __str__(self):
        """
        Converts the configuration of this experiment to a string that can be
        used to generate file names for example.
        """
        data_values = []
        for k, v in self.data_config.items():
            if k == 'datasets' and isinstance(v, tuple):
                data_values.append('|'.join(map(str, v)))

            elif k == 'filters':  
                #todo: crear string con los filtros  
                a=0
            else:
                data_values.append(str(v))

        params_str = '_'.join(map(str, self.params.values()))
        return '_'.join(map(str, [
            self.scorer,
            self.calibrator,
            params_str
        ])).replace(':', '-')  # Windows forbids ':'

        return None

# %% ../nbs/02_experiments.ipynb 7
class ExperimentalSetup:
    def __init__(self, 
                detectors, 
                embeddingModels, 
                qualityModels,
                calibrator_names, 
                calibration_db, 
                enfsi_years, 
                filters,
                metrics, 
                n_calibration_pairs, 
                embedding_model_as_scorer,
                results_folder:str,
                session,
                quality_dropout = [1],
                name:datetime = datetime.now().strftime("%Y-%m-%d %H %M %S")
                ):

        self.detectors = detectors
        self.embeddingModels = embeddingModels
        self.qualityModels = qualityModels
        self.calibrators = self._get_calibrators(calibrator_names)
        self.calibration_db = calibration_db
        self.enfsi_years = enfsi_years
        self.filters = filters
        self.metrics = metrics
        self.n_calibration_pairs = n_calibration_pairs
        self.embedding_model_as_scorer = embedding_model_as_scorer
        self.session = session
        
        self.quality_dropout = quality_dropout
        self.name = name
        self.output_dir= self._make_output_dir(results_folder)
        self.experiments = self.prepare_experiments()
        self.cllr_expert_per_year = self._get_cllr_expert_per_year()


    @staticmethod
    def _get_calibrators(calibrator_names: List[str]) \
            -> List[BaseEstimator]:
        """
        Parses a list of CALIBRATORS configuration names and returns the
        corresponding calibrators. 
        :param calibrator_names: List[str]
        :return: List[ScorerModel]
        """
        CALIBRATORS = {
            'logit': LogitCalibrator(),
            'logit_normalized': NormalizedCalibrator(LogitCalibrator()),
            'KDE': KDECalibrator(),
            'elub_KDE': ELUBbounder(KDECalibrator()),
            'fraction': FractionCalibrator(),
            'isotonic': IsotonicCalibrator(add_misleading=1)
        }  
        # todo: isotonic needs repr method. Could create an instance with one.
        return [CALIBRATORS[c] for c in calibrator_names]

    
    def _get_directory(self):
        #filters = self.image_filters + self.face_image_filters # + self.quality_filters
        
        filterlist = list(chain.from_iterable(self.filters.values()))

        subfolder = f'[{",".join(filterlist)}]'
        folder = f'C_({self.n_calibration_pairs})_[{",".join(self.calibration_db)}]_T_[{",".join([str(year) for year in self.enfsi_years])}]'
        return os.path.join(folder, subfolder)

    def _make_output_dir(self, results_folder):
        directory = self._get_directory()
        output_dir = os.path.join(results_folder, directory)
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        return output_dir


     
    def _get_cllr_expert_per_year(self):
        session = self.session
        expert_eval = session.query(EnfsiImage.year, EnfsiPair.same, EnfsiPair.ExpertsLLR) \
            .filter(EnfsiImage.image_id == EnfsiPair.second_id,
                    EnfsiImage.year.in_(self.enfsi_years)) \
            .all()        

        y_test_per_year = defaultdict(list)
        LLR_experts_per_year = defaultdict(list)

        for year, y, LLR_expert in expert_eval:
            y_test_per_year[year].append(y)
            LLR_experts_per_year[year].append(LLR_expert)

        cllr_experts_per_year = defaultdict(list)

        for year in self.enfsi_years:
            LLR_experts = np.asarray(LLR_experts_per_year[year])
            for i, expert in enumerate(LLR_experts.T):
                # todo: overflow bug with np.power(10, expert) for year 2017.
                LR_expert = np.asarray([np.power(10, i) for i in expert])
                cllr_expert = lir.metrics.cllr(LR_expert,
                                               np.asarray(y_test_per_year[year]))
                cllr_experts_per_year[year].append(cllr_expert)

        return cllr_experts_per_year

    


    def prepare_experiments(self) -> List[Experiment]:
        """
        Returns a list of all experiments that fall under this setup.

        :return: List[Experiment]
        """
        experiments = []
        for detector in self.detectors:
            for embeddingModel in self.embeddingModels:
                for qualityModel in self.qualityModels:
                    for calibrator in self.calibrators:
                        if self.embedding_model_as_scorer:
                            scorer = ScorerModel(metric=self.metrics, embeddingModel=embeddingModel)
                        else:
                            scorer = LogisticRegression(solver='lbfgs')
                        experiments.append(Experiment(
                            detector,
                            embeddingModel,
                            qualityModel,
                            scorer,
                            calibrator,
                            self.calibration_db,
                            self.enfsi_years,
                            self.filters,
                            self.metrics,
                            self.n_calibration_pairs,
                            self.embedding_model_as_scorer,
                            self.output_dir,
                            self.session,
                            self.quality_dropout                            
                    ))

        return experiments

    def __iter__(self) -> Iterator[Experiment]:
        return iter(self.experiments)

    def __len__(self) -> int:
        return len(self.experiments)    
