from enum import Enum, auto
from typing import Type

import numpy as np

import cf_genie.logger as logger
from cf_genie.embedders import EMBEDDERS
from cf_genie.embedders.base import BaseEmbedder
from cf_genie.models import BaseSupervisedModel
from cf_genie.models.base import TrainingMethod
from cf_genie.utils import Timer

log = logger.get_logger(__name__)


def all_strategy(model_class: Type[BaseSupervisedModel], embedder_class: Type[BaseEmbedder], y: np.ndarray):
    with Timer(f'Training {model_class.__name__} on embedder {embedder_class.__name__}'):

        model = model_class(
            embedder_class.read_embedded_words,
            y,
            TrainingMethod.GRID_SEARCH_CV,
            label='with-' +
            embedder_class.__name__ +
            '-on-all-classes')


def one_vs_all(model_class: Type[BaseSupervisedModel], embedder_class: Type[BaseEmbedder], y: np.ndarray):
    for tag_group in np.unique(y):
        non_tag_group = f'NON_{tag_group}'
        y_tag_group = np.vectorize(lambda x: tag_group if x == tag_group else non_tag_group)(y)
        log.info(np.unique(y_tag_group))
        with Timer(f'Training model {model_class.__name__} with embedder {embedder_class.__name__} on tag group {tag_group} vs others', log=log):
            model_class(
                embedder_class.read_embedded_words,
                y_tag_group,
                TrainingMethod.GRID_SEARCH_CV,
                label=f'with-{embedder_class.__name__}-on-{tag_group}-vs-rest-classes')

        with Timer(f'Training model {model_class.__name__} with embedder {embedder_class.__name__} on all classes except {tag_group} data', log=log):
            y_not_tag_group = y != tag_group

            def get_x():
                X = embedder_class.read_embedded_words()
                return X[y_not_tag_group]
            model_class(
                get_x,
                y[y_not_tag_group],
                TrainingMethod.GRID_SEARCH_CV,
                label=f'with-{embedder_class.__name__}-without-{tag_group}-class')


class RunStrategy(Enum):
    ALL = auto()
    ONE_VS_ALL = auto()
    # UNDERSAMPLING = auto()


def run_model(model_class: Type[BaseSupervisedModel], y: np.ndarray, run_strategy: RunStrategy):
    """
    Run a model in all possible embedders
    """
    if RunStrategy.ALL == run_strategy:
        fun = all_strategy
    elif RunStrategy.ONE_VS_ALL == run_strategy:
        fun = one_vs_all
    else:
        raise NotImplementedError(run_strategy.__str__())
    for embedder in EMBEDDERS:
        with Timer(f'Training {model_class.__name__} on embedder {embedder.__name__}'):
            fun(model_class, embedder, y)
