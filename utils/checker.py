import asyncio
import aiohttp
from aiohttp_proxy import ProxyConnector
from fake_useragent import UserAgent

from utils import logger


logger = logger.get_logger()


async def checker(address, proxy, semaphore):
    async with semaphore:
        connector = ProxyConnector.from_url(f'http://{proxy}')
        headers = {
            'accept': '*/*',
            'priority': 'u=1, i',
            'referer': 'https://app.ether.fi/portfolio',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': UserAgent().random,
        }

        async with aiohttp.ClientSession(connector=connector) as session:
            for attempt in range(0, 3):
                try:
                        async with session.get(url=f'https://app.ether.fi/api/king/{address}', headers=headers) as response:
                            data = await response.json()
                            amount = data.get('Amount')
                            error = data.get('error')
                            if amount:
                                amount = int(amount) / 10 ** 18
                                logger.success(f'{address} | {amount} KING')
                                return
                            elif error:
                                logger.success(f'{address} | Not eligible')
                                return

                except Exception as err:
                    logger.warning(f'{address} | {err} |  Retry')
                    await asyncio.sleep(15)