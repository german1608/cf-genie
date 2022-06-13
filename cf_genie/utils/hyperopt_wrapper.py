"""
Simple wrapper over MongoDB to store and retrieve trials.
"""

import pickle
from dataclasses import dataclass

from hyperopt import Trials, fmin, space_eval, tpe
from hyperopt.mongoexp import MongoTrials

from cf_genie.utils.read_write_files import write_hyper_parameters


@dataclass
class HyperoptRun:
    best_params_hp: dict
    best_params_evaluated_space: dict
    trials: Trials
    best_model: object


def run_hyperopt(model_fn, search_space, store_in_mongo=True, mongo_exp_key=None, fmin_kwrgs={}):
    """Tiny wrapper over Hyperopt to run a search for the best parameters.

    Args:
    : model_fn : function that returns the loss and model for hyperopt to determine the best parameter.
    : search_space : hyperopt search space object
    : store_in_mongo : boolean, whether to store the trials in MongoDB
    : mongo_exp_key : string, experiment key to associate on the jobs DB

    The model_fn has to be a function that returns a dictionary with the following keys:
    : loss : float, loss value
    : status : string, status of the trial
    : attachments : dictionary, attachments to the trial. You can add any keys here, but the
                    following keys are reserved:
        - model : pickle.dumps(model) object, the model to be stored in the trial
    """

    if store_in_mongo and not mongo_exp_key:
        raise ValueError('If you use mongo trials, you need to specify an `mongo_exp_key` parameter')

    if store_in_mongo:
        trials = MongoTrials('mongo://localhost:27017/cf_genie/jobs', exp_key=mongo_exp_key)
    else:
        trials = Trials()

    kwargs = {
        'algo': tpe.suggest,
        'show_progressbar': True,
        'trials': trials,
        'max_evals': 100,
        **fmin_kwrgs
    }
    print(kwargs)
    best_params = fmin(
        model_fn,
        search_space,
        **kwargs)

    run = HyperoptRun(
        best_params, space_eval(
            search_space, best_params), trials, pickle.loads(
            trials.trial_attachments(
                trials.best_trial)['model']))

    if mongo_exp_key:
        write_hyper_parameters(mongo_exp_key, run.best_params_evaluated_space)
    return run
