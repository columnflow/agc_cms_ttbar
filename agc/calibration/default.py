# coding: utf-8

"""
Object calibration methods.
"""

from columnflow.calibration import Calibrator, calibrator
from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column, layout_ak_array


np = maybe_import("numpy")
ak = maybe_import("awkward")


@calibrator(
    uses={
        "Jet.pt", "Jet.mass",
    },
    produces={
        "Jet.pt_jes_up", "Jet.pt_jes_down", "Jet.mass_jes_up", "Jet.mass_jes_down",
        "Jet.pt_jer_up", "Jet.pt_jer_down", "Jet.mass_jer_up", "Jet.mass_jer_down",
    },
    # only run on mc datasets
    mc_only=True,
    # special agc case: there is no nominal calibration, so skip on all other shifts
    shifts_only={"nominal", "jes_up", "jes_down", "jer_up", "jer_down"},
)
def jec(self: Calibrator, events: ak.Array, **kwargs) -> ak.Array:
    """
    Fake jet energy (scale + resolution) calibrator.
    Normally, updated nominal values would be added as well, but here we only add varied columns.
    The fake AGC implementation is very trivial though and could therefore be implemented, for
    instance, in the selection itself, but we use a proper calibrator instead to showcase cf.
    """
    flat_pt = ak.flatten(events.Jet.pt, axis=1)
    smearing = layout_ak_array(np.random.normal(np.zeros_like(flat_pt), 0.05), events.Jet.pt)

    for direction, sign in [("up", 1.0), ("down", -1.0)]:
        # jes
        jes_factor = 1 + sign * 0.03
        events = set_ak_column(events, f"Jet.pt_jes_{direction}", events.Jet.pt * jes_factor)
        events = set_ak_column(events, f"Jet.mass_jes_{direction}", events.Jet.mass * jes_factor)

        # jer
        jer_factor = 1 + sign * smearing
        events = set_ak_column(events, f"Jet.pt_jer_{direction}", events.Jet.pt * jer_factor)
        events = set_ak_column(events, f"Jet.mass_jer_{direction}", events.Jet.mass * jer_factor)

    return events


@calibrator(
    shifts=jec.shifts_only,
)
def jec_shifts(self: Calibrator, events: ak.Array, **kwargs) -> ak.Array:
    """
    Empty calibrator that only defines jet energy shifts. It can be declared as a dependency by
    other task array functions to register these shifts.
    """
    return events


@calibrator(
    uses={jec},
    produces={jec},
)
def default(self: Calibrator, events: ak.Array, **kwargs) -> ak.Array:
    """
    Default calibrator.
    """
    if self.dataset_inst.is_mc:
        events = self[jec](events, **kwargs)

    return events
