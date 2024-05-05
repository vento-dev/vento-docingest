import os
print('executing __init__ in package {} at path {}'.format(os.curdir, os.path))

import vertexai
print(f'loading vertexai...')
vertexai.init(project="720913457461", location="us-central1")