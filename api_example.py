from cxone_api import AuthUS, ApiUS, paged_api, CxOneClient
from cxone_api.repo import download_files_to_directory
import os, asyncio


async def main():
    cxone_client = CxOneClient.create_with_oauth(os.environ["OAUTH_CLIENTID"], os.environ["OAUTH_CLIENTSECRET"], "CxOneAPIExample",
        AuthUS(os.environ["TENANT"]), ApiUS(), ssl_verify=False, proxy = {"http" : "http://localhost:8080", "https" : "http://localhost:8080"})

    # print ((await cxone_client.get_repostore_project_tree("153a99d4-686e-4fe9-970d-c68b5d0f83c7")).json())   

    # print((await cxone_client.get_repostore_folder("153a99d4-686e-4fe9-970d-c68b5d0f83c7", "input/client/public")).json()) 
    
    # print((await cxone_client.get_repostore_file("153a99d4-686e-4fe9-970d-c68b5d0f83c7", "input/client/src/index.js")).text) 
   
    # async for scan in paged_api(cxone_client.get_scans, "scans", statuses=['Completed']):
    #     print(f"Scan Id: {scan['id']} ProjectId: {scan['projectId']} Branch: {scan['branch']}")

    # print((await cxone_client.get_scan("153a99d4-686e-4fe9-970d-c68b5d0f83c7")).json())

    await download_files_to_directory(cxone_client, '153a99d4-686e-4fe9-970d-c68b5d0f83c7', 'test')

    last_scan_dict = (await cxone_client.get_project_last_scans(limit=20)).json()

    for scan in last_scan_dict:
        print(f"Scan Id: {last_scan_dict[scan]}")
        # Paging has to be redone manually without page_api



asyncio.run(main())
