from telegram.ext import Updater
from telegram.ext import CommandHandler
import main

# Give bots token to updater
updater = Updater(token='1709460553:AAHxsXqOmaEtey8QtDwtnEOd9t1yFXXdowA', use_context=True)

dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Checking for matches")
    mydb = main.connect_database()
    mycursor = mydb.cursor()
    # Getting qoqaoffer and keyword trough the matches table using their ID
    mycursor.execute("""SELECT SearchWord, Offer, Price, HarvestDate, OfferLink FROM t_matches m JOIN t_searchWords s ON 
    m.fk_SearchWord = s.pk_SearchWord JOIN t_offers o ON m.fk_Offer = o.pk_Offer""")

    matches = mycursor.fetchall()
    # Check if query harvested something
    if not matches:
        matches = "No matches found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=matches)
    print(matches)
    for match in matches:
        # Parsing content to send in a message
        user_kw = match[0]
        article = match[1]
        article_price = match[2]
        time = match[3]
        link = match[4]

        # Writing message
        context.bot.send_message(chat_id=update.effective_chat.id, text="Le mot " + user_kw + " à été trouvé "
                                                                                              "dans l'article suivant "
                                                                                              ":\n"+ str(link))


if __name__ == '__main__':
    # listening for start method
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # start the Bot
    updater.start_polling()
    updater.idle()
