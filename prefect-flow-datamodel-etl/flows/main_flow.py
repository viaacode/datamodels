import glob
import time

import requests
from prefect import flow, task
from prefect.blocks.system import Secret
from tusclient import client


@task(name="TUS upload")
def tusk_upload(accountname, dataset, file_name):
    time.sleep(10)
    # Accountname and dataset where the data needs to be uploaded to:
    # accountname = 'lennert'
    # dataset = 'PrefectOrganisations'
    # file_name = 'result.ttl'
    api_url = 'https://api.meemoo.triply.cc'

    token = Secret.load("triplydb-token").get()
    
    # The basic JOBS URL
    url = f'{api_url}/datasets/{accountname}/{dataset}/jobs'

    # Authorization header. 
    auth = {'Authorization': f'Bearer {token}'}

    # First we need to create a Job. A job is the location where we upload the data to and start the process for inserting it in TriplyDB.
    job = requests.post(url, json = {'type': 'upload', 'graphNames': ["schema"]}, headers=auth)
    print(job.json())
    jobId = job.json()["jobId"]

    # Each Job has a specific jobId and jobId url.
    jobUrl = f'{api_url}/datasets/{accountname}/{dataset}/jobs/{jobId}'
    # Set Authorization headers if it is required by the tus server.
    tus_client = client.TusClient(f'{jobUrl}/add', headers=auth)

    # A file stream may also be passed in place of a file path.
    with open(file_name, 'rb') as fs:

        # This is the actual upload of the file to TriplyDB. We use TUS for uploading files/data to TriplyDB. See `https://tus.io/` for all different clients.
        uploader = tus_client.uploader(file_stream=fs, chunk_size=5 * 1024 * 1024, metadata= {'filename': file_name})
        uploader.upload()

        # Once all the data has been uploaded to the server it is time to start the job to import the data.
        requests.post(f'{jobUrl}/start', headers=auth)
        while True:
            status = requests.get(f'{jobUrl}/', headers=auth)
            indexStatus = status.json()['indexingProgress']
            if indexStatus >= 100:
                break
            time.sleep(2)


@flow(name="prefect_flow_datamodel_etl")
def main_flow():
    """
    Here you write your main flow code and call your tasks and/or subflows.
    """
    for file in glob.glob("*/*.ttl"):
        print(file)
        try:
            tusk_upload("lennert", "schema", file)
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    main_flow()