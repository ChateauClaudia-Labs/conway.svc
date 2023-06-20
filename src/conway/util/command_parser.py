

class CommandParser():
    '''
    Utility class used to correctly parse strings that correspond to CLI commands
    


    '''
    def __init__(self):
        pass
    
    def get_argument_list(self, command):
        '''
        Tokenizes a CLI command and returs its underlying argument list, with particular support for the "tricky case" when 
        a command includes arguments with spaces surrounded in quotes.

        For example, given the command

                'git commit -m "[task-conway-2] Set up branch management preliminaries"'

        the correct argument list (and what is returned by this method) would be:

            ['git',
            'commit',
            '-m',
            '"[task-conway-2] Set up branch management preliminaries"']

        and not 

            ['git',
            'commit',
            '-m',
            '"[task-conway-2]',
            'Set',
            'up',
            'branch',
            'management',
            'preliminaries"']

        :param str command: CLI command to tokenize
        :return: argument list for the command
        :rtype: list[str]
        '''
        # The comments below explain the algorithm with the example where the command is
        #
        #           'git commit -m "[task-conway-2] Set up branch management preliminaries"'
        #
        SPACE                                   = " "
 
        # On a first pass, we tokenize by space, even if splits a single argument like 
        # "[task-conway-2] Set up branch management preliminaries" into pieces.
        tokens                                  = command.split(SPACE)

        '''
        So now tokens is something like this, and we want to traverse the token and recombine together
        the ones that belong to a common argument. In this example, we want to re-combine tokens wit index 3+ into a single string.
                    ['git',
                    'commit',
                    '-m',
                    '"[task-conway-2]',
                    'Set',
                    'up',
                    'branch',
                    'management',
                    'preliminaries"']

        The algorithm is to use a state machine with two states. The machine will traverse the tokens one at a time,
        and the logic to examine a token is dependent on which state the machine is in.

        The two states are:

        * _SubstringState: represents the condition of already having entered a consecutive groups of tokens that
                            are part of the same substring.

        * _UsualState: represents the condition of not having yet entered a token that might be part of a bigger substring.
        
        Each state handles the next token, and if appropriate, transition to the other state if needed.

        '''
        machine                                 = self._StateMachine(tokens)
        machine.run()
        return machine.args


    class _StateMachine():

        SUBSTRING_DELIMETERS = ["'", "\""]

        def __init__(self, token_list):
            self.token_list                     = token_list
            self.token_idx                      = 0
            self.state                          = self._UsualState(machine=self)
            self.args                           = []

        def run(self):
            '''
            Progress one token
            '''
            while self.token_idx < len(self.token_list):
                self.state.advance()
            
        class _AbstractState():
            def __init__(self, machine):
                self.machine                    = machine
                self.next_token                 = None

            def advance(self):
                M                               = self.machine
                self.next_token                 = M.token_list[M.token_idx]
                M.token_idx                     += 1

        class _SubstringState(_AbstractState):
            def __init__(self, machine, initial_token):
                super().__init__(machine)
                self.substring                  = initial_token
                self.delimeter                  = initial_token[0]

            def advance(self):
                super().advance()
                if len(self.next_token.strip()) == 0:
                    return # Ignore the token
                elif self.at_substring_end():
                    self.close_substring()
                else:
                    self.augment_substring()
                
            def close_substring(self):
                M                               = self.machine
                self.substring                  += " " + self.next_token
                M.args.append(self.substring)
                M.state                         = M._UsualState(M)
            
            def augment_substring(self):
                self. substring += " " + self.next_token 

            def at_substring_end(self):
                if self.next_token[-1]==self.delimeter:
                    return True
                else:
                    return False
                
        class _UsualState(_AbstractState):
            def __init__(self, machine):
                super().__init__(machine)

            def advance(self):
                super().advance()
                if len(self.next_token.strip()) == 0:
                    return # Ignore the token
                elif self.at_substring_start():
                    self.start_substring()
                else:
                    self.add_arg()

            def start_substring(self):
                M                               = self.machine
                M.state                         = M._SubstringState(M, self.next_token)
            
            def add_arg(self):
                M                               = self.machine
                M.args.append(self.next_token) 

            def at_substring_start(self):
                M                               = self.machine
                if self.next_token[0] in M.SUBSTRING_DELIMETERS:
                    return True
                else:
                    return False

    