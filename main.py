# main.py - Main entry point for the Neo4j e-commerce system

from neo4j_connection import connect_neo4j, close_connection
from user_operations import insert_user
from product_operations import (
    insert_product, 
    search_products_by_name, 
    search_products_by_seller,
    search_products_by_seller_cpf
)
from order_operations import create_order, get_all_products, get_user_orders, get_order_products
from favorite_operations import add_favorite, get_user_favorites, get_all_products as get_all_products_favorites, remove_favorite

# Resolve name conflict with get_all_products
get_all_products_for_favorites = get_all_products_favorites


def mainMenu():
    # Connect to Neo4j
    driver = connect_neo4j()
    if not driver:
        print("Failed to connect to Neo4j. Please check your connection settings.")
        return
    
    try:
        while True:
            print("""
                ##### Menu Principal #####
                    1- C Usuário
                    2- C Compras
                    3- CR Produto
                    4- C Favoritos
            """)
            option = input('Digite a  opção desejada (S para sair):  ')

            match option:
                case '1':
                    userMenu(driver)
                case '2':
                    orderMenu(driver)
                case '3':
                    productMenu(driver)
                case '4':
                    favoriteMenu(driver)
                case 's' | 'S':
                    return
                case _:
                    print("Opção inválida!")
    
    finally:
        close_connection(driver)

def userMenu(driver):
    while True:
        print("""
                ##### MENU DO USUÁRIO #####
                    1- Criar Usuário
        """)
        option = input("Digite a opção desejada? (V para voltar) ")

        match option:
            case '1':
                name = input("Nome: ")
                last_name = input("Sobrenome: ")
                email = input("Email: ")
                cpf = input("CPF: ")
                password = input("Senha: ")
                
                # Collect addresses
                addresses = []
                add_address = input("Adicionar endereço? (S/N): ").upper() == 'S'
                
                while add_address:
                    street = input("Rua: ")
                    number = input("Número: ")
                    neighborhood = input("Bairro: ")
                    state = input("Estado: ")
                    zip_code = input("CEP: ")
                    
                    addresses.append({
                        'street': street,
                        'number': number,
                        'neighborhood': neighborhood,
                        'state': state,
                        'zipCode': zip_code
                    })
                    
                    add_address = input("Adicionar outro endereço? (S/N): ").upper() == 'S'
                
                is_seller = input("É vendedor? (S/N): ").upper() == 'S'
                
                if is_seller:
                    company_name = input("Nome da Empresa: ")
                    cnpj = input("CNPJ: ")
                    user_id = insert_user(driver, name, last_name, email, cpf, password, addresses, is_seller, company_name, cnpj)
                else:
                    user_id = insert_user(driver, name, last_name, email, cpf, password, addresses)
                
                if user_id:
                    print(f"Usuário {name} criado com sucesso! ID: {user_id}")
                else:
                    print("Falha ao criar usuário")
              
            case 'v' | 'V':
                return 
            case _:
                print("Opção inválida!")

def productMenu(driver):
    while True:
        print("""
                ##### MENU DE PRODUTO #####
                    1- Criar Produto
                    2- Buscar Produto por Nome
                    3- Buscar Produtos por Vendedor
        """)
        option = input("Digite a opção desejada? (V para voltar) ")

        match option:
            case '1':
                name = input("Nome: ")
                description = input("Descrição: ")
                brand = input("Marca: ")
                
                try:
                    price = float(input("Preço: "))
                    stock = int(input("Estoque: "))
                    rating = float(input("Avaliação (0-5): "))
                except ValueError:
                    print("Valor inválido! Por favor, digite um número.")
                    continue
                
                seller_cpf = input("CPF do vendedor (deixe em branco para pular): ")
                
                if seller_cpf:
                    product_id = insert_product(driver, name, description, brand, price, stock, rating, seller_cpf)
                else:
                    product_id = insert_product(driver, name, description, brand, price, stock, rating)
                
                if product_id:
                    print(f"Produto criado com sucesso! ID: {product_id}")
                else:
                    print("Falha ao criar produto")
            
            case '2':
                name = input("Nome do produto (ou parte dele): ")
                products = search_products_by_name(driver, name)
                display_products(products)
            
            case '3':
                print("Buscar por: ")
                print("1. ID do vendedor")
                print("2. CPF do vendedor")
                search_option = input("Opção: ")
                
                if search_option == '1':
                    seller_id = input("ID do vendedor: ")
                    products = search_products_by_seller(driver, seller_id)
                    display_products(products)
                elif search_option == '2':
                    seller_cpf = input("CPF do vendedor: ")
                    products = search_products_by_seller_cpf(driver, seller_cpf)
                    display_products(products)
                else:
                    print("Opção inválida!")
            
            case 'v' | 'V':
                return
            
            case _:
                print("Opção inválida!")


