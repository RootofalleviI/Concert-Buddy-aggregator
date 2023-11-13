from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


@app.get("/{user_id}")
async def root(user_id: str):
    return {
        'info': parse_user_info(get_user_info(user_id)),
        'songs': parse_user_songs(get_user_songs(user_id))
    }


def get_user_info(user_id: str):
    """
    Fetch user information from an external API for a given user ID.
    """
    # Replace with the actual base URL of the external API
    url = f'http://example.com/api/v1/users/{user_id}'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Assuming the response is JSON
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_user_info(info):
    pass


@app.get("/get-user-songs/{user_id}")
async def get_user_songs(user_id: str):
    """
    Fetch songs for a given user ID from an external API.
    """
    # Replace with the actual base URL of the external API
    url = f'http://example.com/api/v1/users/{user_id}/songs'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Assuming the response is JSON
        else:
            raise HTTPException(status_code=404, detail="Songs not found for the user")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_user_songs(songs):
    pass
