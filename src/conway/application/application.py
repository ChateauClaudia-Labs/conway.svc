import abc

class Application(abc.ABC):

    def __init__(self, logger):
        '''
        This class is not supposed to be a singleton, constructed by static methods in concrete derived
        classes. Should not be constructed directly.
        It aims to group some global pluggable components that should be accessible from anywhere in code.
        '''
        if not Application._singleton_app is None:
            raise RuntimeError("An attempt was made to initialize an already initialized Application, which is not allowed")
        
        self.logger                             = logger

        Application._singleton_app              = self

    def log(self, message, log_level, stack_level_increase=0, show_caller=True):
        self.logger.log(message, log_level, stack_level_increase, show_caller=show_caller)

    _singleton_app                              = None

    def app():
        if Application._singleton_app is None:
            raise RuntimeError("An attempt was made access an Application before it is initialized")

        return Application._singleton_app