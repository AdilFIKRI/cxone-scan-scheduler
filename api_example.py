from cxone_api import AuthUS, ApiUS, paged_api, CxOneClient
from cxone_api.repo import Repostore
import os, asyncio, urllib
from pathlib import Path


async def main():
    proxy = {"http" : "http://localhost:8080", "https" : "http://localhost:8080"}

    cxone_client = CxOneClient.create_with_oauth(os.environ["OAUTH_CLIENTID"], os.environ["OAUTH_CLIENTSECRET"], "CxOneAPIExample",
        AuthUS(os.environ["TENANT"]), ApiUS(), ssl_verify=True, proxy = None)

    # print ((await cxone_client.get_repostore_project_tree("153a99d4-686e-4fe9-970d-c68b5d0f83c7")).json())   

    # print((await cxone_client.get_repostore_folder("153a99d4-686e-4fe9-970d-c68b5d0f83c7", "input/client/public")).json()) 
    
    # print((await cxone_client.get_repostore_file("153a99d4-686e-4fe9-970d-c68b5d0f83c7", "input/client/src/index.js")).text) 
   
    # async for scan in paged_api(cxone_client.get_scans, "scans", statuses=['Completed']):
    #     print(f"Scan Id: {scan['id']} ProjectId: {scan['projectId']} Branch: {scan['branch']}")

    # print((await cxone_client.get_scan("153a99d4-686e-4fe9-970d-c68b5d0f83c7")).json())

    # await Repostore.download_files_to_directory(cxone_client, '153a99d4-686e-4fe9-970d-c68b5d0f83c7', './test')

    task_results = []

    async with asyncio.TaskGroup() as tg:
        async for project in paged_api(cxone_client.get_projects, "projects"):
            project_branches_result = await cxone_client.get_branches(project_id=project['id'], limit=100)
            if not project_branches_result.ok:
                continue

            project_branches = project_branches_result.json()
            
            if project_branches is None:
                continue

            for branch in project_branches:
                last_scan_response = await cxone_client.get_project_last_scans(branch=branch, limit=1, project_ids=[project['id']])
                if last_scan_response.ok:
                    last_scan = last_scan_response.json()
                    last_scan_id = last_scan[project['id']]['id']

                    # Inserts a tuple of (scanid, coro) so result of download can be checked at the end
                    task_results.append ((last_scan_id, tg.create_task(Repostore.download_files_to_directory(cxone_client, last_scan_id, 
                                                                            Path("./downloads") / urllib.parse.quote(f"{project['name']}-{branch}")))))
                else:
                    raise Exception(f"Project: {project['id']} Branch: {branch}: failure to get last scan.")

    # last_scan_dict = (await cxone_client.get_project_last_scans(limit=1)).json()

    # for scan in last_scan_dict:
    #     print(f"Scan Id: {last_scan_dict[scan]}")
    #     # Paging has to be redone manually without page_api



asyncio.run(main())
