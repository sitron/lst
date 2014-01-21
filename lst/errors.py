class LstError(Exception): pass
class NotFoundError(LstError): pass
class FileNotFoundError(LstError): pass
class SyntaxError(LstError): pass
class InputParametersError(LstError): pass
class DevelopmentError(LstError): pass
class IOError(LstError): pass
