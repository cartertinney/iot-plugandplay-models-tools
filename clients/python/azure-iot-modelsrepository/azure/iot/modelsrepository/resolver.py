# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import requests
import logging
import re
import json
import urllib

logger = logging.getLogger(__name__)


REMOTE_PROTOCOLS = ["http", "https", "ftp"]


class ResolverError(Exception):
    pass


def resolve(dtmi, endpoint, expanded=False, resolve_dependencies=False):
    """Retrieve and return the DTDL model(s) corresponding to the given DTMI

    :param str dtmi: DTMI for the desired DTDL
    :param str endpoint: Either a URL or a local filesystem directory where the desired DTDL can
        be found according to the specified DTMI
    :param bool expanded: If True, will retrieve the expanded DTDL instead of the regular one
        (Default - False)
    :param bool resolve_dependencies: If True, will recursively resolve any addtional DTMIs
        for components (and subcomponents) referenced from within the DTDL (Default - False)

    :raises: ValueError if DTMI is invalid
    :raises: :class:`azure.iot.modelsrepository.resolver.ResolverError` if resolution of the DTMI
        at the given endpoint is unsuccessful

    :returns: Dictionary mapping DTMIs to a resolved DTDL (multiple DTMIs possible if using
        full resolution mode)
    :rtype: dict
    """
    fully_qualified_dtmi = get_fully_qualified_dtmi(dtmi, endpoint)

    if expanded:
        fully_qualified_dtmi = fully_qualified_dtmi.replace(".json", ".expanded.json")

    json = _fetch_model(fully_qualified_dtmi)  # this isn't strictly a model if it's expanded?

    # Expanded JSON will be in the form of a list of DTDLs, otherwise will be a singular DTDL.
    # Convert it to a DTDL map
    dtdl_map = {}
    # If using expanded JSON, add an entry to the DTDL map for each DTDL
    if expanded:
        for dtdl in json:
            dtdl_map[dtdl["@id"]] = dtdl
    # If resolving dependencies, will need to fetch component DTDLs
    # NOTE: This is unnecessary if using expanded JSON because expanded JSON already has them
    elif resolve_dependencies:
        dtdl_map[dtmi] = json
        _resolve_dtdl_components(json, dtdl_map, endpoint)
    # Otherwise, just return a one-entry map of the returned JSON (singular DTDL)
    else:
        dtdl_map[dtmi] = json

    return dtdl_map


def get_fully_qualified_dtmi(dtmi, endpoint):
    """Return a fully-qualified path for a DTMI at an endpoint

    E.g:
    dtmi:com:example:Thermostat;1, https://somedomain.com
        -> https://somedomain.com/dtmi/com/example/thermostat-1.json

    :param str dtmi: DTMI to be make fully-qualified
    :param str endpoint: Either a URL or a local filesystem directory that corresponds to the DTMI

    :returns: The fully qualified path for the specified DTMI at the specified endpoint
    :rtype: str
    """
    # NOTE: does this belong in this library?
    # NOTE: does this have the correct name? Is this really a DTMI path, or a DTDL path?
    if not endpoint.endswith("/"):
        endpoint += "/"
    fully_qualified_dtmi = endpoint + _convert_dtmi_to_path(dtmi)
    return fully_qualified_dtmi


def _resolve_dtdl_components(dtdl, dtdl_map, endpoint):
    """Retrieve all components of the provided DTDL from the provided endpoint, and add them
    to the provided DTDL map. This recursively operates on the components as well, if there are
    subcomponents, subsubcompoenents, etc."""
    components = [item for item in dtdl["contents"] if item["@type"] == "Component"]
    for component in components:
        component_dtmi = component["schema"]
        if component_dtmi not in dtdl_map:
            fq_component_dtmi = get_fully_qualified_dtmi(component_dtmi, endpoint)
            component_dtdl = _fetch_model(fq_component_dtmi)
            dtdl_map[component_dtmi] = component_dtdl
            _resolve_dtdl_components(component_dtdl, dtdl_map, endpoint)


def _fetch_model(resource_location):
    """Return JSON from a specified resource location"""
    # Check value of endpoint to determine if URL or local filesystem directory
    parse_result = urllib.parse.urlparse(resource_location)

    if parse_result.scheme in REMOTE_PROTOCOLS:
        # HTTP/HTTPS URL
        json = _fetch_model_from_remote_url(resource_location)
    elif parse_result.scheme == "file":
        # Filesystem URI
        resource_location = resource_location[len("file://") :]
        json = _fetch_model_from_local_file(resource_location)
    elif parse_result.scheme == "" and (resource_location.startswith("/")):
        # POSIX filesystem path
        json = _fetch_model_from_local_file(resource_location)
    elif parse_result.scheme == "" and re.search(
        r"\.[a-zA-z]{2,63}$", resource_location[: resource_location.find("/")]
    ):
        # Web URL with protocol unspecified - default to HTTPS
        resource_location = "https://" + resource_location
        json = _fetch_model_from_remote_url(resource_location)
    elif (
        parse_result.scheme != ""
        and len(parse_result.scheme) == 1
        and parse_result.scheme.isalpha()
    ):
        # Filesystem path using drive letters (e.g. scheme == "C" or "F" or something)
        json = _fetch_model_from_local_file(resource_location)
    else:
        raise ValueError("Unable to identify resource location: {}".format(resource_location))

    return json


def _fetch_model_from_remote_url(url):
    """Return JSON from a specified remote URL"""
    logger.debug("Making GET request to {}".format(url))
    response = requests.get(url)
    logger.debug("Received GET response: {}".format(response.status_code))
    if response.status_code == 200:
        return response.json()
    else:
        raise ResolverError(
            "Failed to resolve DTMI from URL. Status Code: {}".format(response.status_code)
        )


def _fetch_model_from_local_file(file):
    """Return JSON from specified local file"""
    logger.debug("Opening local file {}".format(file))
    try:
        with open(file) as f:
            file_str = f.read()
    except Exception as e:
        raise ResolverError("Failed to resolve DTMI from Filesystem") from e
    return json.loads(file_str)


def _convert_dtmi_to_path(dtmi):
    """Converts a DTMI into a DTMI path

    E.g:
    dtmi:com:example:Thermostat;1 -> dtmi/com/example/thermostat-1.json
    """
    pattern = re.compile(
        "^dtmi:[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?(?::[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?)*;[1-9][0-9]{0,8}$"
    )
    if not pattern.match(dtmi):
        raise ValueError("Invalid DTMI")
    else:
        return dtmi.lower().replace(":", "/").replace(";", "-") + ".json"
