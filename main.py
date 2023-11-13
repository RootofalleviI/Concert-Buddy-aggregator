import asyncio
import dataclasses
import datetime
from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException

SAMPLE_USER_ID = '130bd19b-92b6-4dd7-90ef-c477bca9a824'
USER_MICROSERVICE_URL = 'http://127.0.0.1:8080'  # TODO: Replace this when project is deployed

app = FastAPI()


@app.get("/")
def root():
    return 'Hello World!'


@app.get("/{user_id}")
async def main(user_id: str):
    return {
        'info': parse_user_info(get_user_info(user_id)),
        'songs': parse_user_songs(await get_user_songs(user_id))
    }


def get_user_info(user_id: str):
    """
    Fetch user information from an external API for a given user ID.
    """
    # Replace with the actual base URL of the external API
    url = f'{USER_MICROSERVICE_URL}/api/v1/users/{user_id}'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Assuming the response is JSON
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@dataclasses.dataclass
class UserInfo:
    id: str
    name: str
    dateOfBirth: datetime.date
    age: int
    email: str
    profilePictureUrl: str


def parse_user_info(data: Dict):
    del data['password']

    if 'dateOfBirth' in data:
        data['dateOfBirth'] = datetime.datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date()

    return UserInfo(**data)


@app.get("/get-user-songs/{user_id}")
async def get_user_songs(user_id: str):
    """
    Fetch songs for a given user ID from an external API.
    """
    # Replace with the actual base URL of the external API
    url = f'{USER_MICROSERVICE_URL}/api/v1/users/{user_id}/songs'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Songs not found for the user")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@dataclasses.dataclass
class Song:
    id: str
    name: str
    artist: str
    genre: List[str]
    link: str


def parse_user_songs(data: Dict) -> List[Song]:
    try:
        songs = []
        for song_info in data['_embedded']['songList']:
            song_info['link'] = song_info['_links']['self']['href']
            del song_info['_links']
            songs.append(Song(**song_info))
        return songs
    except KeyError as e:
        # Handle missing keys in the data
        print(f"Key error: {e}")
        return []
    except TypeError as e:
        # Handle wrong data type issues
        print(f"Type error: {e}")
        return []
    except Exception as e:
        # Handle any other general exceptions
        print(f"An unexpected error occurred: {e}")
        return []


if __name__ == '__main__':
    print(asyncio.run(main(SAMPLE_USER_ID)))
