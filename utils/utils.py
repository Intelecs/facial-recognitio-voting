import logging

def get_logger(environment: str = "DEV", name: str = __name__) -> logging.getLogger:
    logger = logging.getLogger(name)
    
    
    if environment != "DEV":
        raise NotImplementedError("Only DEV environment is supported")
    
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(process)d] %(levelname)s : %(message)s', datefmt='%Y-%m-%dT%H:%M:%S %Z')
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(formatter)
    logger.addHandler(logger_handler)
    return logger