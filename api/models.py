from pydantic import BaseModel


class FetchPred(BaseModel):
    from_date: str
    to_date: str
    source: str  
      
    
class FetchPre(BaseModel):
    from_date: str
    to_date: str
    source: str    
    


class ToPred(BaseModel):
    source: str
    df: str


