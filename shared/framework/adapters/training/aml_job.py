import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, Command
from azure.ai.ml.constants import AssetTypes

sub, rg, ws = os.environ["AZURE_SUBSCRIPTION_ID"], os.environ["AZURE_RESOURCE_GROUP"], os.environ["AZURE_ML_WORKSPACE"]
ml = MLClient(DefaultAzureCredential(), sub, rg, ws)

env = Environment(name="lora-train", conda_file="environment.yml", image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04")
ml.environments.create_or_update(env)

job = Command(
    code=".",
    command="python train_lora.py --base_model $BASE --output_dir ./outputs --legend $LEGEND --dataset_path $DATASET",
    environment=env,
    compute=os.environ["AML_COMPUTE"],
    inputs={},
    outputs={"model": {"type": AssetTypes.URI_FOLDER, "path": "azureml://datastores/workspaceblobstore/paths/models/${LEGEND}"}},
    environment_variables={"BASE": os.environ["BASE_MODEL"], "DATASET": os.environ["DATASET_PATH"], "LEGEND": os.environ["LEGEND"]}
)
returned = ml.jobs.create_or_update(job)
print(returned.name)
