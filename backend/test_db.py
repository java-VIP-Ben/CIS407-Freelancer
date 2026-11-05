from database import (
    create_freelancer,
    get_freelancers,
    update_freelancer,
    delete_freelancer
)

# CREATE
freelancer_id = create_freelancer(
    "John Smith",
    "john@example.com",
    "555-1234"
)
print("Created:", freelancer_id)

# READ
print("All freelancers:")
print(get_freelancers())

# UPDATE
update_freelancer(
    freelancer_id,
    "John Doe",
    "johndoe@example.com",
    "555-5678"
)
print("After update:")
print(get_freelancers())

# DELETE
delete_freelancer(freelancer_id)
print("After deletion:")
print(get_freelancers())
