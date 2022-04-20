import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .models import ProductsQty
from .models import Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_details = request.data

    fields_names = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    for field in fields_names:
        if field not in order_details.keys():
            return Response(
                {'error': f'{field} is not presented'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

    order_products = order_details['products']
    first_name = order_details['firstname']
    last_name = order_details['lastname']
    address = order_details['address']
    user_phonenumber = order_details['phonenumber']

    if not all([order_products, first_name, last_name, address, user_phonenumber]):
        return Response(
            {'error': 'all fields must be filled'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    if not all(list(map(lambda field: isinstance(field, str),
                        [first_name, last_name, address, user_phonenumber]))):
        return Response(
            {'error': 'fields firstname, lastname, address, '
                      'phonenumber must be strings'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    if not isinstance(order_products, list):
        return Response(
            {'error': 'products are not list'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )


    parsed_phonenumber = phonenumbers.parse(user_phonenumber, "RU")
    if not phonenumbers.is_valid_number(parsed_phonenumber):
        return Response(
            {'error': 'invalid phone number'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )
    formatted_phonenumber = phonenumbers.format_number(
        parsed_phonenumber,
        phonenumbers.PhoneNumberFormat.E164
    )

    try:
        new_order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=formatted_phonenumber,
            address=address,
        )
        for product in order_details['products']:
            try:
                product_instance = Product.objects.get(pk=product['product'])
            except Product.DoesNotExist:
                return Response(
                    {'error': 'invalid product id'},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            ProductsQty.objects.create(
                product=product_instance,
                order=new_order,
                qty=product['quantity']
            )
    except ValueError as error:
        return Response({'error': error})
    return Response({})
