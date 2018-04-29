from flask import Flask, render_template, request, redirect, Response, session, url_for
from config import Config as cfg
import requests
import json

app = Flask(__name__, template_folder="templates")
app.debug = True
app.secret_key = cfg.SECRET_KEY





@app.route('/register_webhook', methods=['GET'])
def register_webhook():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    payload = {
        "webhook": {
            "topic": "products/update",
            "address": "https://{0}/webhooks".format(cfg.HOST),
            "format": "json"
        }
    }
    response = requests.post("https://" + session.get("shop")
                             + "/admin/webhooks.json",
                             data=json.dumps(payload), headers=headers)

    if response.status_code == 201:

        return render_template('register_webhook.html',
                               webhook_response=json.loads(response.text))
    else:
        return Response(response="{0} - {1}".format(response.status_code,
                                                    response.text), status=200)


@app.route('/install', methods=['GET'])
def install():
    """
    Connect a shopify store
    """
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)

    auth_url = "https://{0}/admin/oauth/authorize?client_id={1}&scope={2}&redirect_uri={3}".format(
        shop, cfg.SHOPIFY_CONFIG["API_KEY"], cfg.SHOPIFY_CONFIG["SCOPE"],
        cfg.SHOPIFY_CONFIG["REDIRECT_URI"]
    )
    print("Debug - auth URL: ", auth_url)
    return redirect(auth_url)


@app.route('/connect', methods=['GET'])
def connect():
    if request.args.get("shop"):
        params = {
            "client_id": cfg.SHOPIFY_CONFIG["API_KEY"],
            "client_secret": cfg.SHOPIFY_CONFIG["API_SECRET"],
            "code": request.args.get("code")
        }
        resp = requests.post(
            "https://{0}/admin/oauth/access_token".format(
                request.args.get("shop")
            ),
            data=params
        )

        if 200 == resp.status_code:
            resp_json = json.loads(resp.text)

            session['access_token'] = resp_json.get("access_token")
            session['shop'] = request.args.get("shop")

            # return render_template('welcome.html', from_shopify=resp_json)
            # return render_template('home.html')
            ############################################# Web Hook ##########################################
            headers = {
                "X-Shopify-Access-Token": session.get("access_token"),
                "Content-Type": "application/json"
            }
            payload = {
                "webhook": {
                    "topic": "products/update,order_transactions/create,orders/fulfilled",
                    "address": "https://{0}/webhooks".format(cfg.HOST),
                    "format": "json"
                }
            }
            response1 = requests.post("https://" + session.get("shop")
                                      + "/admin/webhooks.json",
                                      data=json.dumps(payload), headers=headers)

            if response1.status_code == 201:
                print("Web Hook Registered", response1.text)
                # return render_template('register_webhook.html',
                #                        webhook_response=json.loads(response.text))
            else:
                # return Response(response="{0} - {1}".format(response1.status_code,
                #                                             response1.text), status=200)
                print("Web Hook ", "{0} - {1}".format(response1.status_code, response1.text))


            return redirect(url_for('homepage'))
        else:
            print ("Failed to get access token: ", resp.status_code, resp.text)
            return render_template('error.html')


@app.route('/homepage', methods=['GET'])
def homepage():
    return render_template('home.html')


@app.route('/products/<item>', methods=['GET'])
@app.route('/products', methods=['GET'])
def products(item=None):
    """ Get a single or all stores products """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    if(item==None):
        endpoint = "/admin/products.json"
        response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                        endpoint), headers=headers)

        if response.status_code == 200:
            products = json.loads(response.text)
            print(products)

            return render_template('products.html', products=products.get("products"))
        else:
            return False
    else:
        endpoint = "/admin/products/"+item+".json"
        response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                        endpoint), headers=headers)

        if response.status_code == 200:
            product_item = json.loads(response.text)
            # product_item=product_response.product
            print(product_item.get("product"))

            return render_template('product_item.html', product=product_item.get("product"))
        else:
            return False
