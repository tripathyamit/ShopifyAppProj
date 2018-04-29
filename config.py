class Config(object):
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBigg"
    HOST = "dc7708e6.ngrok.io"
    SHOPIFY_CONFIG = {
        'API_KEY': 'f0f78f97a5b0b2390357591295ff81cd',
        'API_SECRET': '54bc48af11f66f7847854821281fd556',
        'APP_HOME': 'http://' + HOST,
        'CALLBACK_URL': 'http://' + HOST + '/install',
        'REDIRECT_URI': 'http://' + HOST + '/connect',
        'SCOPE': 'read_products,read_collection_listings,read_shipping,write_shipping,read_checkouts,write_checkouts,write_orders,read_customers'
    }