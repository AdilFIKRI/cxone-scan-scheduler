import asyncio, os
from pathlib import Path


class ProjectRepoConfig:

    def __init__(self, cxone_client, project_data):
        self.__client = cxone_client
        self.__project_data = project_data
        self.__fetched_undocumented_config = False
        self.__lock = asyncio.Lock()
   
    async def __get_logical_repo_url(self):
        # The documented project API seems to have a bug and does not return the repoUrl.  The undocumented
        # API used by the UI has it.  The undocumented API will no longer be called when the project
        # API is fixed.
        async with self.__lock:
            if len(self.__project_data['repoUrl']) == 0 and not self.__fetched_undocumented_config:
                self.__fetched_undocumented_config = True
                config = (await self.__client.get_project_configuration(self.__project_data['id'])).json()

                for entry in config:
                    if entry['key'] == "scan.handler.git.repository":
                        self.__project_data['repoUrl'] = entry['value']
            
            return self.__project_data['repoUrl']

    @property
    async def primary_branch(self):
        return self.__project_data['mainBranch'] if len(self.__project_data['mainBranch']) > 0 else None

    @property
    async def repo_url(self):
        url = await self.__get_logical_repo_url()
        return url if len(url) > 0 else None

class Repostore:

    @staticmethod
    async def __download_files_to_directory_from_tree (cxone_client, scanid, tree, root_directory):
        real_root = os.path.realpath(root_directory)
        os.makedirs(Path(real_root) / tree['fullPath'], exist_ok=True)
        
        for entry in tree['files']:
            if bool(entry['isDir']):
                await Repostore.__download_files_to_directory_from_tree(cxone_client, scanid, entry, real_root)
            else:
                with open(Path(real_root) / Path(entry['fullPath']), "w") as dest:
                    fetched_file_resp = await cxone_client.get_repostore_file(scanid, entry['fullPath'])
                    if fetched_file_resp.ok:
                        dest.write(fetched_file_resp.text)
                    else:
                        pass
                        # it just won't download the file in this case...
                        # raise Exception(f"Could not load file {entry['fullPath']} from scan {scanid}")
        return True

            

    @staticmethod    
    async def download_files_to_directory(cxone_client, scanid, dest_directory):
        tree_response = await cxone_client.get_project_tree(scanid)
        if tree_response.ok:
            return await Repostore.__download_files_to_directory_from_tree(cxone_client, scanid, tree_response.json(), dest_directory)
        else:
            return False