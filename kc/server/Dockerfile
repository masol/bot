FROM andreysenov/node-gyp as pvapi

LABEL version="0.0.1"
LABEL description="prodvest Fastify (Node.js) webapp Docker Image"
LABEL maintainer="Masol.li <lizhutang@spolo.org>"

# update packages, to reduce risk of vulnerabilities
# ENV PYTHONUNBUFFERED=1
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
# RUN python3 -m ensurepip
# RUN pip3 install --no-cache --upgrade pip setuptools

USER root

# set a non privileged user to use when running this image
RUN addgroup -S webapi && adduser -G webapi -s /bin/bash -h /opt/srv -S webapi
RUN npm config set registry https://registry.npmmirror.com/
RUN yarn config set registry https://registry.npmmirror.com/
# set right (secure) folder permissions
RUN mkdir -p /opt/srv/node_modules && chown -R webapi:webapi /opt/srv && chown -R webapi:webapi /home/node

RUN npm install -g fastify
USER webapi
WORKDIR /opt/srv

# set default node env
#ARG NODE_ENV=development
ARG NODE_ENV=production
# to be able to run tests (for example in CI), do not set production as environment
ENV NODE_ENV=${NODE_ENV}

ENV NPM_CONFIG_LOGLEVEL=warn

# copy project definition/dependencies files, for better reuse of layers
COPY --chown=webapi:webapi package*.json ./



# install dependencies here, for better reuse of layers
RUN yarn install


# copy all sources in the container (exclusions in .dockerignore file)
COPY --chown=webapi:webapi . .

# build/pack binaries from sources

# This results in a single layer image
# FROM node:lts-alpine AS release
# COPY --from=builder /dist /dist

# exposed port/s
EXPOSE 3000

# add an healthcheck, useful
# healthcheck with curl, but not recommended
# HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1
# healthcheck by calling the additional script exposed by the plugin
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s CMD npm run healthcheck-manual

# ENTRYPOINT [ "node" ]
# CMD [ "npm", "start" ]
# CMD [ "fastify", "start", "-l info", "-o", "/opt/srv/app.js" ]
CMD ["node","/opt/srv/start.js"]

# end.