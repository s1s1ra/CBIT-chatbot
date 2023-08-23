from flask import Flask, render_template, request
from custom import Chaitu
from chatterbot.trainers import ChatterBotCorpusTrainer
from BMatch import BestMatch
from Compare import jaccard_similarity
from chatterbot.response_selection import get_first_response
#from chatterbot.trainers import ListTrainer
from customList import TrainList
import xlrd

# Give the location of the file
loc = ("/Users/sisira/Desktop/vir/info.xlsx")

# To open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

app = Flask(__name__)

bot = Chaitu("Chaitu",logic_adapters=[
        "BMatch.BestMatch"
    ])
trainer = TrainList(bot)

for i in range(sheet.nrows):
	trainer.train([
	sheet.cell_value(i,0),
	sheet.cell_value(i,1),
	])

#trainer = ChatterBotCorpusTrainer(bot)
#trainer.train("chatterbot.corpus.english.greetings")

@app.route("/")
def home():
    return render_template("home.html")
@app.route("/get")
def get_bot_response():
	userText = request.args.get('msg') #userText is what the user types
	return str(bot.get_response(userText))
if __name__ == "__main__":
	app.run()
