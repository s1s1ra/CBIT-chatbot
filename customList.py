from chatterbot.trainers import ListTrainer
import os
import sys
import csv
import time
from dateutil import parser as date_parser
from StatementNew import Statement
from chatterbot.tagging import PosLemmaTagger
from chatterbot import utils
import sw

class Trainer(object):
	"""
	Base class for all other trainer classes.
	:param boolean show_training_progress: Show progress indicators for the
	trainer. The environment variable ``CHATTERBOT_SHOW_TRAINING_PROGRESS``
	can also be set to control this. ``show_training_progress`` will override
	the environment variable if it is set.
	"""

	def __init__(self, chatbot, **kwargs):
		self.chatbot = chatbot

		environment_default = os.getenv('CHATTERBOT_SHOW_TRAINING_PROGRESS', True)
		self.show_training_progress = kwargs.get(
		'show_training_progress',
		environment_default
		)

	def get_preprocessed_statement(self, input_statement):
		"""
		Preprocess the input statement.
		"""
		for preprocessor in self.chatbot.preprocessors:
			input_statement = preprocessor(input_statement)
		return input_statement

	def train(self, *args, **kwargs):
		"""
		This method must be overridden by a child class.
		"""
		raise self.TrainerInitializationException()

class TrainList(Trainer):
	"""
	Allows a chat bot to be trained using a list of strings
	where the list represents a conversation.
	"""

	def train(self, conversation):
		"""
		Train the chat bot based on the provided list of
		statements that represents a single conversation.
		"""
		previous_statement_text = None
		previous_statement_search_text = ''

		statements_to_create = []

		for conversation_count, text in enumerate(conversation):
			if self.show_training_progress:
				utils.print_progress_bar(
				'List Trainer',
				conversation_count + 1, len(conversation)
				)

			statement_search_text = sw.remove(text)

			statement = self.get_preprocessed_statement(
			Statement(
			text=text,
			in_response_to=previous_statement_text,
			search_in_response_to=previous_statement_search_text,
			conversation='training'
			)
			)
			if previous_statement_text is not None: statements_to_create.append(statement)
			previous_statement_text = statement.text
			previous_statement_search_text = statement_search_text

		self.chatbot.storage.create_many(statements_to_create)
