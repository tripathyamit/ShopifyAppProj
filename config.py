class Config(object):
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBigg"
    HOST = "dc7708e6.ngrok.io"
    SHOPIFY_CONFIG = {
        'API_KEY': '',
        'API_SECRET': '',
        'APP_HOME': 'http://' + HOST,
        'CALLBACK_URL': 'http://' + HOST + '/install',
        'REDIRECT_URI': 'http://' + HOST + '/connect',
        'SCOPE': 'read_products,read_collection_listings,read_shipping,write_shipping,read_checkouts,write_checkouts,write_orders,read_customers'
    }
