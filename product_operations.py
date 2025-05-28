
import uuid

def insert_product(driver, name, description, brand, price, stock, rating, seller_cpf=None):
    """Insert a product into Neo4j"""
 
    product_id = str(uuid.uuid4())
    
   
    product_props = {
        'id': product_id,
        'name': name,
        'description': description,
        'brand': brand,
        'price': float(price),
        'stock': int(stock),
        'rating': float(rating)
    }
    
   
    query = """
    CREATE (p:Product $props)
    RETURN p.id
    """
    
    result = driver.run_query(query, {'props': product_props})
    
    if not result:
        return None
    
   
    if seller_cpf:
        
        find_seller_query = """
        MATCH (u:User {cpf: $cpf})
        RETURN u.id
        """
        
        seller_result = driver.run_query(find_seller_query, {'cpf': seller_cpf})
        
        if seller_result and seller_result[0]:
            seller_id = seller_result[0][0]
            
           
            update_product_query = """
            MATCH (p:Product {id: $productId})
            SET p.sellerId = $sellerId
            """
            
            driver.run_query(update_product_query, {'productId': product_id, 'sellerId': seller_id})
            
           
            seller_query = """
            MATCH (u:User {id: $sellerId}), (p:Product {id: $productId})
            CREATE (u)-[:SELLS]->(p)
            """
            
            driver.run_query(seller_query, {'sellerId': seller_id, 'productId': product_id})
            print(f"Product linked to seller with CPF {seller_cpf}")
        else:
            print(f"Warning: Seller with CPF {seller_cpf} not found. Product created without seller.")
    
    print(f"Product created with ID: {product_id}")
    return product_id

def search_products_by_name(driver, name):
    """Search products by name"""
    query = """
    MATCH (p:Product)
    WHERE toLower(p.name) CONTAINS toLower($name)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query, {'name': name})
    
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

def search_products_by_brand(driver, brand):
    """Search products by brand"""
    query = """
    MATCH (p:Product)
    WHERE toLower(p.brand) CONTAINS toLower($brand)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query, {'brand': brand})
    
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

def search_products_by_price_range(driver, min_price, max_price):
    """Search products by price range"""
    query = """
    MATCH (p:Product)
    WHERE p.price >= $minPrice AND p.price <= $maxPrice
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.price
    """
    
    params = {
        'minPrice': float(min_price),
        'maxPrice': float(max_price)
    }
    
    result = driver.run_query(query, params)
    
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

def search_products_by_seller(driver, seller_id):
    """Search products by seller ID"""
    query = """
    MATCH (u:User {id: $sellerId})-[:SELLS]->(p:Product)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query, {'sellerId': seller_id})
    
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

def search_products_by_seller_cpf(driver, seller_cpf):
    """Search products by seller CPF"""
    query = """
    MATCH (u:User {cpf: $sellerCpf})-[:SELLS]->(p:Product)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.stock, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query, {'sellerCpf': seller_cpf})
    
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