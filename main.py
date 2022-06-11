from requests_html import HTMLSession
from pprint import pprint
import mysql.connector
import re



def connect_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="qsearchdb"
    )
    return mydb


# Giving a base 'url'
url = 'https://www.qoqa.ch/fr'

session = HTMLSession()
r = session.get(url)


def get_links(url):
    r.html.render()
    tab_pos = r.html.find('#site-header-wrapper > header > div > div > div.website-preview-bar', first=True)
    tab_list = tab_pos.find('ul', first=True)
    links = tab_list.absolute_links
    links.add(url)
    return links


def scrap(link):
    try:

        # Make request, load JS
        r = session.get(link)
        r.html.render()

        # Figure out if is sold out and get HTML accordingly
        is_soldout = 0
        offer = r.html.find('#offer-titles', first=True)

        if not offer:
            is_soldout = 1
            soldout = r.html.find('#offer-titles-over', first=True)

        # Get price and background image (independent of soldout)
        price = r.html.find('#offer-price', first=True)
        container = r.html.find('body > div.content > div.offer__container', first=True)
        img = container.find('picture > img.slider__img', first=True)
        img_link = img.attrs["src"]
        print(img_link)

        # If is soldout get title and description according to new HTML
        if is_soldout:
            title = soldout.find('h1', first=True)
            descrip = soldout.find('h2', first=True)
        else:
            title = offer.find('#offer-titles > h1', first=True)
            descrip = offer.find('#offer-titles > h2', first=True)


        # Check if offer has description if not, add description msg
        if descrip:
            # Transform into text only
            descrip = descrip.text
        else:
            descrip = "Pas de description"

        # Create line with title, description, price, links and tell if it is sold-out
        scrapinfo = (title.text, descrip, price.text, link, img_link, is_soldout)

        # call store function give it line with title, description, price, links and tell if it is sold-out
        store_scrapper_info(scrapinfo)

        print(link)
        print(scrapinfo)
        print('%%%%%%%%%%%%%%%%%%%%%%%%%')
    except Exception:
        pprint(Exception)
        print("Impossible: " + link)
        print('%%%%%%%%%%%%%%%%%%%%%%%%%')


def store_scrapper_info(scrapinfo):
    # Connect to db and generate cursor
    mydb = connect_database()
    mycursor = mydb.cursor()
    # Create query and execute it with cursor
    sql = "INSERT INTO t_offers (Offer, OfferDescription, Price, OfferLink, OfferImgLink, IsSoldout) VALUES (%s, %s, %s, %s, %s, %s)"

    mycursor.execute(sql, scrapinfo)
    mydb.commit()

    # get the auto incremented id
    qoqa_offer_id = mycursor.lastrowid

    # get all searchwords from  "t_Searchwords" table
    mycursor.execute("SELECT * FROM t_searchwords")

    all_searchwords = mycursor.fetchall()

    # for each searchword, check if exists in last qoqaOffer
    for kw in all_searchwords:
        word = kw[1]
        searchword_id = kw[0]

        # if exists, create match relation, to relate searchword with qoqaOffer by inserting them in t_matches table
        match = re.findall(word, scrapinfo[0], re.IGNORECASE)

        if match:
            print('there is a match')
            sql = "INSERT INTO t_matches (fk_User, fk_SearchWord, fk_Offer) values (%s,%s,%s)"
            val = (3, searchword_id, qoqa_offer_id)
            mycursor.execute(sql, val)

            mydb.commit()
            print('match commited')
        else:
            print(word + ' no match')


if __name__ == '__main__':

    links = get_links(url)

    for i in links:
        scrap(i)




