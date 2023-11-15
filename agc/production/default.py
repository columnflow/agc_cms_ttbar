# coding: utf-8

"""
Column production methods related to higher-level features.
"""

from columnflow.production import Producer, producer
from columnflow.production.categories import category_ids
from columnflow.production.normalization import normalization_weights
from columnflow.util import maybe_import

from agc.production.features import features

np = maybe_import("numpy")
ak = maybe_import("awkward")


@producer(
    uses={features, category_ids, normalization_weights},
    produces={features, category_ids, normalization_weights},
)
def default(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # features
    events = self[features](events, **kwargs)

    # category ids
    events = self[category_ids](events, **kwargs)

    # mc-only weights
    if self.dataset_inst.is_mc:
        # normalization weights
        events = self[normalization_weights](events, **kwargs)

    return events
