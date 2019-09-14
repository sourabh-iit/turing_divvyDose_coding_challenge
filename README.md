## Install:

You can use a virtual environment:
```
pip install -r requirements.txt
```

## Running the code
``` 
set environment variables GITHUB_USERNAME and GITHUB_PASSWORD 
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
