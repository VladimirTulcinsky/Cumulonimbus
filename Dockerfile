FROM python:3.8


# Copy helper scripts to container
ADD docker/dependencies /root/bin

# Install required software
RUN ["/bin/bash", "-c", "/root/bin/container-install-prereqs.sh"]

# Install AWS CLI
RUN ["/bin/bash", "-c", "/root/bin/container-install-aws2.sh"]

# Install Azure CLI
RUN ["/bin/bash", "-c", "/root/bin/container-install-azure.sh"]


# Remove scripts
RUN ["rm", "-rf", "/root/bin"]

# Install Cumulonimbus
COPY ./app /app
WORKDIR /app

# Set path to credentials file
ENV AWS_SHARED_CREDENTIALS_FILES=/cumulonimbus/.data/.aws/credentials
ENV AWS_SHARED_CONFIG_FILES=/cumulonimbus/.data/.aws/config

ENV AZURE_CREDENTIALS_FILES=/cumulonimbus/.data/.azure/credentials


# Command
CMD ["/bin/bash"]
