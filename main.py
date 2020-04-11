# -*- coding: UTF-8 -*-
import json
import os
import re
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from template.common import (
    InfoExtractor,
    InfoExtractorJSON,
    InfoExtractorXML,
    NewsPostman,
    NewsPostmanJSON,
    NewsPostmanXML,
)
from utils import (
    add_parameters_into_url,
)

print("DELETED!!")