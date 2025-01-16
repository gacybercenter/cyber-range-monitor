import httpx


class AuthClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = httpx.Client(base_url=base_url)
        self.access_token: str | None = None

    
    def _set_access_token(self, response_json: dict) -> str:
        self.access_token = response_json['access_token']
        return self.access_token
    
    def login(self, username: str, password: str) -> str:
        '''
        Logs in and sets the access token for the instance 
        Arguments:
            username {str} 
            password {str} 
        Returns:
            str -- the access token
        '''
        form_data = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        response = self.client.post("/auth/token", data=form_data)
        response.raise_for_status()

        data = response.json()  # EncodedToken { "access_token": "<...>" }
        return self._set_access_token(data)

    def refresh_access_token(self) -> str:
        """
        Requests a new access token via /auth/refresh.
        The refresh token is automatically picked up from the client's cookies.
        """
        response = self.client.post("/auth/refresh")
        response.raise_for_status()

        data = response.json()  # EncodedToken { "access_token": "<...>" }
        self.access_token = data['access_token']
        return self.access_token

    def logout(self) -> None:
        """
        Logs out the user via /auth/logout, revoking the tokens and clearing cookies.
        """
        response = self.client.get("/auth/logout")
        response.raise_for_status()
        self.access_token = None

    def get(self, url: str, **kwargs) -> httpx.Response:
        """
        Make an authenticated GET request using the stored access_token.
        """
        headers = kwargs.pop("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return self.client.get(url, headers=headers, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        """
        Make an authenticated POST request using the stored access_token.
        """
        headers = kwargs.pop("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return self.client.post(url, headers=headers, **kwargs)

    def close(self):
        """
        Close the underlying httpx.Client session
        """
        self.client.close()
