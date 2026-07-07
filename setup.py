from setuptools import find_packages, setup

setup(
    name="nbstager",
    version="0.1.0",
    description="Jupyter Server extension for staging notebook environment variables and data files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jupyter_server>=2",
        "tornado",
    ],
    data_files=[
        (
            "etc/jupyter/jupyter_server_config.d",
            ["nbstager/etc/jupyter_server_config.d/nbstager.json"],
        ),
    ],
    zip_safe=False,
)
