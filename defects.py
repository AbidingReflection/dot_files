    def get_defect_df_from_defect_runs(self, defect_runs_df):
        if len(defect_runs_df) < 1:
            return None
        defect_run_ids = defect_runs_df['id'].unique().tolist()

        request_count = math.ceil(len(defect_run_ids) / 100)

        defect_dict_list = []

        for k in range(request_count):
            api_url = self.CONFIG["qTest_domain"]
            api_url += self.API_URL_PREFIX
            api_url += str(self.CONFIG["project_id"])
            api_url += '/linked-artifacts?type=test-runs&ids='

            if k == request_count - 1:
                cur_defect_run_ids = defect_run_ids[(k * 100):]
            else:
                cur_defect_run_ids = defect_run_ids[(k * 100):((k * 100) + 100)]

            for defect_id in cur_defect_run_ids:
                api_url += str(defect_id) + "&ids="

            api_url = api_url[:(len(api_url) - 5)]

            if "mock_response_path" in self.CONFIG and self.CONFIG["mock_response_path"]:
                logging.debug(f"Responding to 'Defects' request with mock response from '{self.CONFIG['mock_response_path']}'")
                from unittest.mock import patch
                import re
                sanitized_target_name = re.sub(r'[<>:"/\\|?*]', '', self.target.target_name)
                with patch('requests.Session.send') as mock_send:
                    with open(Path(self.CONFIG["mock_response_path"], f'defects-{sanitized_target_name}-page_{k+1}_of_{request_count}.json'), 'r') as f:
                        mock_data = json.load(f)
                    mock_response = requests.Response()
                    mock_response.status_code = 200
                    mock_response._content = json.dumps(mock_data).encode('utf-8')
                    mock_send.return_value = mock_response

                    request = requests.Request("GET", api_url, headers=self.CONFIG["request_headers"])
                    response = self._process_request(request)
            else:
                request = requests.Request("GET", api_url, headers=self.CONFIG["request_headers"])
                response = self._process_request(request)

            if "capture_response_path" in self.CONFIG and self.CONFIG["capture_response_path"]:
                # Request capture
                data = response.json()
                import re
                sanitized_target_name = re.sub(r'[<>:"/\\|?*]', '', self.target.target_name)
                with open(Path(self.CONFIG["capture_response_path"], f'defects-{sanitized_target_name}-page_{k+1}_of_{request_count}_{time.strftime("%Y%m%d-%H%M%S")}.json'), 'w') as f:
                    json.dump(data, f, indent=4)

            for i in response.json():
                for j in i['objects']:
                    if j['link_type'] == "is_associated_with":
                        defect_dict_list.append({
                            'defect_id': j['id'],
                            'pid': j['pid'],
                            'jira_link': j['self'],
                            'id': i['id']
                        })

        defects_df = pd.DataFrame(defect_dict_list)

        defects_df = defects_df.drop_duplicates()

        return defects_df
