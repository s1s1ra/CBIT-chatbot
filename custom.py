import logging
from chatterbot.storage import StorageAdapter
from LogicNew import ChaituLogic
from searching import IndexedTextSearch
from StatementNew import Statement
from chatterbot import utils
from chatterbot import ChatBot


class Chaitu(ChatBot):
    """
    A conversational dialog chat bot.
    """

    def __init__(self, name, **kwargs):
        self.name = name

        storage_adapter = kwargs.get('storage_adapter', 'StorageNew.ChaituStore')

        self.storage = utils.initialize_class(storage_adapter, **kwargs)

        primary_search_algorithm = IndexedTextSearch(self, **kwargs)

        self.search_algorithms = {
            primary_search_algorithm.name: primary_search_algorithm
        }

        logic_adapters = kwargs.get('logic_adapters', [
            'chatterbot.logic.BestMatch'
        ])

        # Check that each adapter is a valid subclass of it's respective parent
        utils.validate_adapter_class(storage_adapter, StorageAdapter)

        # Logic adapters used by the chat bot
        self.logic_adapters = []


        for adapter in logic_adapters:
            utils.validate_adapter_class(adapter, ChaituLogic)
            logic_adapter = utils.initialize_class(adapter, self, **kwargs)
            self.logic_adapters.append(logic_adapter)

        preprocessors = kwargs.get(
            'preprocessors', [
                'chatterbot.preprocessors.clean_whitespace'
            ]
        )

        self.preprocessors = []

        for preprocessor in preprocessors:
            self.preprocessors.append(utils.import_module(preprocessor))

        self.logger = kwargs.get('logger', logging.getLogger(__name__))

        # Allow the bot to save input it receives so that it can learn
        self.read_only = kwargs.get('read_only', False)

        if kwargs.get('initialize', True):
            pass#self.initialize()




    def get_response(self, statement=None, **kwargs):
        """
        Return the bot's response based on the input.

        :param statement: An statement object or string.
        :returns: A response to the input.
        :rtype: Statement
        """
        additional_response_selection_parameters = kwargs.pop('additional_response_selection_parameters', {})

        if isinstance(statement, str):
            kwargs['text'] = statement

        if statement is None and 'text' not in kwargs:
            raise self.ChatBotException(
                'Either a statement object or a "text" keyword '
                'argument is required. Neither was provided.'
            )

        if hasattr(statement, 'text'):
            data = statement.serialize()
            data.update(kwargs)
            kwargs = data

        if isinstance(statement, dict):
            statement.update(kwargs)
            kwargs = statement

        input_statement = Statement(**kwargs)

        # Preprocess the input statement
        for preprocessor in self.preprocessors:
            input_statement = preprocessor(input_statement)

        response = self.generate_response(input_statement, additional_response_selection_parameters)



        if not self.read_only:

            error_responses_list=[
                "I'm sorry, I do not understand",
                "I'm afraid I cannot comprehend your query",
                "Apologies, your query is beyond my abilities at the moment"
            ]
            # Save the response generated for the input
            if response.text not in error_responses_list :
                self.storage.create(
                    text=response.text,
                    in_response_to=response.in_response_to,
                    conversation=response.conversation,
                    persona=response.persona
                )

        return response



    def generate_response(self, input_statement, additional_response_selection_parameters=None):
        """
        Return a response based on a given input statement.

        :param input_statement: The input statement to be processed.
        """
        results = []
        result = None
        max_confidence = -1

        for adapter in self.logic_adapters:
            if adapter.can_process(input_statement):


                output = adapter.process(input_statement, additional_response_selection_parameters)

                results.append(output)

                self.logger.info(
                    '{} selected "{}" as a response with a confidence of {}'.format(
                        adapter.class_name, output.text, output.confidence
                    )
                )

                if output.confidence > max_confidence:
                    result = output
                    max_confidence = output.confidence
            else:
                self.logger.info(
                    'Not processing the statement using {}'.format(adapter.class_name)
                )

        '''class ResultOption:
            def __init__(self, statement, count=1):
                self.statement = statement
                self.count = count

        # If multiple adapters agree on the same statement,
        # then that statement is more likely to be the correct response
        if len(results) >= 3:
            result_options = {}
            for result_option in results:
                result_string = result_option.text + ':' + (result_option.in_response_to or '')

                if result_string in result_options:
                    result_options[result_string].count += 1
                    if result_options[result_string].statement.confidence < result_option.confidence:
                        result_options[result_string].statement = result_option
                else:
                    result_options[result_string] = ResultOption(
                        result_option
                    )

            most_common = list(result_options.values())[0]

            for result_option in result_options.values():
                if result_option.count > most_common.count:
                    most_common = result_option

            if most_common.count > 1:
                result = most_common.statement'''

        response = Statement(
            text=result.text,
            in_response_to=input_statement.text,
            conversation=input_statement.conversation,
            persona='bot:' + self.name
        )

        response.confidence = result.confidence

        return response



    class ChatBotException(Exception):
        pass
