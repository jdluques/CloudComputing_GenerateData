import boto3
from faker import Faker
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Initialize Faker and DynamoDB client
faker = Faker()

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION_NAME')
)

dynamodb = session.resource('dynamodb')

tienda_table = dynamodb.Table('Tienda')
categoria_table = dynamodb.Table('Categoria')
usuario_table = dynamodb.Table('Usuario')
producto_table = dynamodb.Table('Producto')
pedido_table = dynamodb.Table('Pedido')
resenia_table = dynamodb.Table('Resenia')

# Tienda
tenant_ids = ["Lunavie", "Glow", "Lumiere"]

tiendas = [
    {
        'tenant_id': tenant_id,
        'datos': { 'nombre': tenant_id },
        'fechaCreacion': faker.date_time_between(start_date="2021-10-01", end_date="2022-01-01")
    }
    for tenant_id in tenant_ids
]

# Categoría
categ_names = ["Ojos", "Rostro", "Labios", "Cejas y pestanias"]
categ_descriptions = {
    "Ojos": "Productos destinados al cuidado y embellecimiento de los ojos, como sombras, delineadores y máscaras de pestañas.",
    "Rostro": "Cosméticos para el rostro, incluyendo bases, correctores, rubores, y iluminadores para un acabado perfecto y radiante.",
    "Labios": "Productos específicos para labios, como barras de labios, glosses y delineadores, para realzar la belleza de esta zona.",
    "Cejas y pestanias": "Cosméticos dedicados a las cejas y pestañas, como lápices, geles y máscaras, para definir y dar volumen.",
}

categorias = [
    {
        'tenant_id': tenant_ids[i],
        'categoria_id': faker.uuid4(),
        'nombre': categ_name,
        'data': { 'descripcion': categ_descriptions[categ_name] }
    }
    for i, categ_name in enumerate(categ_names)
]

# Producto
adjectives = ["Radiant", "Glam", "Velvet", "Matte", "Shimmer", "Hydrating", "Bold", "Luxe", "Glow", "Flawless", "Luminous", "Soft", "Elegant"]
brands = ["Maybelline", "L'Oréal", "MAC", "Sephora", "Estée Lauder", "Fenty Beauty", "NARS", "Revlon"]
category_to_makeup_types = {
    "Ojos": ["Mascara", "Eyeliner", "Eyeshadow", "Primer"],
    "Rostro": ["Foundation", "Blush", "Highlighter", "Concealer"],
    "Labios": ["Lipstick"],
    "Cejas y pestanias": ["Mascara", "Eyeliner"]
}

productos = [
    {
        'tenant_id#categoria_nombre': f"{categoria['tenant_id']}#{categoria['nombre']}",
        'producto_id': faker.uuid4(),
        'tenant_id': categoria['tenant_id'],
        'categoria_nombre': categoria['nombre'],
        'nombre': f"{random.choice(adjectives)} {random.choice(category_to_makeup_types[categoria['nombre']])} by {random.choice(brands)}",
        'stock': random.randint(0, 100),
        'precio': round(random.uniform(1.0, 500.0), 2)
    }
    for categoria in categorias for _ in range(2500)
]

# Usuario
usuarios = [
    {
        'tenant_id': random.choice(tenant_ids),
        'user_id': faker.uuid4(),
        'email': faker.email(),
        'password': faker.password(),
        'data': { 'fullName': faker.name() },
        'role': "user",
        'fechaCreacion': (fecha_creacion := faker.date_time_between(start_date="2022-01-01", end_date="2024-12-31")),
        'ultimoAcceso': faker.date_time_between(start_date=fecha_creacion, end_date="2024-12-31").isoformat()
    }
    for _ in range(10000)
]

# Reseña
resenias = [
    {
        'tenant_id#producto_id': f"{(tenant_id := random.choice(tenant_ids))}#{random.choice([p['producto_id'] for p in productos if p['tenant_id'] == tenant_id])}",
        'resenia_id': faker.uuid4(),
        'usuario_id': random.choice(usuarios)['user_id'],
        'detalle': {
            'puntaje': random.randint(1, 5),
            'comentario': faker.sentence(),
        },
        'fecha': faker.date_time_between(start_date="2022-01-01", end_date="2024-12-31"),
        'datos': 1
    }
    for _ in range(10000)
]

# Pedido
productos_dict = {
    producto['producto_id']: producto  # Producto ID as key and full product as value
    for producto in productos
}


def get_estado(fecha_pedido):
    delta = datetime.now() - fecha_pedido

    if delta > timedelta(days=90):
        return random.choices(["ENTREGADO", "CANCELADO"], [0.85, 0.15])[0]

    prob_entregado = min(delta.days / 30 * 0.1, 0.7)
    prob_pendiente = max(0.8 - (delta.days / 30 * 0.1), 0.2)
    prob_cancelado = 1 - (prob_entregado + prob_pendiente)

    return random.choices(
        ["PENDIENTE", "ENTREGADO", "CANCELADO"],
        [prob_pendiente, prob_entregado, prob_cancelado]
    )[0]

estados = ["PENDIENTE", "ENTREGADO", "CANCELADO"]
pedidos = [
    {
        'tenantID': usuario['tenant_id'],
        'usuarioID': usuario['user_id'],
        'pedidoID': faker.uuid4(),
        'estado': get_estado(fecha_pedido := faker.date_time_between(start_date=usuario['fechaCreacion'], end_date="2024-12-31")),
        'datos': {
            'productosID': (productosID := random.sample(
                [producto['producto_id'] for producto in productos if producto['tenant_id'] == usuario['tenant_id']], k=random.randint(1, 5))
            ),
            'cantidad': len(productosID),
            'precio': sum(
                productos_dict[producto_id]['precio']
                for producto_id in productosID if producto_id in productos_dict
            )
        },
        'fechaPedido': fecha_pedido
    }
    for usuario in usuarios for _ in range(random.randint(1, 3))
]


# Batch write data to DynamoDB
def batch_write(table, items):
    with table.batch_writer() as batch:
        for item in items:
            try:
                batch.put_item(Item=item)
            except Exception as e:
                print(f"Error inserting item: {item}. Error: {e}")


print("Inserting data into Tienda table...")
batch_write(tienda_table, tiendas)

print("Inserting data into Categoria table...")
batch_write(categoria_table, categorias)

print("Inserting data into Usuario table...")
batch_write(usuario_table, usuarios)

print("Inserting data into Producto table...")
batch_write(producto_table, productos)

print("Inserting data into Resenia table...")
batch_write(resenia_table, resenias)

print("Inserting data into Pedidos table...")
batch_write(pedido_table, pedidos)

print("Data seeding completed!")
