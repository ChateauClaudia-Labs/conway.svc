from enum                                                           import Enum
import re                                                           as _re
import abc                                                           

class DelimeterType (abc.ABC):

    @abc.abstractmethod
    def is_valid(self, input):
        '''
        :param str input: string that must be checked to see if it conforms to the requirements of this
            DelimeterType
        :returns: True if the ``input`` conforms with the requirements for this DelimeterType
        :rtype: bool
        '''

    @abc.abstractmethod
    def tokenize(self, input):
        '''
        Splits ``input`` into a list of alphanumeric tokens and returns it. It raises an exception if
        ``input`` does not comply with the requirements for this DelimeterType.

        :param str input: string to split into tokens according to this DelimeterType. 
        :returns: list of alphanumeric tokens
        :rtype: list[str]
        '''

class UnderscoreDelimeterType(DelimeterType):

    '''
    Represents a delimeter policy whereby string identifiers only use an underscore ("_") as a delimeter,
    with all other characters requireds to be alphanumeric
    '''
    def __init__(self):
        pass

    REGEX                               = _re.compile("^[_a-zA-Z0-9]+$")
    def is_valid(self, input):
        m                               = _re.match(self.REGEX, input)
        return                          False if m is None or not "_" in input else True

    def tokenize(self, input):
        if not self.is_valid(input):
            raise ValueError(f"Invalid input {input}: should be alphanumeric with underscore delimeters")
        tokens                          = input.split("_")
        return tokens
    
class HyphenDelimeterType(DelimeterType):

    '''
    Represents a delimeter policy whereby string identifiers only use an hyphen ("-") as a delimeter,
    with all other characters requireds to be alphanumeric
    '''
    def __init__(self):
        pass

    REGEX                               = _re.compile("^[-a-zA-Z0-9]+$")
    def is_valid(self, input):
        m                               = _re.match(self.REGEX, input)
        return                          False if m is None or not "-" in input else True

    def tokenize(self, input):
        if not self.is_valid(input):
            raise ValueError(f"Invalid input {input}: should be alphanumeric with hyphen delimeters")
        tokens                          = input.split("-")
        return tokens

class CamelDelimeterType(DelimeterType):

    '''
    Represents a delimeter policy whereby string identifiers are only alphanumeric, and a delimeter event
    is considered to happen when a lower case character is followed by an upper case character. For these
    purposes, numerical characters are considered to be lowercase.
    '''
    def __init__(self):
        pass

    REGEX                               = _re.compile("^[a-zA-Z0-9]+$")
    def is_valid(self, input):
        m                               = _re.match(self.REGEX, input)
        return                          False if m is None else True

    def tokenize(self, input):
        if not self.is_valid(input):
            raise ValueError(f"Invalid input {input}: should be alphanumeric")
        tokens                          = []

        next_token                      = ""
        # We navigate each character at a time. Each time we see an upper case, we consider that the start of
        # a new token
        for c in input:
            if self.is_lower(c) or len(next_token)==0:
                next_token              += c
            else:
                tokens.append(next_token)
                next_token              = c
        # Don't forget the last token! (as we exit the above loop, last token wasn't yet added)
        tokens.append(next_token)

        return tokens

    def is_lower(self, text):
        '''
        :param str text: An alphanumeric string
        :return: True if ``text`` is all lowercase, otherwise returns False. Numerical characters are considered lowercase.
        :rtype: bool
        '''
        return                          True if text.lower()==text else False

