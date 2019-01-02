#!/bin/bash
docker build -t ljmentas/backend:latest .
docker push ljmentas/backend:latest
#we might add testing here
