# coding: utf-8

"""
Selectors that define categories.
"""


from columnflow.selection import Selector, selector
from columnflow.util import maybe_import


ak = maybe_import("awkward")


@selector(uses={"event"})
def sel_pre(self: Selector, events: ak.Array, **kwargs) -> ak.Array:
    # fully inclusive selection
    return ak.ones_like(events.event) == 1


@selector(uses={"Jet.pt", "BJet.pt"})
def sel_ge4j_eq1b(self: Selector, events: ak.Array, **kwargs) -> ak.Array:
    return (
        (ak.num(events.Jet.pt, axis=1) >= 4) &
        (ak.num(events.BJet.pt, axis=1) == 1)
    )


@selector(uses={"Jet.pt", "BJet.pt"})
def sel_ge4j_ge2b(self: Selector, events: ak.Array, **kwargs) -> ak.Array:
    return (
        (ak.num(events.Jet.pt, axis=1) >= 4) &
        (ak.num(events.BJet.pt, axis=1) >= 2)
    )
