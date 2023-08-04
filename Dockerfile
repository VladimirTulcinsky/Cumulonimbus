FROM python:3.8

# Copy helper scripts to container
ADD docker/dependencies /root/bin

# Install required software
RUN /bin/bash -c "/root/bin/container-install-prereqs.sh" \
    && /bin/bash -c "/root/bin/container-install-aws2.sh" \
    && /bin/bash -c "/root/bin/container-install-azure.sh" \
    && rm -rf /root/bin
    
# Install Cumulonimbus
COPY ./app /root/app
WORKDIR /root/app

# Set path to credentials file
ENV AWS_SHARED_CREDENTIALS_FILES=/cumulonimbus/.data/.aws/credentials \
    AWS_SHARED_CONFIG_FILES=/cumulonimbus/.data/.aws/config \
    AZURE_CREDENTIALS_FILES=/cumulonimbus/.data/.azure/credentials


# Command
ENTRYPOINT [ "/bin/bash" ]
