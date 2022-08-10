# Modified from https://dev.to/ejach/how-to-deploy-a-python-flask-app-on-heroku-using-docker-mpc
#Create a ubuntu base image with python 3 installed.
FROM python:3.10

#Set the working directory
WORKDIR /

#copy all the files
COPY . .

#Install the dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --no-deps -r requirements.txt # Keep Flair from pulling in everything

#Expose the required port
EXPOSE 5000

#Run the command
CMD gunicorn server.app:app
