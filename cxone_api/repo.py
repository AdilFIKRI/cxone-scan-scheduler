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
