# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /app

# Install system packages required for building kenlm
RUN apt-get update && apt-get install -y cmake g++ zlib1g-dev

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Install wget
RUN apt-get update && apt-get install -y wget

# Download the files using wget
RUN wget "https://drive.google.com/uc?export=download&id=14cMmeDPlAODbRe37CdHLnhClGX7JXG-A" -O 'freq_dict.txt'
RUN wget "https://drive.google.com/uc?export=download&id=1Ztj6k0A4BMi_o87qwSDKJQ6cyhvlvneD" -O 'freq_dict_eng.txt'

# Copy the rest of the application code to the working directory
COPY . /app/

EXPOSE 8000

# Set the entrypoint for the container
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "api:app"]
