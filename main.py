from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging

## configuration of the Data Ingestion Config

from network_security.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig,DataValidationConfig
from network_security.entity.artifact_entity import DataIngestionArtifact

from network_security.components.data_ingestion import DataIngestion
from network_security.components.data_validation import DataValidation
import sys


if __name__=="__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()
        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        logging.info("Initiate the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info(f"Data ingestion artifact: {data_ingestion}")
        print(dataingestionartifact)
        
        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(data_validation_config,dataingestionartifact)
        logging.info("Initiate the data Validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)
            
        
        
    except Exception as e:
        raise NetworkSecurityException(e,sys)