class LstError(Exception): pass
class NotFoundError(LstError): pass
class FileNotFoundError(LstError): pass
class SyntaxError(LstError): pass
