import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=6379,
    decode_responses=True
)