def process_items(input_list, queryset, extra_data):
    """
    Perform bulk create and bulk update operations on a queryset based on the input list.

    Args:
        input_list (list): A list of dictionaries containing item data, where each dictionary may or may not have an 'id'.
        queryset (QuerySet): A queryset representing the current state of items in the database.
        extra_data (dict): Additional data to be added to each item.

    Returns:
        tuple: A tuple containing three sets: (items_to_update, items_to_create, ids_to_delete).
    """
    # Set to store items that need to be updated or created
    items_to_update = []
    items_to_create = []

    # Get the model class from the queryset
    model_class = queryset.model

    ids_in_input = {item.get("id") for item in input_list if item.get("id")}
    # Get all ids from the queryset (assuming 'id' is the primary key)
    existing_ids = set(
        queryset.values_list("id", flat=True)
    )  # Optimize by extracting ids

    for item in input_list:
        item_id = item.get("id")  # Check if 'id' is in the dictionary
        if item_id and item_id in existing_ids:  # If 'id' exists and is in the database
            items_to_update.append(model_class(**item, **extra_data))
        else:  # If 'id' is not present or doesn't exist in the database
            items_to_create.append(model_class(**item, **extra_data))

    # IDs to be deleted: Those that are in the DB but not in the input list
    ids_to_delete = (
        existing_ids - ids_in_input
    )  # Set difference (ids in db but not in input)

    return {
        "items_to_create": items_to_create,
        "items_to_update": items_to_update,
        "ids_to_delete": ids_to_delete,
    }