def orderMenu(driver):
    while True:
        print("""
                ##### MENU DE COMPRA #####
                    1- Criar Nova Compra
                    2- Ver Compras do Cliente
                    3- Ver Detalhes da Compra
        """)
        option = input("Digite a opção desejada? (V para voltar) ")

        match option:
            case '1':
                # Create a new order
                buyer_cpf = input("CPF do comprador: ")
                
                # Check if buyer exists
                find_buyer_query = """
                MATCH (u:User {cpf: $cpf})
                RETURN u.id, u.name, u.lastName
                """
                
                buyer_result = driver.run_query(find_buyer_query, {'cpf': buyer_cpf})
                
                if not buyer_result or not buyer_result[0]:
                    print(f"Comprador com CPF {buyer_cpf} não encontrado!")
                    continue
                
                buyer_name = f"{buyer_result[0][1]} {buyer_result[0][2]}"
                print(f"Comprador: {buyer_name}")
                
                # Get all available products
                products = get_all_products(driver)
                
                if not products:
                    print("Não há produtos disponíveis!")
                    continue
                
                # Display products and let user select
                order_products = []
                
                while True:
                    print("\nProdutos disponíveis:")
                    print("-" * 80)
                    print(f"{'#':<3} {'Nome':<30} {'Marca':<15} {'Preço':<10} {'Estoque':<8}")
                    print("-" * 80)
                    
                    for idx, product in enumerate(products, 1):
                        name = product['name'][:28] + ".." if len(product['name']) > 30 else product['name']
                        brand = product['brand'][:13] + ".." if len(product['brand']) > 15 else product['brand']
                        print(f"{idx:<3} {name:<30} {brand:<15} R$ {product['price']:<7.2f} {product['stock']:<8}")
                    
                    print("-" * 80)
                    
                    # Select product
                    try:
                        product_idx = int(input("\nSelecione o número do produto (0 para finalizar): "))
                        
                        if product_idx == 0:
                            # Finished selecting products
                            break
                        
                        if product_idx < 1 or product_idx > len(products):
                            print("Número de produto inválido!")
                            continue
                        
                        selected_product = products[product_idx - 1]
                        
                        # Get quantity
                        max_quantity = selected_product['stock']
                        quantity = input(f"Quantidade (máx {max_quantity}): ")
                        
                        if not quantity:
                            quantity = 1
                        else:
                            try:
                                quantity = int(quantity)
                                if quantity < 1:
                                    print("Quantidade deve ser pelo menos 1")
                                    continue
                                if quantity > max_quantity:
                                    print(f"Quantidade máxima disponível: {max_quantity}")
                                    continue
                            except ValueError:
                                print("Quantidade inválida!")
                                continue
                        
                        # Add to order
                        order_products.append({
                            'product_id': selected_product['id'],
                            'quantity': quantity
                        })
                        
                        print(f"{quantity}x {selected_product['name']} adicionado ao pedido")
                        
                        # Remove or update the product in the list
                        if quantity == max_quantity:
                            products.pop(product_idx - 1)
                        else:
                            products[product_idx - 1]['stock'] -= quantity
                            
                    except ValueError:
                        print("Entrada inválida!")
                
                # Create the order if products were selected
                if order_products:
                    order_id = create_order(driver, buyer_cpf, order_products)
                    
                    if order_id:
                        print(f"Pedido criado com sucesso! ID: {order_id}")
                    else:
                        print("Falha ao criar pedido")
                else:
                    print("Nenhum produto selecionado. Pedido cancelado.")
            
            case '2':
                # View customer orders
                buyer_cpf = input("CPF do cliente: ")
                
                orders = get_user_orders(driver, buyer_cpf)
                
                if not orders:
                    print(f"Nenhum pedido encontrado para o cliente com CPF {buyer_cpf}")
                    continue
                
                print("\nPedidos do cliente:")
                print("-" * 80)
                print(f"{'#':<3} {'ID':<36} {'Valor':<12} {'Status':<15} {'Data':<20}")
                print("-" * 80)
                
                for idx, order in enumerate(orders, 1):
                    print(f"{idx:<3} {order['id']:<36} R$ {order['value']:<9.2f} {order['status']:<15} {order['date'][:19]}")
                
                print("-" * 80)
            
            case '3':
                # View order details
                order_id = input("ID do pedido: ")
                
                products = get_order_products(driver, order_id)
                
                if not products:
                    print(f"Nenhum produto encontrado para o pedido com ID {order_id}")
                    continue
                
                total_value = sum(product['total'] for product in products)
                
                print(f"\nDetalhes do pedido (ID: {order_id}):")
                print("-" * 80)
                print(f"{'#':<3} {'Produto':<30} {'Preço':<12} {'Qtd':<6} {'Total':<12}")
                print("-" * 80)
                
                for idx, product in enumerate(products, 1):
                    name = product['name'][:28] + ".." if len(product['name']) > 30 else product['name']
                    print(f"{idx:<3} {name:<30} R$ {product['price']:<9.2f} {product['quantity']:<6} R$ {product['total']:<9.2f}")
                
                print("-" * 80)
                print(f"{'Total do pedido:':<50} R$ {total_value:<9.2f}")
                print("-" * 80)
            
            case 'v' | 'V':
                return
            
            case _:
                print("Opção inválida!")

