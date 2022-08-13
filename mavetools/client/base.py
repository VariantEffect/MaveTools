import json
import logging
import requests
import sys


class BaseClient:
    """
    The BaseClient object upon instantiation sets the base url where API requests will be made.
    """

    def __init__(self, base_url="http://127.0.0.1:8000/api/", auth_token=""):
        """
        Instantiates the Client object and sets the values for base_url and
        auth_token

        Parameters
        ----------
        base_url: the url in which the api endpoint exists
            default: 'http://127.0.0.1:8000/api/'
        auth_token: authorizes POST requests via the API and MaveDB
            default: ''
        """
        self.base_url = base_url
        if auth_token:
            self.auth_token = auth_token

    class AuthTokenMissingException(Exception):
        pass

    def get_model_instance(self, endpoint, instance_id):
        """
        Using a GET, hit an API endpoint to get info on a particular instance
        of a model class such as a ScoreSet.
        This will perform the HTTP GET request and then let the class itself
        parse the JSON data.

        Parameters
        ----------
        endpoint : str
            The API endpoint where we want the request to be made. This is the url extension beyond the base url
            used to instantiate the Client object. For example if you want an experiment from the base url
            'http://127.0.0.1:8000/api/v1/', the api_endpoint argument would be "experiments", making an API endpoint
            of 'http://127.0.0.1:8000/api/v1/experiments'.
        instance_id : str
            The id of the object we are retrieving.

        Returns
        -------
        model_instance: str
            An instance of the passed class as a JSON str.

        Raises
        ------
        ValueError
            If any mandatory fields are missing.
        """
        model_url = f"{self.base_url}{endpoint}/"
        instance_url = f"{model_url}{instance_id}/"
        try:
            r = requests.get(instance_url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(r.json())
            raise SystemExit(e)

        return r.json()

    def post_model_instance(self, model_instance, endpoint, files=None):
        """
        Using a POST, hit an API endpoint to post a resource.
        Performs HTTP POST request.

        Parameters
        ----------
        model_instance: dict
            Instance of model that will be POSTed.
        endpoint: str
            The API endpoint where we want the request to be made. This is the url extension beyond the base url
            used to instantiate the Client object. For example if you want an experiment from the base url
            'http://127.0.0.1:8000/api/v1/', the api_endpoint argument would be "experiments", making an API endpoint
            of 'http://127.0.0.1:8000/api/v1/experiments'.
        files
            The files associated with the model instance.

        Returns
        -------
        str
            The URN of the created model instance.

        Raises
        ------
        AuthTokenMissingException
            If the auth_token is missing
        """
        model_url = f"{self.base_url}{endpoint}/"

        # do MaveCore validation here

        # check for existence of self.auth_token, raise error if does not exist
        if not self.auth_token:
            error_message = "Need to include an auth token for POST requests!"
            logging.error(error_message)
            raise self.AuthTokenMissingException(error_message)

        try:  # to post data
            r = requests.post(
                model_url,
                json=model_instance,
                #files=files,
                headers={"access_token": self.auth_token},
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(r.text)
            sys.exit(1)

        # make second request to post files here, or inside the try block

        # No errors or exceptions at this point, log successful upload
        logging.info(f"Successfully uploaded {model_instance}!")

        # return the URN of the created model instance
        return json.loads(r.text)['urn']
