# coding: utf-8

"""
Producers related to pre-trained ML models.
"""

import os

from columnflow.production import Producer, producer
from columnflow.util import InsertableDict, maybe_import

ak = maybe_import("awkward")


@producer(
    uses={
        "event",
    },
)
def ttbar_ml_score(
    self: Producer,
    events: ak.Array,
    **kwargs,
) -> ak.Array:
    """
    TODO: implement
    """
    return events


@ttbar_ml_score.setup
def ttbar_ml_score_setup(
    self: Producer,
    reqs: dict,
    inputs: dict,
    reader_targets: InsertableDict,
) -> None:
    """
    Custom setup function invoked before chunks are processed.
    """
    from xgboost import XGBClassifier

    self.model_even = XGBClassifier()
    self.model_odd = XGBClassifier()

    model_dir = os.path.expandvars("$AGC_SRC_BASE/analyses/cms-open-data-ttbar/models")
    self.model_even.load_model(os.path.join(model_dir, "model_even"))
    self.model_odd.load_model(os.path.join(model_dir, "model_odd"))
