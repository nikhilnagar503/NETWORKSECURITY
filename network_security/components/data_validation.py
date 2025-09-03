from network_security.entity.config_entity import DataValidationConfig
from network_security.entity.artifact_entity import DataValidationArtifact,DataIngestionArtifact
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging
import sys
import os
from scipy.stats import ks_2samp
from network_security.utils.main_utils.utils import read_yaml_file,write_yaml_file 
from network_security.constants.training_pipeline import SCHEMA_FILE_PATH
import pandas as pd

class DataValidation:
    def __init__(self,data_validation_config:DataValidationConfig,
                 data_ingestion_artifact:DataIngestionArtifact):
                try:
                        self.data_validation_config=data_validation_config
                        self.data_ingestion_artifact=data_ingestion_artifact
                        self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
                        
                except Exception as e:
                        raise NetworkSecurityException(e,sys)
                    
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame :
        try:
            return pd.read_csv(file_path)
        except Exception as e:  
            raise NetworkSecurityException(e,sys)
        
    
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self._schema_config['columns'])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Dataframe has columns: {dataframe.shape[1]}")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    def detect_dataset_drift(self,base_df:pd.DataFrame,current_df:pd.DataFrame,threshold=0.05)->bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                same_distribution = ks_2samp(d1,d2)
                if same_distribution.pvalue >= threshold:
                    is_found = False 
                else :
                    is_found = True
                    status = False
                report.update({column:{
                    "p_value":float(same_distribution.pvalue),
                    "drift_status":is_found
                }})
                    
                drift_report_file_path = self.data_validation_config.drift_report_file_path
                dir_path = os.path.dirname(drift_report_file_path)
                
                # createte the dir
                os.makedirs(dir_path,exist_ok=True)
                write_yaml_file(file_path = drift_report_file_path,content=report)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
        
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            
            logging.info("Starting data validation")
            
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path
            
            
            
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)
            
            status = self.validate_number_of_columns(train_dataframe)
            if not status:
                raise Exception("Number of columns are not as per the schema in the train dataframe")
            
            status = self.validate_number_of_columns(test_dataframe)
            if not status:
                raise Exception("Number of columns are not as per the schema in the test dataframe")
            
            status = self.detect_dataset_drift(base_df = train_dataframe,current_df = test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)
            
            
            
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True

            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            
            
            
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
