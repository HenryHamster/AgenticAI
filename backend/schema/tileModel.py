"""
Tile-specific data models
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional

class SecretKV(BaseModel):
    key: str
    value: int

class TileModel(BaseModel):
    position: List[int] = Field(min_length=2, max_length=2)
    description: str = Field(default="")
    terrainType: str = Field(default="plains")
    terrainEmoji: str = Field(default="🌾")
    secrets: Optional[List[SecretKV]] = Field(default_factory=list)
    
    @model_validator(mode='before')
    @classmethod
    def transform_secrets(cls, data: Any) -> Any:
        """Transform secrets from {'key': value} format to {'key': 'key', 'value': value} format"""
        if isinstance(data, dict) and 'secrets' in data:
            secrets = data['secrets']
            if isinstance(secrets, list):
                transformed_secrets = []
                for secret in secrets:
                    if isinstance(secret, dict):
                        # Check if it's already in the correct format
                        if 'key' in secret and 'value' in secret:
                            transformed_secrets.append(secret)
                        else:
                            # Transform from {'coin stash': 12} to {'key': 'coin stash', 'value': 12}
                            for k, v in secret.items():
                                transformed_secrets.append({'key': k, 'value': v})
                    else:
                        transformed_secrets.append(secret)
                data['secrets'] = transformed_secrets
        return data
