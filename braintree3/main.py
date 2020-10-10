import json

from flask import Flask, request

from braintree_gateway import generate_client_token, transact, customer_create, customer_find, payment_method

app = Flask(__name__)
app.secret_key = 'alskfjaslkdjfKKDKfn93'  # this is used for authentication don't change


@app.route('/braintree_client_token', methods=['GET'])
def new_checkout():
    customer_id = request.args.get('user_id')
    email = request.args.get('email')
    get_or_create_customer(email, customer_id)
    client_token = generate_client_token(customer_id)
    return json.dumps(client_token)


def create_customer(email, user_id):
    result = customer_create({
        'id': user_id,
        'email': email
    })
    if result.is_success:
        print(result.customer)
        return result.customer
    else:
        print('Customer creation failed {} {} {}'.format(email, user_id, result))
    return None


def get_or_create_customer(email, user_id):
    try:
        customer = customer_find(user_id)
    except Exception as e:
        print('Could not find or create customer {} {}'.format(email, user_id))
        customer = create_customer(email, user_id)
    return customer


# add a payment method to a user
@app.route('/add_payment_method', methods=['POST'])
def add_payment_method():
    customer = get_or_create_customer(request.form['email'], request.form['user_id'])
    result = payment_method({
        "customer_id": customer.id,
        "payment_method_nonce": request.form['payment_nonce'],
        "options": {
            "verify_card": True,
        }
    })
    print(result)
    return


# add a subscription to a payment method


# remove a subscriptoin from a user


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4567, debug=True)
