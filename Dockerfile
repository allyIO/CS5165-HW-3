FROM python:3.9-slim

# Set the working directory
WORKDIR /home/data
# Copy Python script and text files to the container
COPY script.py .
COPY IF.txt .
COPY AlwaysRememberUsThisWay.txt .
RUN mkdir /home/data/output
#<Add additional commands such as RUN>
CMD ["python", "script.py"]
