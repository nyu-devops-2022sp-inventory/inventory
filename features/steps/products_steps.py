"""
Product Steps
Steps file for Pet.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following products')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the pets and delete them one by one
    context.resp = requests.get(context.base_url + '/inventory')
    expect(context.resp.status_code).to_equal(200)
    id_counter = set()
    for product in context.resp.json():
        context.resp = requests.delete(context.base_url + '/inventory/' + str(product["product_id"]))
        if product["product_id"] not in id_counter:
            id_counter.add(product["product_id"])
            expect(context.resp.status_code).to_equal(204)
        else:
            expect(context.resp.status_code).to_equal(404)
    
    # load the database with new pets
    create_url = context.base_url + '/inventory'
    for row in context.table:
        data = {
            "product_id": row['product_id'],
            "product_name": row['product_name'],
            "quantity": row['quantity'],
            "condition": row['condition'],
            "restock_level": row['restock_level'],
            "reorder_amount": row['reorder_amount']
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)