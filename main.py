import asyncio
import dataclasses
import datetime
from typing import Dict, List

import httpx
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
import random

SAMPLE_USER_ID = '0e21d65c-203a-4ba8-88f6-06cac7a0a2ca'
SAMPLE_CONCERT_ID = 'b392da9d-3d11-4d2d-98e1-6219a9a4f056'
USER_MICROSERVICE_URL = 'http://ec2-13-59-208-208.us-east-2.compute.amazonaws.com:8012'
FINDER_MICROSERVICE_URL = 'http://ec2-18-191-86-156.us-east-2.compute.amazonaws.com:8080'
CONCERT_MICROSERVICE_URL = 'http://concertbuddyconcert.uc.r.appspot.com'

app = FastAPI()


@app.get("/")
def root():
    return 'Hello World!'


@app.get("/{user_id}/{concert_id}")
async def main(user_id: str, concert_id: str):
    tasks = [
        get_user_info(user_id),
        get_user_songs(user_id),
        get_concert_info(concert_id),
        get_user_matches(user_id, concert_id)
    ]

    results = {}
    for task in asyncio.as_completed(tasks):
        result = await task
        if isinstance(result, UserInfo):  # Assuming get_user_info returns an instance of UserInfo
            results['info'] = parse_user_info(result)
        elif isinstance(result, list):  # Assuming get_user_songs returns a list
            # You may need to refine this condition based on the actual return type
            results['songs'] = parse_user_songs(result)
        elif isinstance(result, Concert):  # Assuming get_concert_info returns an instance of Concert
            results['concert'] = parse_concert_info(result)
        elif isinstance(result, Match):  # Assuming get_user_matches returns an instance of Match
            results['matches'] = parse_user_matches(result)
        # Add additional conditions as necessary for different return types

    return results


# =====================================
# User Info
# =====================================
@app.get("/get-user-info/{user_id}")
async def get_user_info(user_id: str):
    """
    Fetch user information from an external API for a given user ID.
    """
    url = f'{USER_MICROSERVICE_URL}/api/v1/users/{user_id}'
    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(random.random())
            response = await client.get(url)

            if response.status_code == 200:
                res = response.json()
                print(f"Got user info")
                return res
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


# =====================================
# User Songs
# =====================================
@app.get("/get-user-songs/{user_id}")
async def get_user_songs(user_id: str):
    """
    Fetch songs for a given user ID from an external API.
    """
    url = f'{USER_MICROSERVICE_URL}/api/v1/users/{user_id}/songs'

    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(random.random())
            response = await client.get(url)

            if response.status_code == 200:
                res = response.json()
                print(f"Got user songs")
                return res
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


# =====================================
# Concert Info
# =====================================
@app.get("/get-concert-info/{concert_id}")
async def get_concert_info(concert_id: str):
    """
    Fetch info for a given concert from an external API.
    """
    url = f'{CONCERT_MICROSERVICE_URL}/api/v1/concerts/{concert_id}'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)

            if response.status_code == 200:
                res = response.json()
                print(f"Got concert info")
                return res
            else:
                raise HTTPException(status_code=404, detail="Concert not found")

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))


@dataclasses.dataclass
class Concert:
    id: str
    name: str
    venue: str
    performingArtist: str
    dateTime: str
    genre: str
    subGenre: str


def parse_concert_info(data: Dict) -> Concert:
    return Concert(**data)


# =====================================
# User Matches
# =====================================
@app.get("/get-user-matches/{user_id}/{concert_id}")
async def get_user_matches(user_id: str, concert_id: str):
    """
    Fetch matches at a given concert for a given user ID from an external API.
    """
    url = f'{FINDER_MICROSERVICE_URL}/api/v1/finder/{user_id}/{concert_id}'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data={'userId': user_id, 'concertId': concert_id})

            if response.status_code == 200:
                res = response.json()
                print(f"Got user matches")
                return res
            else:
                raise HTTPException(status_code=404,
                                    detail=f"Didn't find match for user {user_id} at concert {concert_id}")

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))


@dataclasses.dataclass
class Match:
    id: str
    userId: str
    concertId: str
    matchedUserId: List[str]


def parse_user_matches(data: Dict) -> Match:
    del data['_links']
    return Match(**data)


if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    asyncio.run(main(SAMPLE_USER_ID, SAMPLE_CONCERT_ID))
