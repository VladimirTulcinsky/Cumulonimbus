FROM python:3.12-slim

# Copy helper scripts and banner to container
ADD docker/dependencies /root/bin
COPY docker/motd.sh /root/motd.sh

# Install required software
RUN /bin/bash -c "/root/bin/install-prereqs.sh" \
    && /bin/bash -c "/root/bin/install-aws2.sh" \
    && /bin/bash -c "/root/bin/install-azure.sh" \
    && rm -rf /root/bin \
    && chmod +x /root/motd.sh \
    && echo 'source /root/motd.sh' >> /root/.bashrc

# Install Cumulonimbus
COPY ./app /root/app
WORKDIR /root/app
RUN chmod +x /root/app/cnimbus.py \
    && ln -s /root/app/cnimbus.py /usr/local/bin/cnimbus

# Set path to credentials file
ENV AWS_SHARED_CREDENTIALS_FILES=/cumulonimbus/.data/.aws/credentials \
    AWS_SHARED_CONFIG_FILES=/cumulonimbus/.data/.aws/config \
    AZURE_CREDENTIALS_FILES=/cumulonimbus/.data/.azure/credentials

# Command
ENTRYPOINT [ "/bin/bash" ]
