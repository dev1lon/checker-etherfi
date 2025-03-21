import asyncio
from pathlib import Path
import os

from utils import utils, checker


BASE_DIR = Path(__file__).resolve().parent
addresses = utils.read_file(os.path.join(BASE_DIR, "wallets.txt"))
proxies = utils.read_file(os.path.join(BASE_DIR, "proxies.txt"))


async def main():
    if len(addresses) != len(proxies):
        raise Exception('Адреса не соответствуют количеству прокси')
    elif len(addresses) == 0 or len(proxies) == 0:
        raise Exception('Нет прокси и адресов')

    semaphore = asyncio.Semaphore(3)

    tasks = []
    for address, proxy in zip(addresses, proxies):
        tasks.append(checker.checker(address, proxy, semaphore))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
  asyncio.run(main())