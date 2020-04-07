# -*- coding: UTF-8 -*-
import os
import re
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from template.common import (
    InfoExtractor,
    InfoExtractorJSON,
    NewsPostman,
    NewsPostmanJSON,
)
from utils import (
    add_parameters_into_url,
)

print("DELETED!!")