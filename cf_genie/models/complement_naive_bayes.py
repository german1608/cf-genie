"""
Complemeent naive bayes sklearn wrapper.

Complement naive bayes (CNB) is a veresion of MNB that is supposed to work well with imbalanced data
"""
import pickle
from typing import List

from hyperopt import STATUS_OK, hp
from sklearn.naive_bayes import ComplementNB

import cf_genie.logger as logger
import cf_genie.utils as utils
from cf_genie.models.base import BaseSupervisedModel
from cf_genie.utils.timer import Timer

logger.setup_applevel_logger(
    is_debug=False, file_name=__file__, simple_logs=True)


log = logger.get_logger(__name__)

SEARCH_SPACE = {
    'alpha': hp.uniform('alpha', 0.0, 1.0),
}


def objective(docs, labels, model_name):
    def wrapped(params):
        log.info('Training MNB with params: %s', params)
        model = ComplementNB(**params)

        with Timer(f'Training {model_name} model', log=log):
            model.fit(docs, labels)

        return {
            'loss': -model.score(docs, labels),
            'status': STATUS_OK,
            'attachments': {
                'model': pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
            }
        }
    return wrapped


class ComplementNaiveBayes(BaseSupervisedModel):
    def train(self):
        model_path = utils.get_model_path(f'{self.model_name}.bin')
        try:
            with open(model_path, 'rb') as f:
                model: ComplementNB = pickle.load(f)
                log.info(f'{self.model_name} model loaded from disk')
        except BaseException:
            log.info('Model not stored. Building MNB model from scratch using hyper-parameterization')
            with Timer(f'{self.model_name} hyper-parameterization', log=log):
                hyperopt_info = utils.run_hyperopt(
                    objective(
                        self._docs_to_train_models,
                        self._labels,
                        self.model_name),
                    SEARCH_SPACE,
                    mongo_exp_key=self._model_name,
                    fmin_kwrgs={
                        'max_evals': 40})
                model: ComplementNB = hyperopt_info.best_model

        self.model = model
        pass

    def predict(self, doc) -> List[str]:
        return self.model.predict(doc)

    def training_score(self) -> float:
        return self.model.score(self._docs_to_train_models, self._labels)