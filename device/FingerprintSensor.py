import time
from pyfingerprint.pyfingerprint import PyFingerprint
from dataclasses import dataclass
from utils.utils import get_logger
import hashlib
import tempfile

@dataclass
class FingerprintSensor:
    com_port: str
    fingerprint_sensor: PyFingerprint = None
    logger = get_logger(name=__name__)


    def setup_sensor(self):
        try:
            self.fingerprint_sensor = PyFingerprint(self.com_port, 57600, 0xFFFFFFFF, 0x00000000)
            if (self.fingerprint_sensor.verifyPassword() == False):
                raise ValueError('The given fingerprint sensor password is wrong!')
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)
    
    def enroll_fingerprint(self, id):
        pass

    def sensor_details(self) -> str:
        return f"{str(self.fingerprint_sensor.getTemplateCount())}/{str(self.fingerprint_sensor.getStorageCapacity)}"
    
    def enroll_fingerprint(self):
        try:
            self.logger.info('Waiting for finger...')
            while (self.fingerprint_sensor.readImage() == False):
                pass
            self.logger.info('Downloading image (this might take a while)...')
            self.fingerprint_sensor.downloadImage('./data/fingerprint.bmp')
            self.logger.info('Converting image to characteristics...')
            self.fingerprint_sensor.convertImage(0x01)
            self.logger.info('Uploading image...')
            self.fingerprint_sensor.uploadImage(0x01)
            self.logger.info('Searching for template...')
            result = self.fingerprint_sensor.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]

            if (positionNumber >= 0):
                self.logger.info('Template already exists at position #' + str(positionNumber))

            self.logger.info('Remove finger...')
            time.sleep(2)

            self.logger.info('Waiting for same finger again...')
            
            
            while (self.fingerprint_sensor.readImage() == False):
                pass


            self.fingerprint_sensor.convertImage(0x02)

            if (self.fingerprint_sensor.compareCharacteristics() == 0):
                raise Exception('Fingers do not match')
            
            self.fingerprint_sensor.createTemplate()
            
            
            positionNumber = self.fingerprint_sensor.storeTemplate()
            # if (positionNumber == -1):
            #     self.logger.info('No match found!')
            # else:
            #     self.logger.info('Found template at position #' + str(positionNumber))
            #     self.logger.info('The accuracy score is: ' + str(accuracyScore))
            
            # self.fingerprint_sensor.loadTemplate(positionNumber, 0x01)
            # characteristics = self.fingerprint_sensor.downloadCharacteristics(0x01)

            # self.logger.info('SHA-2 hash of template: ' + str(list(characteristics)))
            # self.logger.info('Waiting for finger...')
        except Exception as e:
            self.logger.info('Operation failed!')
            self.logger.info('Exception message: ' + str(e))
            exit(1)
    
    def search_fingerprint(self):
        try:
            self.logger.info('Waiting for finger...')
            while (self.fingerprint_sensor.readImage() == False):
                pass

            self.logger.info('Converting image to characteristics...')
            self.fingerprint_sensor.convertImage(0x01)

            self.logger.info('Searching for template...')
            result = self.fingerprint_sensor.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if (positionNumber == -1):
                self.logger.info('No match found!')
            else:
                self.logger.info('Found template at position #' + str(positionNumber))
                self.logger.info('The accuracy score is: ' + str(accuracyScore))
            
            self.fingerprint_sensor.loadTemplate(positionNumber, 0x01)
            characteristics = self.fingerprint_sensor.downloadCharacteristics(0x01)

            print('SHA-2 hash of template: ' + hashlib.sha256(characteristics).hexdigest())
            
            self.logger.info('Fingerprint matched!')
        except Exception as e:
            self.logger.info('Operation failed!')
            self.logger.info('Exception message: ' + str(e))
            exit(1)

    def delete_fingerprint(self, pos: int):
        try:
            if (self.fingerprint_sensor.deleteTemplate(pos) == True):
                self.logger.info('Template deleted!')
        except Exception as e:
            self.logger.info('Operation failed!')
            self.logger.info('Exception message: ' + str(e))
            exit(1)
    
    def delete_all_fingerprints(self):
        try:
            if (self.fingerprint_sensor.emptyDatabase() == True):
                self.logger.info('Database cleared!')
        except Exception as e:
            self.logger.info('Operation failed!')
            self.logger.info('Exception message: ' + str(e))
            exit(1)
    
    def get_fingerprint_count(self):
        return self.fingerprint_sensor.getTemplateCount()
    
    def download_fingerprint(self):
        try:
            self.logger.info('Waiting for finger...')
            while (self.fingerprint_sensor.readImage() == False):
                pass

            image_destination = tempfile.gettempdir() + '/fingerprint.bmp'
            self.logger.info('Downloading image (this might take a while)...')
            self.fingerprint_sensor.downloadImage(image_destination)
        except Exception as e:
            self.logger.info('Operation failed!')
            self.logger.info('Exception message: ' + str(e))
            exit(1)
        