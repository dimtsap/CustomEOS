from abc import ABC, abstractmethod


class HyadesRunner(ABC):
    
    @abstractmethod
    def run_and_retrieve_output():
        pass