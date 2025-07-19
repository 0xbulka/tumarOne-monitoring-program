#!/bin/sh
docker build -t tumar-mock-api . && docker run -d --name tumar_mock_api -p 4000:80 -v ./db.json:/data/db.json tumar-mock-api