
from database import (
    create_freelancer,
    get_freelancers,
    update_freelancer,
    delete_freelancer,
    create_projects,
    get_projects,
    update_projects,
    delete_projects,
    create_client,
    get_client,
    update_client,
    delete_client
)


# ---------------------------------------
# 1. Freelancer CRUD Testing
# ---------------------------------------

print("\n===== FREELANCER CRUD TEST =====")

# CREATE
freelancer_id = create_freelancer(
    "John Smith",
    "john@example.com",
    "555-1234"
)
print("Created freelancer:", freelancer_id)

# READ
print("All freelancers:")
print(get_freelancers())

# UPDATE
updated = update_freelancer(
    freelancer_id,
    "John Doe",
    "johndoe@example.com",
    "555-5678"
)
print("Rows updated:", updated)

# READ AGAIN
print("After update:")
print(get_freelancers())


# ---------------------------------------
# 2. Client CRUD Testing
# ---------------------------------------

print("\n===== CLIENT CRUD TEST =====")

# CREATE
client_id = create_client(
    "Jane Smith",
    "123 Main Street",
    "jane@example.com",
    "555-9876"
)
print("Created client:", client_id)

# READ
print("All clients:")
print(get_client())

# UPDATE
updated = update_client(
    client_id,
    "Jane Doe",
    "456 Oak Street",
    "janedoe@example.com",
    "555-4321"
)
print("Rows updated:", updated)

# READ AGAIN
print("After update:")
print(get_client())


# ---------------------------------------
# 3. Project CRUD Testing
# ---------------------------------------

print("\n===== PROJECT CRUD TEST =====")

# CREATE
project_id = create_projects(
    freelancer_id,
    client_id,
    None,  # PaymentID
    None,  # SkillsID
    None,  # MilestonesID
    None   # ProposalID
)
print("Created project:", project_id)

# READ
print("All projects:")
print(get_projects())

# UPDATE
updated = update_projects(
    project_id,
    freelancer_id,
    client_id,
    None,  # PaymentID
    None,  # SkillsID
    None,  # MilestonesID
    None   # ProposalID
)
print("Rows updated:", updated)

# READ AGAIN
print("After update:")
print(get_projects())


# ---------------------------------------
# 4. Delete Testing
# ---------------------------------------

print("\n===== DELETE CRUD TEST =====")

# Delete project first because it references
# the freelancer and client.

deleted = delete_projects(project_id)
print("Projects deleted:", deleted)

deleted = delete_freelancer(freelancer_id)
print("Freelancers deleted:", deleted)

deleted = delete_client(client_id)
print("Clients deleted:", deleted)


# ---------------------------------------
# 5. Final Database Check
# ---------------------------------------

print("\n===== FINAL DATABASE CHECK =====")

print("Freelancers:")
print(get_freelancers())

print("\nClients:")
print(get_client())

print("\nProjects:")
print(get_projects())

print("\n===== CRUD TESTING COMPLETE =====")

