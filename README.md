# Indexing Confluence with Vector Search on Vertex AI

## Overview
This repository provides a solution to index Confluence documents and enable natural language querying using Google Cloud's Vertex AI Vector Search. The project leverages a private and secure infrastructure setup, using CloudRun for containerized deployments.

## Documentation
* [Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview?hl=es-419)
* [Cloud Run](https://cloud.google.com/run/?hl=es)

## Prerequisites
- Python
- GCP Account
- Google Cloud SDK configured
- Terraform
- Docker

## Structure
```bash
gcp-vertexai-vectorsearch/
├── code
│   ├── app.py
│   ├── confluence_export.py
│   ├── constants.py
│   ├── Dockerfile
│   ├── load_docs.py
│   ├── rag_chat.py
│   ├── rag.py
│   ├── requirements.txt
│   ├── secrets_engine.py
│   └── vector_db_loader.py
├── infra
│   ├── .env
│   ├── cloudrun.tf
│   ├── network.tf
│   ├── outputs.tf
│   ├── variables.tf
│   ├── versions.tf
│   └── vertex.tf
├── .gitignore
└── README.md
```

## Installation

1. Configure docker location: 

   ```bash
   gcloud auth configure-docker europe-west4-docker.pkg.dev
   ```

2. Export your credentials, replace with your correct values:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="your_credentials_file.json"
   export TF_VAR_project_id="my_gcp_project"
   export CONFLUENCE_URL="my_confluence_url"
   export COMPANY="my_company"
   export SUPPORT_MAIL="my_support_mail"
   ```

3. Create a Confluence token and put it in .env file inside infra folder.

4. Create infra:

   ```bash
   terraform -chdir="./infra" init -upgrade
   terraform -chdir="./infra" apply --auto-approve
   ```

5. Create and push Docker Image to GCP:

   ```bash
   export INDEX_ID="$(terraform -chdir="./infra" output -raw index_id)"
   export INDEX_ENDPOINT_ID="$(terraform -chdir="./infra" output -raw index_endpoint_id)"
   export REPOSITORY_ID="$(terraform -chdir="./infra" output -raw repository_id)"
   export CONTAINER="cloudrun-vertex:latest"
   cd ./code
   docker buildx build \
   --build-arg project_id=${TF_VAR_project_id} \
   --build-arg index_id=${INDEX_ID} \
   --build-arg index_endpoint_id=${INDEX_ENDPOINT_ID} \
   --build-arg confluence_url=${CONFLUENCE_URL} \
   --build-arg company=${COMPANY} \
   --build-arg support_mail=${SUPPORT_MAIL} \
   --platform linux/amd64 -t ${CONTAINER} .
   docker tag ${CONTAINER} europe-west4-docker.pkg.dev/${TF_VAR_project_id}/${REPOSITORY_ID}/${CONTAINER}
   docker push europe-west4-docker.pkg.dev/${TF_VAR_project_id}/${REPOSITORY_ID}/${CONTAINER}
   cd ..
   ```

6. Create CloudRun with terraform and get the URI:

   ```bash
   terraform -chdir="./infra" apply --auto-approve --var create_cloudrun=true
   export CLOUDRUN_URI="$(terraform -chdir="./infra" output -raw cloudrun_uri)"
   ```

## Local calls with curl

1. Update Index with your different page ids from Confluence, only parent page_ids because it is recursive:

   ```bash
   curl ${CLOUDRUN_URI}/update_index \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
     -d '{
       "page_ids": [page_id1, page_id2, ...],
       "is_complete_overwrite": "False"
     }'
   ```

2. Ask questions:

   ```bash
   curl ${CLOUDRUN_URI}/chatbot \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "¿Put_your_question_here?"
     }'

## (Optional) Local calls with UI

1. Create Docker container with Streamlit app:

   ```bash
   cd local_app
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   cd ..
   ```

2. Open your browser in http://localhost:8501/.

## Clean resources

1. Clean Resources:

   ```bash
   terraform -chdir="./infra" destroy --auto-approve
   ```

   > [!IMPORTANT]  
   > It may happen that Google takes time to release the service connection network, and the destroy may fail. In such a case, wait 5-10 minutes and re-launch the destroy.
