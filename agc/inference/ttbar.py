# coding: utf-8

"""
ttbar inference model.
"""

from columnflow.inference import inference_model, InferenceModel, ParameterType


@inference_model
def ttbar_model(self: InferenceModel) -> None:

    #
    # categories
    #

    self.add_category(
        "ge4j_eq1b",
        config_category="ge4j_eq1b",
        config_variable="ht",
        data_from_processes=["wjets", "singlet"],  # fake data
        mc_stats=True,
    )
    self.add_category(
        "ge4j_ge2b",
        config_category="ge4j_ge2b",
        config_variable="trijet_mass",
        data_from_processes=["wjets", "singlet"],  # fake data
        mc_stats=True,
    )

    #
    # processes
    #

    self.add_process(
        "ttbar",
        is_signal=True,
        config_process="tt",
    )
    self.add_process(
        "singlet",
        config_process="st",
    )
    self.add_process(
        "wjets",
        config_process="w",
    )

    #
    # parameters
    #

    # groups
    self.add_parameter_group("experiment")
    self.add_parameter_group("theory")

    # lumi
    lumi = self.config_inst.x.luminosity
    for unc_name in lumi.uncertainties:
        self.add_parameter(
            unc_name,
            type=ParameterType.rate_gauss,
            effect=lumi.get(names=unc_name, direction=("down", "up"), factor=True),
        )
        self.add_parameter_to_group(unc_name, "experiment")

    # jet energy scaling uncertainty
    self.add_parameter(
        "jes",
        process="*",
        type=ParameterType.shape,
        config_shift_source="jes",
    )
    self.add_parameter_to_group("jes", "experiment")

    # jet energy resolution uncertainty
    self.add_parameter(
        "jer",
        process="*",
        type=ParameterType.shape,
        config_shift_source="jes",
    )
    self.add_parameter_to_group("jer", "experiment")

    # theory scale variation
    self.add_parameter(
        "scale",
        process="ttbar",
        type=ParameterType.shape,
        config_shift_source="scale",
    )
    self.add_parameter_to_group("scale", "theory")


@inference_model
def ttbar_model_no_shapes(self: InferenceModel) -> None:
    # same initialization as "ttbar_model" above
    ttbar_model.init_func.__get__(self, self.__class__)()

    # remove all shape parameters
    for category_name, process_name, parameter in self.iter_parameters():
        if parameter.type.is_shape or any(trafo.from_shape for trafo in parameter.transformations):
            self.remove_parameter(parameter.name, process=process_name, category=category_name)
