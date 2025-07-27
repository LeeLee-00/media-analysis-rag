from pydantic import BaseModel
from typing import Dict, Any, Optional, Union

class AnalysisResult(BaseModel):
    filename: str
    summary: Union[str, Dict[str, Any]]  # Allow summary to be either string or dict
    transcript: Optional[str]
    media_metadata: Optional[Dict[str, Any]] = None  # Make media_metadata optional with default None