class CaseUtils():

    '''
    Utility methods to convert across multiple formats for string identifiers used in code.

    For example, consider a string like "CASH_MANAGEMENT". That is considered the "static" format.

    Often it needs to be converted to any of there other formats:

    * Camel case: "cashManagement"

    * Pascal case: "CashManagement"

    * Snake case: "cash_management"

    * Kebab case: "cash-management"

    These class contains utilities to convert from any of these to the others

    Proper operation depends on the following requirements on strings fed as input to conversion methods:

    * Only allowed delimeter characters are "-" and "_"

    * An input string contains at most 1 kind of delimeter. All other characters must be alphanumerical.

    * Strings with no delimeter are assumed to be in Camel format. That is, each transition from a lower case to
      an upper case character is interpreted as implicitly following a delimeter. Since only alphanumerical 
      characters are allowed (other than delimeters), in the above logic it must be clarified what lower case vs
      upper case means for numerical characters. By convention, all numerical characters are treated as if they 
      were lowercase already. Thus, an input string like "my4Var" would be converted to a static format like
      "MY4_VAR"
    '''
    def __init__(self):
        pass

    def as_camel(input):
        '''
        Returns a Camel-case equivalent for ``input``. For example, if the input is "cash-management", it returns
            "cashManagement"

        Raises an exception if ``input`` does not consist exclusively of alphanumeric characters and at most one type of
            delimeter, where valid types are undercore ("_") and hypen ("-")

        :param str input: identifier for which we want a Camel-case equivalent
        :return: a Camel-case equivalent for ``input``. 
        :rtype: str
        '''
        tokens                              = CaseUtils._tokenize(input)
        result                              = tokens[0].lower() + "".join(CaseUtils._token_to_pascal(t) for t in tokens[1:])
        return result
    
    def as_pascal(input):
        '''
        Returns a Pascal-case equivalent for ``input``. For example, if the input is "cash-management", it returns
            "CashManagement"

        Raises an exception if ``input`` does not consist exclusively of alphanumeric characters and at most one type of
            delimeter, where valid types are undercore ("_") and hypen ("-")

        :param str input: identifier for which we want a Pascal-case equivalent
        :return: a Pascal-case equivalent for ``input``. 
        :rtype: str
        '''
        tokens                              = CaseUtils._tokenize(input)
        result                              = "".join(CaseUtils._token_to_pascal(t) for t in tokens)
        return result
    
    def as_snake(input):
        '''
        Returns a Snake-case equivalent for ``input``. For example, if the input is "CASH_MANAGEMENT", it returns
            "cash_management"

        Raises an exception if ``input`` does not consist exclusively of alphanumeric characters and at most one type of
            delimeter, where valid types are undercore ("_") and hypen ("-")

        :param str input: identifier for which we want a Snake-case equivalent
        :return: a Snake-case equivalent for ``input``. 
        :rtype: str
        '''
        tokens                              = CaseUtils._tokenize(input)
        result                              = "_".join([t.lower() for t in tokens])
        return result

    def as_kebab(input):
        '''
        Returns a Kebab-case equivalent for ``input``. For example, if the input is "CASH_MANAGEMENT", it returns
            "cash-management"

        Raises an exception if ``input`` does not consist exclusively of alphanumeric characters and at most one type of
            delimeter, where valid types are undercore ("_") and hypen ("-")

        :param str input: identifier for which we want a Kebab-case equivalent
        :return: a Kebab-case equivalent for ``input``. 
        :rtype: str
        '''
        tokens                              = CaseUtils._tokenize(input)
        result                              = "-".join([t.lower() for t in tokens])
        return result
    
    def as_static(input):
        '''
        Returns a Static-case equivalent for ``input``. For example, if the input is "CashManagement", it returns
            "CASH_MANAGEMENT"

        Raises an exception if ``input`` does not consist exclusively of alphanumeric characters and at most one type of
            delimeter, where valid types are undercore ("_") and hypen ("-")

        :param str input: identifier for which we want a Static-case equivalent
        :return: a Static-case equivalent for ``input``. 
        :rtype: str
        '''
        tokens                              = CaseUtils._tokenize(input)

        result                              = "_".join([t.upper() for t in tokens])
        return result

    def _tokenize(input):
        '''
        Infers what kind of delimeter is used in the ``input`` and uses it to split ``input`` into tokens and return the
        list of tokens.

        :param str input: input to be split into tokens, based on a notion of delimeter notion supported
            by the CaseUtils services

        :returns: list of tokens comprising the input. Each token is guaranteed to only contain alphanumeric characters.
        :rtype: list[str]
        '''
        un                                      = UnderscoreDelimeterType()
        hy                                      = HyphenDelimeterType()
        ca                                      = CamelDelimeterType()

        if un.is_valid(input):
            tokens                              = un.tokenize(input)
        elif hy.is_valid(input):
            tokens                              = hy.tokenize(input)
        elif ca.is_valid(input):
            tokens                              = ca.tokenize(input)
        else:
            raise ValueError(f"Invalid input `{input}`: does not match any of the supported delimeter types")

        return tokens
    
    def _token_to_pascal(token):
        '''
        Expects an alphanumeric token and returns its Pascal equivalent, i.e., first character is capitalized and the
        rest are lowercase.
        '''
        if len(token) == 0:
            return ""
        
        return token[0].upper() + token[1:].lower()