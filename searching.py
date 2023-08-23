from StatementNew import Statement
import sw

class IndexedTextSearch:
    """
    :param statement_comparison_function: The dot-notated import path
        to a statement comparison function.
        Defaults to ``levenshtein_distance``.

    :param search_page_size:
        The maximum number of records to load into memory at a time when searching.
        Defaults to 1000
    """

    name = 'indexed_text_search'

    def __init__(self, chatbot, **kwargs):
        from Compare import jaccard_similarity

        self.chatbot = chatbot

        self.compare_statements = kwargs.get(
            'statement_comparison_function',
            jaccard_similarity
        )

        self.search_page_size = kwargs.get(
            'search_page_size', 1000
        )

    def search(self, input_statement, **additional_parameters):
        """
        Search for close matches to the input. Confidence scores for
        subsequent results will order of increasing value.

        :param input_statement: A statement.
        :type input_statement: chatterbot.conversation.Statement

        :param **additional_parameters: Additional parameters to be passed
            to the ``filter`` method of the storage adapter when searching.

        :rtype: Generator yielding one closest matching statement at a time.
        """
        self.chatbot.logger.info('Beginning search for close text match')

        input_search_text = sw.remove(input_statement.text)


        search_parameters = {
            'search_text_contains': input_search_text,
            'persona_not_startswith': 'bot:',
            'page_size': self.search_page_size
        }

        if additional_parameters:
            search_parameters.update(additional_parameters)

        statement_list = self.chatbot.storage.filter(**search_parameters);

        #statement_list = self.chatbot.storage.get(**search_parameters)

        closest_match = Statement(text='')
        closest_match.confidence = 0

        self.chatbot.logger.info('Processing search results')

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement);

            if confidence > closest_match.confidence:
                statement.confidence = confidence
                closest_match = statement

                self.chatbot.logger.info('Similar text found: {} {}'.format(
                    closest_match.text, confidence
                ))
                yield closest_match
