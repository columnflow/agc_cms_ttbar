# coding: utf-8

"""
Column production methods related to higher-level features.
"""


from columnflow.production import Producer, producer
from columnflow.production.categories import category_ids
from columnflow.selection.util import create_collections_from_masks
from columnflow.util import maybe_import
from columnflow.columnar_util import EMPTY_FLOAT, Route, set_ak_column, attach_behavior


np = maybe_import("numpy")
ak = maybe_import("awkward")


@producer(
    uses={
        "Jet.pt", "Jet.eta", "Jet.phi", "Jet.mass", "Jet.btagCSVV2",
    },
    produces={
        # new columns
        "ht", "n_jet", "trijet_mass",
    },
)
def features(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # ht and njet
    events = set_ak_column(events, "ht", ak.sum(events.Jet.pt, axis=1))
    events = set_ak_column(events, "n_jet", ak.num(events.Jet.pt, axis=1), value_type=np.int32)

    # trijet mass
    # create all combinations
    triplets = ak.combinations(attach_behavior(events.Jet, "Jet"), 3, fields=["j1", "j2", "j3"])
    # at least one b-tag per combination
    max_btag = np.maximum(
        triplets.j1.btagCSVV2,
        np.maximum(triplets.j2.btagCSVV2, triplets.j3.btagCSVV2),
    )
    triplets = triplets[max_btag >= 0.5]
    # per event, pick the triplet with the maximum pt
    p4 = triplets.j1 + triplets.j2 + triplets.j3
    p4_maxpt = p4[ak.argmax(p4.pt, axis=1, keepdims=True)][:, 0]
    # store the mass
    events = set_ak_column(events, "trijet_mass", p4_maxpt.mass, np.float32)

    return events


@producer(
    uses={
        category_ids,
        # nano columns
        "Jet.pt", "Jet.eta", "Jet.phi",
    },
    produces={
        category_ids,
        # new columns
        "cutflow.jet1_pt",
    },
)
def cutflow_features(
    self: Producer,
    events: ak.Array,
    object_masks: dict[str, dict[str, ak.Array]],
    **kwargs,
) -> ak.Array:
    # apply object masks and create new collections
    reduced_events = create_collections_from_masks(events, object_masks)

    # create category ids per event and add categories back to the
    events = self[category_ids](reduced_events, target_events=events, **kwargs)

    # add cutflow columns
    events = set_ak_column(
        events,
        "cutflow.jet1_pt",
        Route("Jet.pt[:,0]").apply(events, EMPTY_FLOAT),
    )

    return events
