from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging

## configuration of the Data Ingestion Config

from network_security.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig,DataValidationConfig,DataTransformationConfig

from network_security.components.data_ingestion import DataIngestion
from network_security.components.data_validation import DataValidation
from network_security.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from network_security.components.data_transformation import DataTransformation

import sys

from network_security.components.model_trainer import ModelTrainer
from network_security.entity.config_entity import ModelTrainerConfig


if __name__=="__main__":
    try:
        trainingpipelineconfig =  TrainingPipelineConfig()
        
        
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")
        print(dataingestionartifact)
        
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(data_validation_config,dataingestionartifact)
        logging.info("Initiate the data Validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)
        
        
        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        logging.info("data Transformation started")
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("data Transformation completed")
        
        logging.info("Model Training sstared")
        model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model__trainer()
        logging.info(f"{model_trainer_artifact}")
        logging.info("Model Training artifact created")
        
        
    except Exception as e:
        raise NetworkSecurityException(e,sys)