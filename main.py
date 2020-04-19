# -*- coding: UTF-8 -*-
import hashlib
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
    LOGO,
    add_parameters_into_url,
    xml_to_json,
)

print("DELETED!!")