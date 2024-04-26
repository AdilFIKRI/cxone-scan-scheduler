from cxone_api import AuthUS, ApiUS, paged_api, CxOneClient
from cxone_api.repo import ProjectRepoConfig
import os, asyncio


async def main():
    cxone_client = CxOneClient.create_with_oauth(os.environ["OAUTH_CLIENTID"], os.environ["OAUTH_CLIENTSECRET"], "CxOneAPIExample",
        AuthUS(os.environ["TENANT"]), ApiUS())
    
    async for scan in paged_api(cxone_client.get_scans, "scans", statuses=['Completed']):
        print(f"Scan Id: {scan['id']} ProjectId: {scan['projectId']} Branch: {scan['branch']}")
        pass

asyncio.run(main())
