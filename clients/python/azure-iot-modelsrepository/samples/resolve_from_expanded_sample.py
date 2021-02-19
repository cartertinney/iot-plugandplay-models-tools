# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.iot.modelsrepository import resolver
import pprint

repository_endpoint = "https://devicemodels.azure.com"
dtmi = "dtmi:com:example:TemperatureController;1"


# This API call will return a dictionary mapping DTMIs to corresponding DTDLs for all elements
# of a .expanded.json file at the specified endpoint
# i.e. https://devicemodels.azure.com/dtmi/com/example/temperaturecontroller-1.expanded.json
a = resolver.resolve(dtmi, repository_endpoint, resolve_dependencies=resolver.DEPENDENCY_MODE_TRY_FROM_EXPANDED)
pprint.pprint(a)
