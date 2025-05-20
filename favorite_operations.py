# favorite_operations.py - Simple favorite operations

def add_favorite(driver, user_cpf, product_id):
    """Add a favorite relationship between user and product"""
    # Find user by CPF
    user_query = """
    MATCH (u:User {cpf: $cpf})
    RETURN u.id, u.name
    """
    
    user_result = driver.run_query(user_query, {'cpf': user_cpf})
    
    if not user_result or not user_result[0]:
        print(f"User with CPF {user_cpf} not found")
        return False
    
    user_id = user_result[0][0]
    
    # Create favorite relationship
    favorite_query = """
    MATCH (u:User {id: $userId}), (p:Product {id: $productId})
    MERGE (u)-[:FAVORITE]->(p)
    RETURN p.name
    """
    
    result = driver.run_query(favorite_query, {
        'userId': user_id,
        'productId': product_id
    })
    
    if not result or not result[0]:
        print("Failed to add favorite - product may not exist")
        return False
    
    print(f"Product '{result[0][0]}' added to favorites")
    return True

def get_user_favorites(driver, user_cpf):
    """Get all favorites for a user"""
    query = """
    MATCH (u:User {cpf: $cpf})-[:FAVORITE]->(p:Product)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.rating
    ORDER BY p.name
    """
    
    result = driver.run_query(query, {'cpf': user_cpf})
    
    if not result:
        return []
    
    favorites = []
    for record in result:
        favorites.append({
            'id': record[0],
            'name': record[1],
            'description': record[2],
            'brand': record[3],
            'price': record[4],
            'rating': record[5]
        })
    
    return favorites

def get_all_products(driver):
    """Get all products"""
    query = """
    MATCH (p:Product)
    RETURN p.id, p.name, p.description, p.brand, p.price, p.rating
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
            'rating': record[5]
        })
    
    return products

def remove_favorite(driver, user_cpf, product_id):
    """Remove a favorite relationship"""
    query = """
    MATCH (u:User {cpf: $cpf})-[r:FAVORITE]->(p:Product {id: $productId})
    DELETE r
    RETURN p.name
    """
    
    result = driver.run_query(query, {
        'cpf': user_cpf,
        'productId': product_id
    })
    
    if not result or not result[0]:
        print("Favorite relationship not found")
        return False
    
    print(f"Removed '{result[0][0]}' from favorites")
    return True