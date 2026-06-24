# gatekeeper_chain — ACR scenario image. The player is granted AcrPull by the
# gatekeeper, pulls this image, and finds TWO plaintext secrets hidden two ways:
#
#   (decoy)  a runtime config file present in the container  -> found by running
#            it, but it is an old rotated value + a breadcrumb.
#   (real)   a credential written into one layer and "deleted" in a later layer
#            -> gone from the final filesystem but still in the image history /
#            earlier layer's tarball. This is the flag that unlocks the next stage.
#
# Built FROM a Microsoft Container Registry base so the build never pulls from
# Docker Hub.
FROM mcr.microsoft.com/cbl-mariner/base/core:2.0

LABEL maintainer="platform-team@cumulonimbus.local"

# --- decoy secret in a runtime file (found by running the container) ----------
RUN mkdir -p /app/config && \
    printf '%s\n' \
      '# application runtime configuration' \
      'environment=production' \
      '# NOTE: the deploy token was embedded at build time and then removed in a' \
      '#       later build step. Old value kept below for rollback.' \
      'legacy_deploy_token=CUMULONIMBUS{r0t4t3d_t0k3n_n0t_th3_fl4g}' \
      'next_hop=Recover the REAL token from an earlier image layer, then submit it to the gatekeeper to unlock the Container Instance.' \
      > /app/config/app.config

# --- real secret written into a layer, then deleted in a LATER layer ---------
RUN printf 'DEPLOY_TOKEN=CUMULONIMBUS{4CR_1m4g3_L4y3r_S3cr3t_Ch41n}\n' > /root/.deploy_token
RUN rm -f /root/.deploy_token

WORKDIR /app
CMD ["sh", "-c", "echo 'cumulonimbus app running'; sleep 3600"]
