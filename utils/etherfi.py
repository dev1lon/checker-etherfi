import asyncio
import aiohttp
from fake_useragent import UserAgent
from eth_account import Account
from eth_account.messages import encode_defunct

from utils import logger
import settings


logger = logger.get_logger()


class EtherFi:
    def __init__(self, private_key: str, proxy: str, semaphore: asyncio.Semaphore):
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = f'http://{proxy}'
        self.amount = 0
        self.semaphore = semaphore

    async def checker(self):
        headers = {
            'user-agent': UserAgent().random,
        }

        for attempt in range(0,3):
            try:
                async with self.semaphore:
                    async with aiohttp.request(method='GET',url=f'https://app.ether.fi/api/portfolio/season-four/{self.address}', headers=headers, proxy=self.proxy) as response:
                        data = await response.json()
                        self.amount = data.get('S4RewardsAmount')
                        error = data.get('error')
                        if self.amount:
                            self.amount = round(int(self.amount) / 10 ** 18, 5)
                            if settings.network is None:
                                logger.success(f'{self.address} | {self.amount} KING')
                            return True
                        elif error:
                            logger.success(f'{self.address} | Not eligible')
                            return False

            except Exception as err:
                logger.warning(f'{self.address} | {err} |  Retry')
                await asyncio.sleep(15)

    async def set_network(self):
        if await self.checker():
            if settings.network is not None:
                network = settings.network

                sign_text = f'I want to claim my KING tokens on {network}'
                encoded_message = encode_defunct(text=sign_text)
                signed_message = self.account.sign_message(encoded_message)

                json_data = {
                    'address': self.address,
                    'message': f'I want to claim my KING tokens on {network}',
                    'signature': '0x' + signed_message.signature.hex(),
                }

                async with self.semaphore:
                    async with aiohttp.request(method='POST',url=f'https://app.ether.fi/api/king-claim-chain/{self.address}', json=json_data, proxy=self.proxy) as response:
                        data = await response.json()
                        if 'success' in data:
                            logger.success(f'{self.address} | {self.amount} KING | Select network for claim - {network}')
                            await asyncio.sleep(2)
                            return True
