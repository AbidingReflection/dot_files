    def get_linked_requirements(self):
        linked_requirements_dict = {}
        pageNum = 1
        matrix_response_list = []

        api_url = self.CONFIG["qTest_domain"]
        api_url += self.API_URL_PREFIX
        api_url += str(self.CONFIG["project_id"])
        api_url += f'/requirements/trace-matrix-report?page={pageNum}&size=999'

        headers = {'Authorization': f'{self.CONFIG["AUTH"]["bearer_token"]}'}
        response = requests.get(api_url, headers=headers, verify=False)

        at_end = False
        # Handles multi-page responses
        while response.status_code == 200 and not at_end:
            linked_requirements_list = response.json()
            if len(linked_requirements_list) < 1:
                at_end = True
                continue

            # Adds response for page to response list
            matrix_response_list.append(linked_requirements_list)
            pageNum += 1

            api_url = self.CONFIG["qTest_domain"]
            api_url += self.API_URL_PREFIX
            api_url += str(self.CONFIG["project_id"])
            api_url += f'/requirements/trace-matrix-report?page={pageNum}&size=999'
            response = requests.get(api_url, headers=headers, verify=False)


        for req_dict_list in matrix_response_list:

            parentDictList = req_dict_list
            childList = []

            while(len(parentDictList)>0):
                childList = []
                levelDictList = parentDictList
                for req_dict in levelDictList:
                    for req in req_dict['requirements']:
                        if "linked-testcases" in req.keys():
                            linked_requirements_dict[req['id']] = {'id':req['id'],
                                                    'req_name': req['name'],
                                                    'testcases': req['testcases'],
                                                    'linked_testcase_count':req['linked-testcases']}

                    if len(req_dict['children']) > 0 :
                        for req in req_dict['children']:
                            childList.append(req)
                parentDictList = childList
                        
        req_df = pd.DataFrame(list(linked_requirements_dict.values()), index=list(linked_requirements_dict.keys()))

        return req_df
