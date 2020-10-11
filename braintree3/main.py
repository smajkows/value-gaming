import json

from flask import Flask, request

from braintree_gateway import generate_client_token, transact, customer_create, customer_find, payment_method, get_plans, \
    create_subscription, customer_find, find_subscription, cancel_subscription

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


@app.route('/get_plans', methods=['GET'])
def get_braintree_plans():
    json_plans = {}
    for plan in get_plans():
        json_plans[plan.id] = {'id': plan.id, 'description': plan.description, 'price': plan.price,
                               'created_at': plan.created_at.strftime("%m/%d/%Y"), 'name': plan.name}
    return json.dumps(json_plans)

# add a subscription to a payment method
@app.route('/update_user_plan', methods=['POST'])
def update_user_plan():
    customer = customer_find(request.form['user_id'])
    plan_id = request.form['plan_id']
    sub_id = request.form['subscription_id']

    if not customer:
        print('non-existing customer trying to update plan user_id:{}'.format(request.form['user_id']))
    payment_methods = customer.payment_methods
    payment_token = None
    for payment_method in payment_methods:
        if payment_method.default:
            payment_token = payment_method.token
    result = create_subscription({
        "payment_method_token": payment_token,
        "plan_id": plan_id
        })
    outcome = {'success': False, 'plan_id': plan_id, 'subscription_id': sub_id}
    if result.is_success:
        outcome = {'success': result.is_success, 'plan_id': plan_id, 'subscription_id': result.subscription.id}
        # if we add a new plan cancel their old one
        try:
            old_sub = find_subscription(sub_id)
            if old_sub:
                # if the old sub is found cancel it
                cancel_result = cancel_subscription(sub_id)
                print('Cancel sub {} was a {}'.format(sub_id, cancel_result.is_success))
        except Exception as e:
            print("old subscription {} could not be found but new one was made {} for user {}"
                  .format(sub_id, result.subscription.id, request.form['user_id']))
            print(e)
    return json.dumps(outcome)



# remove a subscriptoin from a user


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4567, debug=True)
