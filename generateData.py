import boto3
from faker import Faker
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import uuid
from decimal import Decimal


# Initialize Faker and DynamoDB client
faker = Faker()

start_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2023-12-31", "%Y-%m-%d")

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION_NAME')
)

dynamodb = session.resource('dynamodb')
tienda_table = dynamodb.Table('dev-proyecto-tienda')
categoria_table = dynamodb.Table('dev-t_categorias')
usuario_table = dynamodb.Table('dev-proyecto-usuarios')
producto_table = dynamodb.Table('dev-proyecto_productos')
pedido_table = dynamodb.Table('dev-proyecto-pedidos')
resenia_table = dynamodb.Table('proyecto-api-resenia-dev-resena')

# Tienda
tenant_ids = ["Lunavie", "Glow", "Lumiere"]

tiendas = [
    {
        'tenant_id': tenant_id,
        'datos': {'nombre': tenant_id},
        'fecha': faker.date_time_between(start_date=start_date, end_date=end_date)
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
        'tenant_id': tenant_ids[i % len(tenant_ids)],  # Usa el módulo para repetir los elementos si es necesario
        'categoria_id': faker.uuid4(),
        'nombre': categ_name,
        'data': {'descripcion': categ_descriptions[categ_name]}
    }
    for i, categ_name in enumerate(categ_names)
]
# Producto
adjectives = ["Radiant", "Glam", "Velvet", "Matte", "Shimmer", "Hydrating", "Bold", "Luxe", "Glow", "Flawless",
              "Luminous", "Soft", "Elegant"]
brands = ["Maybelline", "L'Oréal", "MAC", "Sephora", "Estée Lauder", "Fenty Beauty", "NARS", "Revlon"]
category_to_makeup_types = {
    "Ojos": ["Mascara", "Eyeliner", "Eyeshadow", "Primer"],
    "Rostro": ["Foundation", "Blush", "Highlighter", "Concealer"],
    "Labios": ["Lipstick", "Lip Gloss"],
    "Cejas y pestanias": ["False Lashes"]
}

makeup_type_to_img = {
    "Mascara": ["Glow/14de21a81e0b49f6bc84130e09452f7f_20241205052409.jpg", "Lunavie/4e8e46d458ad490893efe4d0cd6ec65f_20241205054215.jpg", "Lumiere/f43dcfdf8d504fddab88396478d20003_20241205054257.jpg"],
    "Eyeliner": ["Lumiere/d0b0a51f3b7540618a3bdcd036231c64_20241205054635.jpg", "Glow/180223ade26e41148c3e10d9fbb69184_20241205054652.jpg", "Lunavie/67abbd519ce84f38a7dd604ff2463a0c_20241205054708.jpg"],
    "Eyeshadow": ["Lunavie/1b874ca12430435cae9cd799d7a4b1f1_20241205054901.jpg", "Lumiere/a90ca8e5a6bd420b83d423f0ab7c0ade_20241205054925.jpg", "Glow/4509c741cee34ef282b1ed6d23745ea1_20241205055112.jpg"],
    "Primer": ["Glow/20e673b70b3b43b39594f37cf1d7f6fa_20241205055220.jpg","Lumiere/041814a9bc08425cbe0deca54e686326_20241205055252.jpg", "Lunavie/a4718207691d40f5ad8092756caf5e49_20241205055304.jpg" ],
    "Foundation": ["Lunavie/4ece204afd8a44c9b3f8416db9354472_20241205055435.jpg", "Glow/8dd718abb68542bb9154cce95fb46e5e_20241205055445.jpg", "Lumiere/8d206b5564f74ec29494cf82566fb806_20241205055505.jpg"],
    "Blush": ["Lumiere/06e264558be641c096ef4ae5c67f48a4_20241205060008.jpg","Glow/0ba5c213f1304e87a74ce81552c4d70f_20241205060030.jpg", "Lunavie/2b5045c0ba604df9b398e823ec3aaaae_20241205060040.jpg" ],
    "Highlighter": ["Lunavie/4f1fdf11ce574d93ab1e14244b6d5196_20241205060210.jpg", "Glow/9d0d3f9838e645748814a85c1c6ab514_20241205060218.jpg", "Lumiere/0b9a07f9f2ee4bd9b973b7e9e38d9bce_20241205060239.jpg"],
    "Concealer": ["Lumiere/5bc73060f28e4a9a9728ff95ff2a440b_20241205060448.jpg", "Glow/c1107cb010654a17b4c80021c884340d_20241205060456.jpg", "Lunavie/d5906b76f38a4d24af429b246d409a24_20241205060522.jpg"],
    "Lipstick": ["Lunavie/1c223410b5f84bf1b0d893e74117bcb8_20241205060708.jpg", "Lumiere/3f8f5d41e97e4f6ba8a8b1744d19d5f3_20241205060732.jpg", "Glow/d7aa675506284c3eb26ff5298fdbe6ab_20241205060750.jpg"],
    "Lip Gloss": ["Glow/edbdfb0c8fae41539f5cb56a0134d803_20241205060950.jpg","Lunavie/057cad2ca6fd4c8a98129247b39d6d0e_20241205061020.jpg", "Lumiere/e831c62691844811afcddcdb0f9b6bf6_20241205061032.jpg" ],
    "False Lashes": ["Lumiere/33ef518946f4478a863c7dab5fc8309b_20241205061253.jpg", "Glow/b4ff7da0112a48c7b28510105aff4967_20241205061312.jpg", "Lunavie/39f71f17fe4f45918bcab3fa397263a2_20241205061330.jpg"]
}

