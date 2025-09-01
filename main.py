from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging

## configuration of the Data Ingestion Config

from network_security.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig

from network_security.components.data_ingestion import DataIngestion
import sys


if __name__=="__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()
        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion = data_ingestion.initiate_data_ingestion()
        logging.info(f"Data ingestion artifact: {data_ingestion}")
        
        print(data_ingestion)
        
    except Exception as e:
        raise NetworkSecurityException(e,sys)