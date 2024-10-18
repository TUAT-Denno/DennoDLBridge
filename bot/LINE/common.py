import aiohttp
import asyncio

async def line_get_request(url : str, token : str) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url = url,
            headers = { 'Authorization': 'Bearer ' + token }
        ) as response:
            return response
        
async def line_post_request(url :str, headers : dict, data : dict) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url = url,
            headers = headers,
            data = data
        ) as response:
            return response