def favoriteMenu(driver):
    """Menu for favorite operations"""
    while True:
        print("""
                ##### MENU DE FAVORITOS #####
                    1- Adicionar aos Favoritos
                    2- Ver Meus Favoritos
                    3- Remover dos Favoritos
        """)
        option = input("Digite a opção desejada? (V para voltar) ")

        match option:
            case '1':
                # 1. Show all products
                products = get_all_products(driver)
                
                if not products:
                    print("Não há produtos disponíveis")
                    continue
                
                print("\nProdutos disponíveis:")
                print("-" * 80)
                print(f"{'#':<3} {'Nome':<30} {'Marca':<15} {'Preço':<10} {'Avaliação':<10}")
                print("-" * 80)
                
                for idx, product in enumerate(products, 1):
                    name = product['name'][:28] + ".." if len(product['name']) > 30 else product['name']
                    brand = product['brand'][:13] + ".." if len(product['brand']) > 15 else product['brand']
                    print(f"{idx:<3} {name:<30} {brand:<15} R$ {product['price']:<7.2f} {product['rating']:<10.1f}")
                
                print("-" * 80)
                
                # 2. Select product
                try:
                    product_idx = int(input("\nSelecione o número do produto: "))
                    
                    if product_idx < 1 or product_idx > len(products):
                        print("Número de produto inválido!")
                        continue
                    
                    selected_product = products[product_idx - 1]
                    
                    # 3. Ask for user CPF
                    user_cpf = input("Digite o CPF do usuário: ")
                    
                    # 4. Add to favorites
                    success = add_favorite(driver, user_cpf, selected_product['id'])
                    
                    if success:
                        print(f"Produto '{selected_product['name']}' adicionado aos favoritos")
                    
                except ValueError:
                    print("Entrada inválida!")
            
            case '2':
                # View user's favorites
                user_cpf = input("Digite seu CPF: ")
                
                favorites = get_user_favorites(driver, user_cpf)
                
                if not favorites:
                    print(f"Nenhum produto favorito encontrado para o CPF {user_cpf}")
                    continue
                
                print(f"\nSeus produtos favoritos ({len(favorites)}):")
                print("-" * 80)
                print(f"{'#':<3} {'Nome':<30} {'Marca':<15} {'Preço':<10} {'Avaliação':<10}")
                print("-" * 80)
                
                for idx, product in enumerate(favorites, 1):
                    name = product['name'][:28] + ".." if len(product['name']) > 30 else product['name']
                    brand = product['brand'][:13] + ".." if len(product['brand']) > 15 else product['brand']
                    print(f"{idx:<3} {name:<30} {brand:<15} R$ {product['price']:<7.2f} {product['rating']:<10.1f}")
                
                print("-" * 80)
            
            case '3':
                # Remove from favorites
                user_cpf = input("Digite seu CPF: ")
                
                favorites = get_user_favorites(driver, user_cpf)
                
                if not favorites:
                    print(f"Nenhum produto favorito encontrado para o CPF {user_cpf}")
                    continue
                
                print(f"\nSeus produtos favoritos ({len(favorites)}):")
                print("-" * 80)
                print(f"{'#':<3} {'Nome':<30} {'Marca':<15} {'Preço':<10}")
                print("-" * 80)
                
                for idx, product in enumerate(favorites, 1):
                    name = product['name'][:28] + ".." if len(product['name']) > 30 else product['name']
                    brand = product['brand'][:13] + ".." if len(product['brand']) > 15 else product['brand']
                    print(f"{idx:<3} {name:<30} {brand:<15} R$ {product['price']:<7.2f}")
                
                print("-" * 80)
                
                # Select product to remove
                try:
                    product_idx = int(input("\nSelecione o número do produto a remover: "))
                    
                    if product_idx < 1 or product_idx > len(favorites):
                        print("Número de produto inválido!")
                        continue
                    
                    selected_product = favorites[product_idx - 1]
                    
                    # Remove from favorites
                    success = remove_favorite(driver, user_cpf, selected_product['id'])
                    
                    if success:
                        print(f"Produto removido dos favoritos")
                    
                except ValueError:
                    print("Entrada inválida!")
            
            case 'v' | 'V':
                return
            
            case _:
                print("Opção inválida!")


def display_products(products):
    """Display a list of products in a formatted way"""
    if products:
        print(f"\nProdutos encontrados ({len(products)}):")
        print("-" * 80)
        for product in products:
            print(f"ID: {product['id']}")
            print(f"Nome: {product['name']}")
            print(f"Descrição: {product['description']}")
            print(f"Marca: {product['brand']}")
            print(f"Preço: R$ {product['price']:.2f}")
            print(f"Estoque: {product['stock']}")
            print(f"Avaliação: {product['rating']:.1f}")
            print("-" * 30)
    else:
        print("Nenhum produto encontrado")

if __name__ == "__main__":
    mainMenu()