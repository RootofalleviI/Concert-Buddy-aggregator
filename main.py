import asyncio
import dataclasses
import datetime
import random
from typing import Dict, List

import httpx
import requests
from fastapi import FastAPI, HTTPException

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
async def main_async(user_id: str, concert_id: str):
    async def task_wrapper(task: str, coro: any):
        return task, await coro

    tasks = [
        task_wrapper('info', get_user_info(user_id)),
        task_wrapper('songs', get_user_songs(user_id)),
        task_wrapper('concert', get_concert_info(concert_id)),
        task_wrapper('matches', get_user_matches(user_id, concert_id))
    ]

    results = {}
    for future in asyncio.as_completed(tasks):
        name, result = await future
        if name == 'info':
            results['info'] = parse_user_info(result)
        elif name == 'songs':
            results['songs'] = parse_user_songs(result)
        elif name == 'concert':
            results['concert'] = parse_concert_info(result)
        elif name == 'matches':
            results['matches'] = parse_user_matches(result)

    return results


# @app.get("/{user_id}/{concert_id}")
# async def main_sync(user_id: str, concert_id: str):
#     user_info = await get_user_info(user_id)
#     user_songs = await get_user_songs(user_id)
#     concert_info = await get_concert_info(concert_id)
#     user_matches = await get_user_matches(user_id, concert_id)
#
#     return {
#         'info': parse_user_info(user_info),
#         'songs': parse_user_songs(user_songs),
#         'concert': parse_concert_info(concert_info),
#         'matches': parse_user_matches(user_matches)
#     }


# =====================================
# User Info
# =====================================
# @app.get("/get-user-info/{user_id}")
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
# @app.get("/get-user-songs/{user_id}")
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
# @app.get("/get-concert-info/{concert_id}")
async def get_concert_info(concert_id: str):
    """
    Fetch info for a given concert from an external API.
    """
    url = f'{CONCERT_MICROSERVICE_URL}/api/v1/concerts/{concert_id}'

    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(random.random())
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
# @app.get("/get-user-matches/{user_id}/{concert_id}")
async def get_user_matches(user_id: str, concert_id: str):
    """
    Fetch matches at a given concert for a given user ID from an external API.
    """
    url = f'{FINDER_MICROSERVICE_URL}/api/v1/finder/{user_id}/{concert_id}'

    async with httpx.AsyncClient() as client:
        try:
            await asyncio.sleep(random.random())
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
    asyncio.run(main_async(SAMPLE_USER_ID, SAMPLE_CONCERT_ID))
