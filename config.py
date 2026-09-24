import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent
load_dotenv(BASE_DIR/'.env')
@dataclass(frozen=True)
class Settings:
    groq_api_key:str; groq_model:str; groq_timeout:float; max_input_chars:int; min_input_words:int; database_path:str
settings=Settings(os.getenv('GROQ_API_KEY','').strip(),os.getenv('GROQ_MODEL','openai/gpt-oss-20b').strip(),float(os.getenv('GROQ_TIMEOUT','60')),int(os.getenv('MAX_INPUT_CHARS','30000')),int(os.getenv('MIN_INPUT_WORDS','80')),os.getenv('DATABASE_PATH',str(BASE_DIR/'briefly_ai.db')))
