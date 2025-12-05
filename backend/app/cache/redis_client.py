import os
import json
from typing import Optional, Any
from datetime import timedelta
import redis
from dotenv import load_dotenv

load_dotenv()


class RedisClient:
    """Redis cache client"""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, db: int = 0):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        self.client = None
        
        try:
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            self.client.ping()
        except:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except:
            pass
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.client:
            return False
        
        try:
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            if ttl:
                self.client.setex(key, ttl, json_value)
            else:
                self.client.set(key, json_value)
            return True
        except:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except:
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        if not self.client:
            return False
        
        try:
            self.client.flushdb()
            return True
        except:
            return False

