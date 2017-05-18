class CommandExecutor:
    def __init__(self, executor, arguments_types=()):
        self.executor = executor
        self.arguments_types = arguments_types
        self.arguments = []

    def validate(self, arguments):
        self.arguments = arguments
        self.validate_number_of_args()
        self.validate_types_of_arguments()

    def validate_number_of_args(self):
        if len(self.arguments_types) != len(self.arguments):
            raise Exception('Wrong quantity of parameters')

    def validate_types_of_arguments(self):
        transformed_args = []
        for arg, arg_type in zip(self.arguments, self.arguments_types):
            if not isinstance(arg, arg_type):
                try:
                    new_arg = arg_type(arg)
                    transformed_args.append(new_arg)
                except:
                    raise TypeError(
                        'Argument {name} is of wrong type: {got}. Expected {expect}'.format(
                            name=arg,
                            got=type(arg),
                            expect=arg_type,
                        )
                    )
            else:
                transformed_args.append(arg)
        self.arguments = transformed_args

    def __call__(self, *args, **kwargs):
        self.executor(*self.arguments)
