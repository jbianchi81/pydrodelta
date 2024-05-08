import yaml

class Base():
    """An abstract class"""
    @classmethod
    def load(cls, file : str):
        """Load configuration from yaml file

        Args:
            file (str): path of yaml configuration file

        Returns:
            Plan: an object of this class according to the provided configuration
        """
        t_config = yaml.load(open(file),yaml.CLoader)
        return cls(**t_config)