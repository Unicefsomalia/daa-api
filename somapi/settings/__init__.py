from .base import *

try:
    from .local import *

    # print("Local only")
    live = False
except Exception as e:
    print(e)
    live = True

if live:
    # print("Live mode enabled")
    from .production import *
