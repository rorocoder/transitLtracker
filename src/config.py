from dotenv import load_dotenv
import os

load_dotenv()

WALK_TO_BUS = 3 # minutes
WALK_TO_METRA = 10 # minutes

BUS_ARRIVAL_PADDING = 7 # minutes
GOOD_RL_WAIT = 5 # minutes
GOOD_GL_WAIT = 10 # minutes

CTA_BUS_API_KEY = os.getenv('CTA_BUS_API_KEY')
CTA_TRAIN_API_KEY = os.getenv('CTA_TRAIN_API_KEY')
METRA_API_KEY = ""

ELLIS_BUS_STOP_ID = "10575"
GL_BUS_STOP_ID = "10582"
RL_BUS_STOP_ID = "10589"

RL_GARFIELD_TRAIN_STOP_ID = "30223"
GL_GARFIELD_TRAIN_STOP_ID = "30099"

METRA_STOP_ID = ""

