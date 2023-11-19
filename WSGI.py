import sys
import os

# Assuming your Flask app is in a folder named 'myapp' and the main file is 'app.py'
# and your PythonAnywhere username is 'yourusername'

# Add your project directory to the sys.path
project_home = '/home/Tikob24/BGRemover'
if project_home not in sys.path:
    sys.path.append(project_home)


# Activate your virtual environment
path_to_virtualenv = '/home/Tikob24/.virtualenvs/venv'  # Replace 'venv' with your env name
if path_to_virtualenv not in sys.path:
    sys.path.append(path_to_virtualenv)

# Now we can import packages from the virtualenv
activate_this = os.path.join(path_to_virtualenv, 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
