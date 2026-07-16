def authEntity(item)-> dict:
    return {
        "_id": str(item['_id']),
        "name": item['name'],
        "email": item['email'],
        "password": item['password']
    }
