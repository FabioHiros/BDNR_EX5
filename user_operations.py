
import uuid

def insert_user(driver, name, last_name, email, cpf, password, addresses=None, is_seller=False, 
                company_name=None, cnpj=None):
    """
    Insert a user into Neo4j
    
    Args:
        driver: Neo4j connection driver
        name: User's first name
        last_name: User's last name
        email: User's email
        cpf: User's CPF
        password: User's password
        addresses: List of address dictionaries with street, number, neighborhood, state, zipCode
        is_seller: Whether the user is a seller
        company_name: Company name (for sellers)
        cnpj: CNPJ (for sellers)
        
    Returns:
        str: ID of the created user, or None if creation failed
    """
   
    user_id = str(uuid.uuid4())
    
 
    user_props = {
        'id': user_id,
        'name': name,
        'lastName': last_name,
        'email': email,
        'cpf': cpf,
        'password': password,
        'isSeller': is_seller
    }
    
  
    if is_seller and company_name and cnpj:
        user_props['companyName'] = company_name
        user_props['cnpj'] = cnpj
    
   
    query = """
    CREATE (u:User $props)
    RETURN u.id
    """
    
    result = driver.run_query(query, {'props': user_props})
    
    if not result:
        return None
    
   
    if addresses:
        for address in addresses:
            add_user_address(driver, user_id, 
                            address['street'], 
                            address['number'], 
                            address['neighborhood'], 
                            address['state'], 
                            address['zipCode'])
    
    print(f"User created with ID: {user_id}")
    return user_id

def add_user_address(driver, user_id, street, number, neighborhood, state, zip_code):
    """Add an address to a user"""
   
    address_props = {
        'street': street,
        'number': number,
        'neighborhood': neighborhood,
        'state': state,
        'zipCode': zip_code
    }
    
   
    query = """
    MATCH (u:User {id: $userId})
    CREATE (a:Address $addressProps)
    CREATE (u)-[:HAS_ADDRESS]->(a)
    RETURN a
    """
    
    params = {
        'userId': user_id,
        'addressProps': address_props
    }
    
    result = driver.run_query(query, params)
    
    if not result:
        return False
    
    print(f"Address added to user {user_id}")
    return True