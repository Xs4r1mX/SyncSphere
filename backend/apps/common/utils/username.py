from django.utils.text import slugify


def generate_username(user_model, first_name, last_name):

    base_username = slugify(f"{first_name} {last_name}")

    username = base_username
    counter = 1

    while user_model.objects.filter(username=username).exists():

        username = f"{base_username}-{counter}"

        counter += 1

    return username
