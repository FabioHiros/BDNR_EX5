# order_operations.py - Order operations in Neo4j

import uuid
from datetime import datetime

def create_order(driver, buyer_cpf, products):
    """
    Create an order with multiple products
    
    Args:
        driver: Neo4j connection driver
        buyer_cpf: CPF of the buyer
        products: List of dictionaries with product_id and quantity
        
    Returns:
        str: ID of the created order, or None if creation failed
    """
    # Find buyer by CPF
    find_buyer_query = """
    MATCH (u:User {cpf: $cpf})
    RETURN u.id
    """
    
    buyer_result = driver.run_query(find_buyer_query, {'cpf': buyer_cpf})
    
    if not buyer_result or not buyer_result[0]:
        print(f"Buyer with CPF {buyer_cpf} not found")
        return None
    
    buyer_id = buyer_result[0][0]
    
    # Generate unique order ID
    order_id = str(uuid.uuid4())
    
    # Calculate total value and prepare products for the order
    total_value = 0
    order_products = []
    
    for product_entry in products:
        product_id = product_entry['product_id']
        quantity = product_entry['quantity']
        
        # Get product info
        product_query = """
        MATCH (p:Product {id: $productId})
        RETURN p.name, p.price
        """
        
        product_result = driver.run_query(product_query, {'productId': product_id})
        
        if not product_result or not product_result[0]:
            print(f"Product with ID {product_id} not found")
            continue
        
        product_name = product_result[0][0]
        product_price = product_result[0][1]
        product_total = product_price * quantity
        total_value += product_total
        
        order_products.append({
            'id': product_id,
            'name': product_name,
            'price': product_price,
            'quantity': quantity
        })
    
    if not order_products:
        print("No valid products for the order")
        return None
    
    # Create order node
    order_props = {
        'id': order_id,
        'value': total_value,
        'status': "Pending",
        'date': datetime.now().isoformat(),
        'buyerId': buyer_id
    }
    
    order_query = """
    CREATE (o:Order $props)
    RETURN o.id
    """
    
    order_result = driver.run_query(order_query, {'props': order_props})
    
    if not order_result:
        print("Failed to create order")
        return None
    
    # Create relationship between buyer and order
    buyer_order_query = """
    MATCH (u:User {id: $buyerId}), (o:Order {id: $orderId})
    CREATE (u)-[:ORDERED]->(o)
    """
    
    driver.run_query(buyer_order_query, {'buyerId': buyer_id, 'orderId': order_id})
    
    # Create relationships between order and products
    for product in order_products:
        product_order_query = """
        MATCH (o:Order {id: $orderId}), (p:Product {id: $productId})
        CREATE (o)-[:CONTAINS {quantity: $quantity}]->(p)
        """
        
        driver.run_query(product_order_query, {
            'orderId': order_id,
            'productId': product['id'],
            'quantity': product['quantity']
        })
        
        # Update product stock
        update_stock_query = """
        MATCH (p:Product {id: $productId})
        SET p.stock = p.stock - $quantity
        """
        
        driver.run_query(update_stock_query, {
            'productId': product['id'],
            'quantity': product['quantity']
        })
    
    print(f"Order created successfully with ID: {order_id}")
    print(f"Total value: R$ {total_value:.2f}")
    
    return order_id

def get_all_products(driver):
    """
    Get all available products
    
    Args:
        driver: Neo4j connection driver
        
    Returns:
        list: List of product dictionaries
    """
    query = """
    MATCH (p:Product)
    WHERE p.stock > 0
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query)
    
    if not result:
        return []
    
    products = []
    for record in result:
        products.append({
            'id': record[0],
            'name': record[1],
            'description': record[2],
            'brand': record[3],
            'price': record[4],
            'stock': record[5],
            'rating': record[6]
        })
    
    return products

def get_user_orders(driver, buyer_cpf):
    """
    Get all orders for a user
    
    Args:
        driver: Neo4j connection driver
        buyer_cpf: CPF of the buyer
        
    Returns:
        list: List of order dictionaries
    """
    query = """
    MATCH (u:User {cpf: $cpf})-[:ORDERED]->(o:Order)
    RETURN o.id, o.value, o.status, o.date
    ORDER BY o.date DESC
    """
    
    result = driver.run_query(query, {'cpf': buyer_cpf})
    
    if not result:
        return []
    
    orders = []
    for record in result:
        orders.append({
            'id': record[0],
            'value': record[1],
            'status': record[2],
            'date': record[3]
        })
    
    return orders

def get_order_products(driver, order_id):
    """
    Get products in an order
    
    Args:
        driver: Neo4j connection driver
        order_id: ID of the order
        
    Returns:
        list: List of product dictionaries with quantities
    """
    query = """
    MATCH (o:Order {id: $orderId})-[r:CONTAINS]->(p:Product)
    RETURN p.id, p.name, p.price, r.quantity
    """
    
    result = driver.run_query(query, {'orderId': order_id})
    
    if not result:
        return []
    
    products = []
    for record in result:
        products.append({
            'id': record[0],
            'name': record[1],
            'price': record[2],
            'quantity': record[3],
            'total': record[2] * record[3]
        })
    
    return products