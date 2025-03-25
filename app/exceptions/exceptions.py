from fastapi import status


class DatabaseError(Exception):
    def __init__(self, message):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = message
        super().__init__(self.message)


class ItemsListException(Exception):
    def __init__(self, items_type: str, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Failed to get {items_type} list: {message}"
        super().__init__(self.message)


class ItemNotFoundException(Exception):
    def __init__(self, item_type: str, item_id: int):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = f"{item_type} with ID ({item_id}) not found."
        super().__init__(self.message)


class ItemDetailException(Exception):
    def __init__(self, item_type: str, item_id: int, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = (
            f"Error retrieving details for {item_type} ID {item_id}: {message}."
        )
        super().__init__(self.message)


class ItemAlreadyExistException(Exception):
    def __init__(self, item_type: str, unique_field_name: str, unique_field_value: str):
        self.status_code = status.HTTP_409_CONFLICT
        self.message = (
            f"{item_type} with {unique_field_name} {unique_field_value} already exist."
        )
        super().__init__(self.message)


class ItemCreateException(Exception):
    def __init__(self, item_type: str, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Failed to create {item_type}: {message}"
        super().__init__(self.message)


class ItemUpdateException(Exception):
    def __init__(self, item_type: str, item_id: int, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Failed to update {item_type} with ID ({item_id}): {message}."
        super().__init__(self.message)


class ItemDeleteException(Exception):
    def __init__(self, item_type: str, item_id: int, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Failed to delete {item_type} with ID ({item_id}): {message}"
        super().__init__(self.message)
