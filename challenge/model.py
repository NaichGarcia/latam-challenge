import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import confusion_matrix, classification_report

from sklearn.linear_model import LogisticRegression

import xgboost as xgb

from typing import Tuple, Union, List

class CustomFeature:

    def __init__(self):
        pass

    @staticmethod
    def get_period_day(date):
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("4:59", '%H:%M').time()
        
        if(date_time > morning_min and date_time < morning_max):
            return 'mañana'
        elif(date_time > afternoon_min and date_time < afternoon_max):
            return 'tarde'
        elif(
            (date_time > evening_min and date_time < evening_max) or
            (date_time > night_min and date_time < night_max)
        ):
            return 'noche'

    @staticmethod
    def is_high_season(fecha):
        fecha_año = int(fecha.split('-')[0])
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
        range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
        range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
        range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
        range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
        range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
        range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
        range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
        
        if ((fecha >= range1_min and fecha <= range1_max) or 
            (fecha >= range2_min and fecha <= range2_max) or 
            (fecha >= range3_min and fecha <= range3_max) or
            (fecha >= range4_min and fecha <= range4_max)):
            return 1
        else:
            return 0
    
    @staticmethod
    def get_min_diff(data):
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = ((fecha_o - fecha_i).total_seconds())/60
        return min_diff

class DelayModel:

    def __init__(
        self
    ):
        self._model = None

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """

        # Get "delay" values
        data['min_diff'] = data.apply(CustomFeature.get_min_diff, axis = 1)
 
        threshold_in_minutes = 15
        data['delay'] = np.where(data['min_diff'] > threshold_in_minutes, 1, 0)

        # Process features
        training_data = shuffle(
            data[['OPERA', 'MES', 'TIPOVUELO', 'SIGLADES', 'DIANOM', 'delay']], 
            random_state = 111
        )

        features = pd.concat([
            pd.get_dummies(training_data['OPERA'], prefix = 'OPERA'),
            pd.get_dummies(training_data['TIPOVUELO'], prefix = 'TIPOVUELO'), 
            pd.get_dummies(training_data['MES'], prefix = 'MES')], 
            axis = 1
        )

        # Top 10 features according to the DS
        top_10_features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]
        features = features[top_10_features]

        if(target_column):
            target = training_data[[target_column]].copy()
            return (features, target)

        return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
         
        x_train, _, y_train, _ = train_test_split(
            features, 
            np.ravel(target), 
            test_size=0.33, 
            random_state=42
        )
        
        # Data Balance
        n_y0 = len(y_train[y_train == 0])
        n_y1 = len(y_train[y_train == 1])
        scale = n_y0/n_y1

        # Fit Model
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight=scale)
        self._model.fit(x_train, y_train)

        self._model.save_model("model.json")
        
        return

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """

        # Checks if the model is already trained
        if(self._model is None):
            try:
                self._model = xgb.XGBClassifier()
                self._model.load_model("model.json")
            except:
                raise ValueError("El modelo aún no es entrenado")

        predicted_targets = self._model.predict(features)
        predicted_targets = predicted_targets.tolist()

        return predicted_targets