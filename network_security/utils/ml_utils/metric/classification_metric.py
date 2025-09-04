from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging
from network_security.entity.artifact_entity import ClassificationMetricArtifact
import os,sys
from sklearn.metrics import precision_score,recall_score,f1_score

def get_classification_score(y_true,y_pred)->dict:
    try:
        model_f1_score = f1_score(y_true,y_pred)
        model_precision_score = precision_score(y_true,y_pred)
        model_recall_score = recall_score(y_true,y_pred)
        
        get_classification_score = ClassificationMetricArtifact(f1_score=model_f1_score,
                                                             precision_score=model_precision_score,
                                                             recall_score=model_recall_score
                                                             )
        return get_classification_score
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
