from nltk.corpus import stopwords as swa
from nltk.tokenize import word_tokenize
import string

def remove(text):
	text=text.lower()
	stopwords=list(swa.words('english'))
	stopwords.remove('what')
	stopwords.remove('where')
	stopwords.remove('up')
	stopwords.append('tell')
	for i in string.punctuation:
		stopwords.append(i)
	text=word_tokenize(text)
	tokens_without_sw = [word for word in text if not word in stopwords]
	return (" ").join(tokens_without_sw)
