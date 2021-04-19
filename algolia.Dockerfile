FROM node:lts-alpine3.13

RUN echo '{"scripts":{"algolia": "atomic-algolia"}}' > package.json
RUN npm install atomic-algolia