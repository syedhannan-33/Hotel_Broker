from django import template

register = template.Library()


def  modify_url(value):
    if value == '/':
        value += "?d=10"
    return value

register.filter('modify_url',modify_url)


@register.filter
def unique_room_types_with_prices(rooms):
    """Filter unique room types from a queryset of rooms with their respective prices."""
    unique_rooms = {}
    for room in rooms:
        if room.room_type not in unique_rooms:
            unique_rooms[room.room_type] = room.price_per_night
    return list(unique_rooms.items())