import asyncio
from pathlib import Path
import os

from utils import utils, checker, logger


logger = logger.get_logger()


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

    results = await asyncio.gather(*tasks)

    eligible_count = sum(1 for result in results if result)
    logger.success(f'Eligible wallets - {eligible_count}')

if __name__ == '__main__':
  asyncio.run(main())
