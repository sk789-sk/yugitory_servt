


class ValidationError(Exception):
    def __init__(self, parameter, value, message="Invalid value"):
        
        self.parameter = parameter
        self.value = value

        self.message = f"{message} for parameter {parameter}"
        super().__init__(self.message)