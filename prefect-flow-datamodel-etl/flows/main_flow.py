import glob
import time

import requests
from prefect import flow, task
from prefect.blocks.system import Secret
from tusclient import client

 ## TODO: use triply Prefect task from prefect_meemoo (in PR)


@flow(name="prefect_flow_datamodel_etl")
def main_flow():
    """
    Here you write your main flow code and call your tasks and/or subflows.
    """
    # This loops over all turtle files in the directory
    for file in glob.glob("*/*.ttl"):
        # Do the task
        pass
    
if __name__ == "__main__":
    main_flow()