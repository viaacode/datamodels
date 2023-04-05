ARG PREFECT_VERSION
FROM prefecthq/prefect:${PREFECT_VERSION}-python3.9
ARG TRIPLY_GITLAB_TOKEN
ENV TOKEN=${TRIPLY_GITLAB_TOKEN}
COPY prefect-flow-datamodel-etl/requirements.txt .
RUN pip3 install -r requirements.txt --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple --trusted-host do-prd-mvn-01.do.viaa.be
ENV NODE_VERSION=18.13.0
RUN apt-get update
RUN apt-get -y install curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
ADD prefect-flow-datamodel-etl/triply-etl /opt/prefect/triply-etl
WORKDIR /opt/prefect/triply-etl
RUN npm install -g yarn
RUN yarn add @triplyetl/etl --ignore-engines
ADD prefect-flow-datamodel-etl/flows /opt/prefect/flows
ADD description /opt/prefect/description
ADD education /opt/prefect/education
ADD events /opt/prefect/events
ADD objects /opt/prefect/objects
ADD ontologies /opt/prefect/ontologies
ADD organizations /opt/prefect/organizations
ADD terms /opt/prefect/terms
