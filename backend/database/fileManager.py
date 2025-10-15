from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
class Savable:
    @abstractmethod
    def save(self) -> str:
        raise Exception(f"Save not implemented for {self}")
    def load(self, loaded_data:dict|str):
        raise Exception(f"Load not implemented for {self}")
    @staticmethod
    def toJSON(data: dict) -> str:
        return FileManager.toJSON(data)
    @staticmethod
    def fromJSON(data: str) -> dict:
        return FileManager.fromJSON(data)
        
class FileManager:
    FILE_ENCODING = "utf-8"
    def writeToFile(self, file_name: str, contents: str):
        try:
            with open(file_name, "w", encoding=self.FILE_ENCODING) as f:
                f.write(contents)
        except Exception as e:
            raise IOError(f"Failed to write to {file_name}: {e}")

    def readFromFile(self, file_name: str) -> str:
        try:
            with open(file_name, "r", encoding=self.FILE_ENCODING) as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read from {file_name}: {e}")
        
    def saveJSON(self, file_name: str, data: dict):
        """Save a dictionary as JSON using Savable.toJSON."""
        json_str = self.toJSON(data)
        self.writeToFile(file_name, json_str)

    def loadJSON(self, file_name: str) -> dict:
        """Load a dictionary from JSON using Savable.fromJSON."""
        json_str = self.readFromFile(file_name)
        return self.fromJSON(json_str)

    def saveSavable(self, file_name: str, obj: Savable):
        """Save a Savable object to a file as JSON."""
        json_str = obj.save()
        self.writeToFile(file_name, json_str)

    def loadSavable(self, file_name: str, obj: Savable):
        """Load JSON from a file and pass it to a Savable object."""
        json_str = self.readFromFile(file_name)
        data = Savable.fromJSON(json_str)
        obj.load(data)
    @staticmethod
    def toJSON(data: dict) -> str:
        return json.dumps(data) #Ensures consistent saving / loading parameters
    @staticmethod
    def fromJSON(data: str) -> dict:
        return json.loads(data)