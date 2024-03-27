from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
# Flask: The main Flask class used to create the web application.
# request: Provides access to the incoming HTTP request data.
# jsonify: Converts Python dictionaries to a JSON response.
# SQLAlchemy: An SQL toolkit for Python. Flask-SQLAlchemy is a Flask extension that simplifies the use of SQLAlchemy in Flask applications.
# Marshmallow: A library for object serialization and deserialization.

# Instance iniatialize
app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)

# db.Model represents the structure of the database table.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Product Schema (Marshmallow)
# This schema defines how to serialize and deserialize Product instances.
class ProductSchema(ma.Schema):
    class Meta:
        model = Product
        fields = ['id','name','description','price' ,'qty']

product_schema = ProductSchema() # For single product 
products_schema = ProductSchema(many=True) # For multiple products

@app.route('/product', methods=['POST'])
def add_product():
    # data = request.get_json()
    data = product_schema.load(request.get_json()) # It is use to deserialize (load) the JSON data into a Python dictionary.
    print(data)
    # new_product = Product(name='shahid', description='sample', price=20, qty=50) # we can also do like this but this is not good way because we don't know how many data we have.
    new_product = Product(**data) #mouth:teeth
    # (**data) is the dictionary unpacking syntax. 
    # It takes the key-value pairs from the data dictionary and passes them as keyword arguments to the constructor of the Product class.
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)
    # serialize the new_product instance into a JSON response and then returned to the client(browser).

# Get all products (Read)
@app.route('/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products) # It is use to serialize (dump) the list of products into JSON.
    return jsonify(result)
    
# Get single product (Read one)
@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    result = product_schema.dump(product)
    return jsonify(result)
    # return product_schema.jsonify(product)

# Update a product (Update)
@app.route('/product/<int:id>', methods=['PUT', 'PATCH'])
def update_product(id):
    # product = Product.query.filter_by(id=id).first() # first() is used to retrieve the first result from the filtered query.
    product = Product.query.get(id) # we can also use this.

    # Deserializes (load) data and it converts the JSON data obtained(got) from request.get_json() into a Python dictionary.
    data = product_schema.load(request.get_json()) 
     
    if product:
        if  request.method == 'PUT':
            product.name = data["name"]
            product.description = data["description"]
            product.price = data["price"]
            product.qty = data["qty"] 
            
        if request.method == 'PATCH':
            if 'name' in data:
                product.name = data["name"]

            if 'description' in data:
                product.description = data["description"]

            if 'price' in data:
                product.price = data["price"]

            if 'qty' in data:
                product.qty = data["qty"]

        db.session.commit()
        return product_schema.jsonify(product)
    return jsonify({"User": "not fond"})
    
# Delete a product (Delete)
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)

# Run server
if __name__ == "__main__":
    app.run(debug=True,port=5000)
