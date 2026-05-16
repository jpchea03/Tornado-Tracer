# Title: joplin_2011.py
# Description: Test NEXRAD pipeline with the Joplin, MO tornado event on May 22, 2011.
# Author: Joseph Cheatham

from pipeline import run_pipeline
import pytz
from datetime import datetime

if __name__ == '__main__':
    start = datetime(2011, 5, 22, 22, 30, tzinfo=pytz.UTC)
    end   = datetime(2011, 5, 22, 23, 15, tzinfo=pytz.UTC)
    run_pipeline(start, end, 'KSGF')