productos = [
    {
        'tenant_id#categoria_nombre': f"{categoria['tenant_id']}#{categoria['nombre']}",
        'producto_id': faker.uuid4(),
        'tenant_id': categoria['tenant_id'],
        'categoria_nombre': (categoria_nombre := categoria['nombre']),
        'nombre': f"{random.choice(adjectives)} {(makeup_type := random.choice(category_to_makeup_types[categoria_nombre]))} by {random.choice(brands)}",
        'img': random.choice(makeup_type_to_img[makeup_type]),
        'stock': random.randint(0, 100),
        'precio': round(random.uniform(1.0, 500.0), 2)
    }
    for categoria in categorias for _ in range(2500)
]

# Usuario
# Generación de usuarios
# Conversión de la fecha a una cadena en formato 'YYYY-MM-DD'
usuarios = [
    {
        'user_id': str(uuid.uuid4()),  # Generar un UUID como 'user_id'
        'tenant_id': random.choice(tenant_ids),  # Asumiendo que 'tenant_ids' está definido
        'email': faker.email(),
        'password': faker.password(),
        'data': {
            'nombre': faker.name()
        },
        'fechaCreacion': faker.date_this_decade().strftime('%Y-%m-%d')  # Formatear la fecha como cadena
    }
    for _ in range(1000)  # Generar 1000 usuarios
]




# Reseña
# Reseña
comentario_to_puntaje = {
    0: [
        "Este producto es horrible, me irritó la piel.",
        "No lo compraría nunca más. No sirve para nada.",
        "Totalmente decepcionada, no hace lo que promete.",
        "Es el peor maquillaje que he probado, me dejó la piel peor.",
        "Me arruinó el look, no lo recomiendo en absoluto."
    ],
    1: [
        "Muy mala calidad. Se ve artificial y no dura nada.",
        "No es lo que esperaba, se oxida rápidamente.",
        "No cubre bien, y el acabado es muy poco natural.",
        "Me dejó la piel seca y no tiene buena fijación.",
        "No me gustó para nada, no lo volvería a usar."
    ],
    2: [
        "Es regular, no es increíble pero tampoco es tan malo.",
        "No es lo que pensaba, pero funciona para salir del paso.",
        "El acabado es decente, pero no es mi favorito.",
        "Lo usaría en ocasiones casuales, pero no lo recomendaría a nadie.",
        "Me gusta el color, pero no dura mucho."
    ],
    3: [
        "Es un buen producto, aunque no es el mejor de todos.",
        "Me gusta el acabado, aunque podría durar más.",
        "Cumple su función, pero no es algo que me encante.",
        "Es decente para el precio, pero podría mejorar en algunos aspectos.",
        "Lo recomendaría si no hay mejores opciones."
    ],
    4: [
        "Me encanta, el acabado es muy bonito y dura todo el día.",
        "Muy buen producto, se aplica con facilidad y tiene buena cobertura.",
        "Lo usaría todo el tiempo, es bastante bueno.",
        "Cubre perfectamente y no se siente pesado en la piel.",
        "Me ha gustado mucho, aunque quizás algo caro."
    ],
    5: [
        "Es perfecto, no puedo vivir sin él. Lo recomiendo totalmente.",
        "Es el mejor producto que he probado. ¡Me encantó!",
        "Superó mis expectativas. El acabado es increíble y dura todo el día.",
        "Este maquillaje es espectacular. No lo cambio por nada.",
        "Lo mejor que he comprado en mucho tiempo, ¡totalmente recomendable!"
    ]
}

resenias = [
    {
        'tenant_id#producto_id': f"{(tenant_id := random.choice(tenant_ids))}#{random.choice([p['producto_id'] for p in productos if p['tenant_id'] == tenant_id])}",
        'resenia_id': faker.uuid4(),
        'usuario_id': (usuario := random.choice([usuario for usuario in usuarios if usuario['tenant_id'] == tenant_id]))['user_id'],
        'detalle': {
            'puntaje': (puntaje := random.randint(0, 5)),
            'comentario': random.choice(comentario_to_puntaje[puntaje]),
        },
        'fecha': faker.date_time_between(
            start_date=usuario['fechaCreacion'],
            end_date=datetime(2024, 12, 31)
        ).isoformat(),
    }
    for _ in range(10000)
]


# Pedido
productos_dict = {
    producto['producto_id']: producto  # Producto ID como clave y el producto completo como valor
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
        'estado': get_estado(fecha_pedido := faker.date_time_between(start_date=usuario['fechaCreacion'],
                                                                     end_date=datetime(2024, 12, 31))),
        'datos': {
            'productosID': (productosID := random.sample(
                [producto['producto_id'] for producto in productos if producto['tenant_id'] == usuario['tenant_id']],
                k=random.randint(1, 5))),
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

def convert_floats_to_decimal(item):
    for key, value in item.items():
        if isinstance(value, float):
            item[key] = Decimal(str(value))
        elif isinstance(value, dict):
            convert_floats_to_decimal(value)
        elif isinstance(value, list):
            for i in range(len(value)):
                if isinstance(value[i], float):
                    value[i] = Decimal(str(value[i]))
                elif isinstance(value[i], dict):
                    convert_floats_to_decimal(value[i])
    return item


def batch_write(table, items):
    with table.batch_writer() as batch:
        for item in items:
            item = convert_floats_to_decimal(item)  # Convertir floats a Decimal
            batch.put_item(Item=item)

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
