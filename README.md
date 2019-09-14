## Clone repo and create virtual environment:
```
cd turing_divvyDose_coding_challenge
virtualenv -p python3.6 venv
source venv/bin/activate
```

## Install:

You can use a virtual environment:
```
pip install -r requirements.txt
```

## Running the code 
set environment variables GITHUB_USERNAME and GITHUB_PASSWORD 
from command shell
```
export GITHUB_USERNAME=<your_github_username>
export GITHUB_PASSWORD=<your_github_password>
```


### Spin up the service

```
# activate the environment and start up local server
python -m run 
```

### Making Requests

```
curl -H "Content-Type: application/json" -X GET http://localhost:5000/api/merge-profiles/mailchimp
```
