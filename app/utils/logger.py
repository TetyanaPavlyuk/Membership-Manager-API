import logging
import asyncio

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(fmt="%(asctime)s - %(message)s")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]


async def async_log(message: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, logger.info, message)
