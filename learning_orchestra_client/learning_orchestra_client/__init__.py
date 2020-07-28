import requests
import json
import time

cluster_url = None


class Context():
    def __init__(self, ip_from_cluster):
        global cluster_url
        cluster_url = 'http://' + ip_from_cluster


class AsyncronousWait():
    WAIT_TIME = 3
    METADATA_INDEX = 0

    def wait(self, filename, pretty_response=True):
        if(pretty_response):
            print("\n----------" + " WAITING " + filename + " FINISH " +
                  "----------")

        database_api = DatabaseApi()

        while(True):
            time.sleep(self.WAIT_TIME)
            response = database_api.read_file(
                filename, limit=1, pretty_response=False)

            if(len(response["result"]) == 0):
                continue

            if(response["result"][self.METADATA_INDEX]["finished"]):
                break


class ResponseTreat():
    UNKNOW_ERROR = "unknow server error"
    HTTP_CREATED = 201
    HTTP_SUCESS = 200
    HTTP_ERROR = 500

    def treatment(self, response, pretty_response=True):
        if(response.status_code != self.HTTP_SUCESS and
           response.status_code != self.HTTP_CREATED):
            raise Exception(response.json()["result"])
        elif(response.status_code >= self.HTTP_ERROR):
            raise Exception(self.UNKNOW_ERROR)
        else:
            if(pretty_response):
                return json.dumps(response.json(), indent=2)
            else:
                return response.json()


class DatabaseApi():
    DATABASE_API_PORT = "5000"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.DATABASE_API_PORT + '/files'
        self.asyncronous_wait = AsyncronousWait()

    def read_resume_files(self, pretty_response=True):
        if(pretty_response):
            print("\n----------" + " READ RESUME FILES " + "----------")

        url = self.url_base
        response = requests.get(url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_file(self, filename, skip=0, limit=10, query={},
                  pretty_response=True):
        if(pretty_response):
            print("\n----------" + " READ FILE " + filename + " ----------")

        request_params = {
            'skip': str(skip),
            'limit': str(limit),
            'query': str(query)
        }
        read_file_url = self.url_base + '/' + filename
        response = requests.get(
            url=read_file_url, params=request_params)

        return ResponseTreat().treatment(response, pretty_response)

    def create_file(self, filename, url, pretty_response=True):
        if(pretty_response):
            print("\n----------" + " CREATE FILE " + filename + " ----------")

        request_body_content = {
            'filename': filename,
            'url': url
        }

        response = requests.post(url=self.url_base, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)

    def delete_file(self, filename, pretty_response=True):
        if(pretty_response):
            print("\n----------" + " DELETE FILE " + filename + " ----------")

        self.asyncronous_wait.wait(filename, pretty_response)

        request_url = self.url_base + '/' + filename
        response = requests.delete(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)


class Projection():
    PROJECTION_PORT = "5001"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.PROJECTION_PORT + \
            '/projections'

        self.asyncronous_wait = AsyncronousWait()

    def create_projection(self, filename, projection_filename, fields,
                          pretty_response=True):
        if(pretty_response):
            print("\n----------" + " CREATE PROJECTION FROM " + filename +
                  " TO " + projection_filename + " ----------")

        self.asyncronous_wait.wait(filename, pretty_response)

        request_body_content = {
            'projection_filename': projection_filename,
            'fields': fields
        }
        request_url = self.url_base + '/' + filename
        response = requests.post(url=request_url, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)


class DataTypeHandler():
    DATA_TYPE_HANDLER_PORT = "5003"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.DATA_TYPE_HANDLER_PORT + \
            '/fieldtypes'
        self.asyncronous_wait = AsyncronousWait()

    def change_file_type(self, filename, fields_dict, pretty_response=True):
        if(pretty_response):
            print("\n----------" + " CHANGE " + filename + " FILE TYPE " +
                  "----------")

        self.asyncronous_wait.wait(filename, pretty_response)

        url_request = self.url_base + '/' + filename

        response = requests.patch(url=url_request, json=fields_dict)

        return ResponseTreat().treatment(response, pretty_response)


class ModelBuilder():
    MODEL_BUILDER_PORT = '5002'

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.MODEL_BUILDER_PORT + '/models'
        self.asyncronous_wait = AsyncronousWait()

    def build_model(self, training_filename, test_filename, label='label',
                    pretty_response=True):
        if(pretty_response):
            print("\n----------" + " BUILD MODEL WITH " + training_filename +
                  " AND " + test_filename + " ----------")

        self.asyncronous_wait.wait(training_filename, pretty_response)
        self.asyncronous_wait.wait(test_filename, pretty_response)

        request_body_content = {
            'training_filename': training_filename,
            'test_filename': test_filename,
            'label': label
        }

        response = requests.post(url=self.url_base, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)
