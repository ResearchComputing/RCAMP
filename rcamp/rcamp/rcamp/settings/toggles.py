import os
_debug = os.environ.get('RCAMP_DEBUG', 'False')
DEBUG = _debug == 'True'
