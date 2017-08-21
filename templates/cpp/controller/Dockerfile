FROM avatao/controller:ubuntu-16.04

# Copy is prefered for simple files/directories as
# it doesn't try to decompress archives or fetch URLs.
COPY ./controller/ /

# Set environment variable to communicate with the solvable on an HTTP port
ENV SOLVABLE_PORT=7777