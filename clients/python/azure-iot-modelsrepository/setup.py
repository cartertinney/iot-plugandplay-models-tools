# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from setuptools import setup, find_packages

# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure

    try:
        ver = azure.__version__
        raise Exception(
            "This package is incompatible with azure=={}. ".format(ver)
            + 'Uninstall it with "pip uninstall azure".'
        )
    except AttributeError:
        pass
except ImportError:
    pass

with open("README.md", "r") as fh:
    _long_description = fh.read()

setup(
    name="azure-iot-modelsrepository",
    version="0.0.0-preview",
    description="Microsoft Azure IoT Models Repository Library",
    license="MIT License",
    url="https://github.com/Azure/iot-plugandplay-models-tools",
    author="Microsoft Corporation",
    author_email="opensource@microsoft.com",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        # Define sub-dependencies due to pip dependency resolution bug
        # https://github.com/pypa/pip/issues/988
        # ---requests dependencies---
        # requests 2.22+ does not support urllib3 1.25.0 or 1.25.1 (https://github.com/psf/requests/pull/5092)
        "urllib3>1.21.1,<1.26,!=1.25.0,!=1.25.1;python_version!='3.4'",
        # Actual project dependencies
        "requests>=2.22.0",
    ],
    extras_require={":python_version<'3.0'": ["azure-iot-nspkg>=1.0.1"]},
    python_requires=">=3.5, <4",
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "samples",
            "samples.*",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.iot",
        ]
    ),
    zip_safe=False,
)
