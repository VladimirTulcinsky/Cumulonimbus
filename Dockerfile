# Pin to Debian bookworm. The floating python:3.12-slim tag moved to Debian
# trixie, for which Microsoft does not publish an azure-cli apt package, breaking
# the build. Pinning keeps the build reproducible and on a supported base.
FROM python:3.12-slim-bookworm

# Copy helper scripts to container
ADD docker/dependencies /root/bin

# Install required software
RUN /bin/bash -c "/root/bin/install-prereqs.sh" \
    && /bin/bash -c "/root/bin/install-aws2.sh" \
    && /bin/bash -c "/root/bin/install-azure.sh" \
    && rm -rf /root/bin

# Banner (kept after installs so changes don't bust the install cache)
COPY docker/motd.sh /root/motd.sh
RUN chmod +x /root/motd.sh \
    && echo 'source /root/motd.sh' >> /root/.bashrc

# Install Cumulonimbus
COPY ./app /root/app
# CTFd assets (compose + the ctfd/azure Terraform) so the shell can deploy the
# persistent Azure scoreboard from inside the container.
COPY ./ctfd /root/ctfd
WORKDIR /root/app
RUN chmod +x /root/app/cnimbus.py \
    && ln -s /root/app/cnimbus.py /usr/local/bin/cnimbus

# Credential file paths are set at runtime by the app (global_variables.py),
# pointing at the per-install .data directory. The previous ENV entries here were
# unused (wrong names/paths) and tripped the SecretsUsedInArgOrEnv build check.

# Command
ENTRYPOINT [ "/bin/bash" ]
