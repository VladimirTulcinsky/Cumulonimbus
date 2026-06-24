# Cumulonimbus lab image — secrets hidden two complementary ways:
#
#   (2) RUNTIME FILE  : a config file that exists in the running container, found
#                       by pulling the image and running it interactively. It is
#                       a decoy (an old, rotated token) plus a breadcrumb.
#
#   (3) DELETED LAYER : a credential written into one layer and "removed" in a
#                       later layer. It is gone from the final filesystem, but it
#                       still lives in the image history and in the earlier
#                       layer's tarball. THIS is the real flag.
#
# Lesson: deleting a secret in a later Dockerfile step does NOT remove it from
# the image — every layer is retained and shippable.
FROM alpine:3.18

LABEL org.opencontainers.image.title="cumulonimbus-app"
LABEL maintainer="platform-team@example.com"

# --- (2) Secret sitting in the running container's filesystem ---------------
# Looks like the prize, but it is an old rotated value and a hint to keep going.
RUN mkdir -p /app/config && \
    printf '%s\n' \
      '# application runtime configuration' \
      'environment=production' \
      'db_host=prod-db.internal.example.com' \
      '# NOTE: the registry deploy token was embedded at build time and then' \
      '#       removed in a later build step. Old value kept here for rollback.' \
      'legacy_deploy_token=CUMULONIMBUS{r0t4t3d_t0k3n_n0t_th3_fl4g}' \
      > /app/config/app.config

# --- (3) Secret written into a layer, then deleted in a LATER layer ----------
# The rm strips it from the final image, but the value remains recoverable via
# `docker history --no-trunc` and by extracting this layer with `docker save`.
RUN printf 'DEPLOY_TOKEN=CUMULONIMBUS{4CR_Adm1n_Cr3ds_2_D3l3t3d_L4y3r_S3cr3t}\n' > /root/.deploy_token
RUN rm -f /root/.deploy_token

WORKDIR /app
CMD ["sh", "-c", "echo 'cumulonimbus app running'; sleep 3600"]
