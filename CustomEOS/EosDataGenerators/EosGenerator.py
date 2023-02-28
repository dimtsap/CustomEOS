from abc import ABC, abstractmethod


class EosGenerator(ABC):
    pass

    @abstractmethod
    def run_once_and_generate_eos_file(self):
        pass