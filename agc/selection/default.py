# coding: utf-8

"""
Event selectors.
"""

from functools import reduce
from operator import and_
from collections import defaultdict

from columnflow.selection import Selector, SelectionResult, selector
from columnflow.selection.util import sorted_indices_from_mask
from columnflow.selection.stats import increment_stats
from columnflow.production.processes import process_ids
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.util import maybe_import

from agc.calibration.default import jec_shifts
from agc.production.features import cutflow_features


np = maybe_import("numpy")
ak = maybe_import("awkward")


#
# unexposed selectors
# (not selectable from the command line but used by other, exposed selectors)
#

@selector(
    uses={"Electron.pt", "Electron.eta", "Electron.cutBased", "Electron.sip3d"},
)
def electron_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # per electron selection
    electron_mask = (
        (events.Electron.pt > 30.0) &
        (np.abs(events.Electron.eta) < 2.1) &
        (events.Electron.cutBased == 4) &
        (events.Electron.sip3d < 4.0)
    )

    return events, SelectionResult(
        objects={
            "Electron": {
                "Electron": sorted_indices_from_mask(electron_mask, events.Electron.pt, ascending=False),
            },
        },
        aux={
            "n_electrons": ak.sum(electron_mask, axis=1),
        },
    )


@selector(
    uses={"Muon.pt", "Muon.eta", "Muon.tightId", "Muon.sip3d", "Muon.pfRelIso04_all"},
)
def muon_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # per muon selection
    muon_mask = (
        (events.Muon.pt > 30.0) &
        (abs(events.Muon.eta) < 2.1) &
        (events.Muon.tightId) &
        (events.Muon.sip3d < 4.0) &
        (events.Muon.pfRelIso04_all < 0.15)
    )

    return events, SelectionResult(
        objects={
            "Muon": {
                "Muon": sorted_indices_from_mask(muon_mask, events.Muon.pt, ascending=False),
            },
        },
        aux={
            "n_muons": ak.sum(muon_mask, axis=1),
        },
    )


@selector(
    uses={"Jet.pt", "Jet.eta", "Jet.jetId", "Jet.btagCSVV2"},
)
def jet_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # per jet selection
    jet_mask = (
        (events.Jet.pt > 30.0) &
        (abs(events.Jet.eta) < 2.4) &
        # the jetId bit at index 2 refers to the tight lepton veto
        ((events.Jet.jetId & (1 << 2)) != 0)
    )

    # additional btag selection
    btag_mask = jet_mask & (events.Jet.btagCSVV2 >= 0.5)

    return events, SelectionResult(
        objects={
            "Jet": {
                "Jet": sorted_indices_from_mask(jet_mask, events.Jet.pt, ascending=False),
                "BJet": sorted_indices_from_mask(btag_mask, events.Jet.pt, ascending=False),
            },
        },
        aux={
            "n_jets": ak.sum(jet_mask, axis=1),
            "n_btags": ak.sum(btag_mask, axis=1),
        },
    )


@selector()
def event_selection(
    self: Selector,
    events: ak.Array,
    results: SelectionResult,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    # lepton selection
    results.steps.lepton = (results.x.n_electrons + results.x.n_muons) == 1

    # jet selection
    results.steps.jet = results.x.n_jets >= 4

    # b-tag selection
    results.steps.btag = results.x.n_btags >= 1

    # combined event selection after all steps
    results.main["event"] = results.steps.lepton & results.steps.jet & results.steps.btag

    return events, results


#
# exposed selectors
# (those that can be invoked from the command line)
#

@selector(
    uses={
        process_ids, mc_weight, electron_selection, muon_selection, jet_selection,
        event_selection, cutflow_features, increment_stats,
    },
    produces={
        process_ids, mc_weight, cutflow_features,
    },
    shifts={
        jec_shifts,
    },
    exposed=True,
)
def default(
    self: Selector,
    events: ak.Array,
    stats: defaultdict,
    **kwargs,
) -> SelectionResult:
    # prepare the selection results that are updated at every step
    results = SelectionResult()

    # add process ids
    events = self[process_ids](events, **kwargs)

    # add the mc weight, potentially corrected based on CMS-specific recommendations
    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)

    # electron selection
    events, electron_results = self[electron_selection](events, **kwargs)
    results += electron_results

    # muon selection
    events, muon_results = self[muon_selection](events, **kwargs)
    results += muon_results

    # jet selection
    events, jet_results = self[jet_selection](events, **kwargs)
    results += jet_results

    # full event selection
    events, results = self[event_selection](events, results, **kwargs)

    # cutflow features
    events = self[cutflow_features](events, results.objects, **kwargs)

    # combined event selection after all steps
    results.event = reduce(and_, results.steps.values())

    # increment stats
    weight_map = {
        "num_events": Ellipsis,
        "num_events_selected": results.event,
    }
    group_map = {}
    if self.dataset_inst.is_mc:
        # sum of mc weight for all events
        weight_map["sum_mc_weight"] = (events.mc_weight, Ellipsis)
        # sum of mc weight for selected events
        weight_map["sum_mc_weight_selected"] = (events.mc_weight, results.event)
        # store all weights per process id
        group_map["process"] = {
            "values": events.process_id,
            "mask_fn": (lambda v: events.process_id == v),
        }
    events, results = self[increment_stats](
        events=events,
        results=results,
        stats=stats,
        weight_map=weight_map,
        group_map=group_map,
        **kwargs,
    )

    return events, results
