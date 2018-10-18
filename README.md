# databot 
[![Codeship Status for vshelke/databot](https://app.codeship.com/projects/97219030-b4fb-0136-f9e5-32589ba82fe2/status?branch=master)](https://app.codeship.com/projects/311332)

A databot made for jaano india iniative.

# install and run

```pip install -r requirements.txt```

```export FLASK_APP=app.py```

```flask run```


## Docker deployment

Build image:

```
docker build -t databot:0.1 .
```

Run container:

```
docker run -p 8080:8080 databot:0.1
``` 