@app.route('/order/<item>', methods=['GET','POST'])
@app.route('/order',methods=['GET','POST'])
def order(item=None):
    """ Create an Order and Update Inventory """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    if request.method=="GET":
        if(item!=None):
            endpoint = "/admin/products/" + item + ".json"
            response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                            endpoint), headers=headers)
            if response.status_code == 200:
                product_item = json.loads(response.text)
                product=product_item.get("product")
                print('product',product)
            kwarg = locals()
            return render_template('order.html', **kwarg)
    if request.method=='POST':
        email=request.form.get('email')
        name=request.form.get('name')
        first_name=""
        last_name=""
        if(name):
            name=name.split()
            first_name=name[0]
            if len(name)>2:
                last_name=name[1]
        id=request.form.get('product_id')
        quantity=request.form.get("quantity")
        product_name=request.form.get('product_name')
        title = request.form.get('title')
        price = request.form.get('price',type=int)

        print(email,name,id,quantity)
        order_vals={
                      "order": {
                        "email": email,
                        "fulfillment_status": "fulfilled",
                        "send_receipt": "true",
                        "send_fulfillment_receipt": "true",
                        "inventory_behaviour":"decrement_obeying_policy",
                        "line_items": [
                          {
                            "variant_id": id,
                            "quantity": quantity,
                            "name":product_name,
                            "price":price,
                            "title":title
                          },
                        ],
                          "customer": {
                              "first_name": first_name,
                              "last_name": last_name,
                              "email": email
                          },
                      }
                    }
        endpoint = "/admin/orders.json"
        response = requests.post("https://" + session.get("shop")
                                 + endpoint,
                                 data=json.dumps(order_vals), headers=headers)
        if response.status_code == 201:
            # location_id = request.form.get('location_id', type=int)
            # inventory_item_id = request.form.get('inventory_item_id', type=int)
            # available_adjustment = quantity
            # endpoint='/admin/inventory_levels/adjust.json'
            # inventory_adjust={
            #     "location_id": 905684977,
            #     "inventory_item_id": 808950810,
            #     "available_adjustment": 5
            # }
            # response=request.post("https://" + session.get("shop") + endpoint,
            #                      data=json.dumps(inventory_adjust), headers=headers)
            print('response',response)
            kwarg = locals()
            return render_template('order_successful.html',**kwarg)
        else:
            return Response(response="{0} - {1}".format(response.status_code,
                                                        response.text), status=200)

@app.route('/order_history',methods=['GET','POST'])
def order_history():
    """ Get Order History """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }
    if request.method=="GET":
        endpoint = "/admin/orders.json?status=any"
        response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                        endpoint), headers=headers)
        if response.status_code == 200:
            orders_history = json.loads(response.text)
            orders_data=orders_history.get("orders")
            print('orders_data',orders_data)
            kwarg = locals()
            return render_template('order_history.html', **kwarg)
        else:
            return Response(response="{0} - {1}".format(response.status_code,
                                                        response.text), status=200)
@app.route('/customers/<customerid>',methods=['GET','POST'])
@app.route('/customers',methods=['GET','POST'])
def customers(customerid=None):
    """ Get All customers """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }
    if request.method=="GET":
        if customerid==None:
            endpoint = "/admin/customers.json?status=any"
            response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                            endpoint), headers=headers)
            if response.status_code == 200:
                customers = json.loads(response.text)
                customers=customers.get("customers")
                print('customers',customers)
                kwarg = locals()
                return render_template('customers.html', **kwarg)
            else:
                return Response(response="{0} - {1}".format(response.status_code,
                                                            response.text), status=200)
        else:
            # endpoint = "/admin/customers/"+customerid+"/orders.json"
            endpoint="/admin/orders.json?customer_id="+customerid+"&status=any"
            response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                            endpoint), headers=headers)
            if response.status_code == 200:
                customer_orders = json.loads(response.text)
                customer_orders = customer_orders.get("orders")
                print('customer_orders', customer_orders)
                kwarg = locals()
                return render_template('customer_orders.html', **kwarg)
            else:
                return Response(response="{0} - {1}".format(response.status_code,
                                                            response.text), status=200)


def get_registered_webhooks_for_shop():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    get_webhooks_response = requests.get("https://" + session.get("shop") +
                                         "/admin/webhooks.json",
                                         headers=headers)

    if get_webhooks_response.status_code == 200:
        webhooks = json.loads(get_webhooks_response.text)
        print(webhooks)
        return webhooks
    else:
        return False


@app.route('/webhooks', methods=['GET', 'POST'])
def webhooks():
    if request.method == "GET":
        return render_template('webhooks.html',
                               webhooks=get_registered_webhooks_for_shop())
    else:
        webhook_data = json.loads(request.data.decode('utf-8'))
        print("Title: {0}".format(webhook_data.get("title")))
        print(webhook_data)
        return Response(status=200)
@app.route('/search_customer', methods=['GET', 'POST'])
def search_customer():
    return render_template("search_customers.html")

@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    return render_template("login_register.html")

@app.route('/kart', methods=['GET', 'POST'])
def kart():
    return render_template("kart.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)