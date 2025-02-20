from decouple import config
# from .base import *


project = config('PROJECT', default='dev')


# Determine which settings to import based on the project variable
if project == 'local':
    print("Running local...", 'green')
    from .local import *
else:
    print("Running development...", 'green')
    from .dev import *