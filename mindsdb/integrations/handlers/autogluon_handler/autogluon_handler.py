from typing import Dict
import pandas as pd
from typing import Optional
import logging
import dill
from mindsdb.integrations.libs.base import BaseMLEngine
from autogluon.tabular import TabularDataset, TabularPredictor

class AutoGluonHandler(BaseMLEngine):
    name = 'autogluon'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_path = 'mindsdb-predict'

    def create(self, target: str, df: Optional[pd.DataFrame] = None, args=None, **kwargs) -> None:
        if 'using' in args:
            args = args['using']
        if 'target' in args:
            target = args['target']
        else:
            args['target'] = target

        try:
            model_name = args['model_name']
        except KeyError:
            model_name = 'default'

        # specifies folder to store trained models
        predictor = TabularPredictor(label=args['target'], path=self.save_path).fit(df)

        ###### persist changes to handler folder
        self.model_storage.json_set("model_args", args)
        self.model_storage.file_set("training_df", dill.dumps(df))

    def predict(self, df: pd.DataFrame, args: Optional[Dict] = None) -> pd.DataFrame:
        logging.debug('Predict!')
        args = self.model_storage.json_get('args')
        predictor = TabularPredictor.load(self.save_path)
        y_pred = predictor.predict(df)
        return pd.DataFrame(y_pred)

    def update(self, df: Optional[pd.DataFrame] = None, args: Optional[Dict] = None) -> None:
        logging.debug('Update!')

    def describe(self, attribute: Optional[str] = None) -> pd.DataFrame:
        args = self.model_storage.json_get('args')
        logging.debug('Describe!')
        return pd.DataFrame([[args]], columns=['model_args'])

    def create_engine(self, connection_args: dict):
        logging.debug('Create engine!')
