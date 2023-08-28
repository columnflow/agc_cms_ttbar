# coding: utf-8

"""
Categorizations.
"""


from columnflow.categorization import Categorizer, categorizer
from columnflow.util import maybe_import


ak = maybe_import("awkward")


@categorizer(uses={"event"})
def cat_pre(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    # fully inclusive selection
    return events, ak.ones_like(events.event) == 1


@categorizer(uses={"Jet.pt", "BJet.pt"})
def cat_ge4j_eq1b(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    return events, (
        (ak.num(events.Jet.pt, axis=1) >= 4) &
        (ak.num(events.BJet.pt, axis=1) == 1)
    )


@categorizer(uses={"Jet.pt", "BJet.pt"})
def cat_ge4j_ge2b(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    return events, (
        (ak.num(events.Jet.pt, axis=1) >= 4) &
        (ak.num(events.BJet.pt, axis=1) >= 2)
    )
