#Create a ubuntu base image with python 3 installed.
FROM python:3.7.0

#Set the working directory
WORKDIR /app

#copy all the files
COPY . .

#Install the dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN python -m pip install --upgrade pip
RUN pip install cmake
RUN pip install -r requirements.txt

#Run the command
CMD python app.py

#Expose the required port
EXPOSE 5000