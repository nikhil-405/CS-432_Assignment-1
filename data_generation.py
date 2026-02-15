import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
from faker import Faker
import random
from datetime import timedelta, datetime

fake = Faker()

# Database Setup
DB_USER = 'root'
DB_PASSWORD = 'password' # We entered our details here for connecting to the localhosr
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'SafeDocs'

# Connecting to the MySQL server (without a specific DB) to ensure SafeDocs exists
base_conn = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'
base_engine = create_engine(base_conn)

with base_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    conn.commit()
    print(f"✔️ Database '{DB_NAME}' verified/created.")

# Creating the engine specifically for SafeDocs
engine = create_engine(f"{base_conn}/{DB_NAME}", echo=False)

# Configuration

NUM_ROWS = 20
# 1. Role Table
roles_data = [
    {"RoleID": 1, "RoleName": "Admin", "Description": "Full system access"},
    {"RoleID": 2, "RoleName": "Editor", "Description": "Can modify documents"},
    {"RoleID": 3, "RoleName": "Viewer", "Description": "Read-only access"},
    {"RoleID": 4, "RoleName": "Commenter", "Description": "View files and suggest edits"}
]
df_roles = pd.DataFrame(roles_data)

# 2. Organization Table
orgs = []
for i in range(1, NUM_ROWS + 1):
    orgs.append({
        "OrganizationID": i,
        "OrgName": fake.company(),
        "OrgType": random.choice(["Legal", "Finance", "Academic", "Tech"]),
        "Address": fake.address().replace("\n", ", "),
        "CreatedAt": fake.date_time_between(start_date="-20y", end_date="-1y")
    })
df_orgs = pd.DataFrame(orgs)

orgs = df_orgs["OrgName"].to_list()


email_suffixes = {}
for _, org in df_orgs.iterrows():
    # Creating a mapping of OrgID -> suffix (e.g., 1: "tec.com")
    suffix = f"{org['OrgName'][:3].lower()}.com"
    email_suffixes[org['OrganizationID']] = suffix
NUM_USERS = 1000

# 2. User Table Generation 
users = []
for i in range(1, NUM_USERS + 1):
    # Select organization first to determine email suffix
    org_id = random.choice(df_orgs["OrganizationID"])
    suffix = email_suffixes[org_id]

    # Generate Name components for email formatting
    first_name = fake.first_name().lower()
    last_name = fake.last_name().lower()

    users.append({
        "UserID": i,
        "Name": f"{first_name.capitalize()} {last_name.capitalize()}",
        # Email format used for relaistic data: first.second@sub
        "Email": f"{first_name}.{last_name}@{suffix}",
        # Real tim Legible phone format: XXX-XXX-XXXX
        "ContactNumber": fake.numerify(text='###-###-####'),
        "Age": random.randint(22, 65),
        "RoleID": random.choice(df_roles["RoleID"]),
        "OrganizationID": org_id,
        "AccountStatus": random.choice(["Active", "Suspended", "Pending"])
    })

df_users = pd.DataFrame(users)

def int_to_roman(n):
    romans = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
              6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'}
    return romans.get(n, str(n))

# Professional descriptions for the 10 levels
descriptions = [
    "Publicly accessible documents with no viewing restrictions.",
    "General information available to all registered organization members.",
    "Standard internal resources and organizational policy manuals.",
    "Internal operational files accessible to all staff members.",
    "Departmental data requiring basic internal authorization.",
    "Sensitive project documentation with restricted editing rights.",
    "Internal communications and strategic planning records.",
    "Highly restricted financial and legal documentation.",
    "Strictly confidential executive data requiring explicit clearance.",
    "Top-secret administrative oversight data; restricted to Admins only."
]

policies = []
for i in range(1, 11):
    # Logic: Lower security (Role 3/Viewer) for levels I-III,
    # Medium security (Role 2/Editor) for IV-VII,
    # High security (Role 1/Admin) for VIII-X.
    if i <= 3:
        max_role = 3  # Viewer
    elif i <= 7:
        max_role = 2  # Editor
    else:
        max_role = 1  # Admin

    policies.append({
        "PolicyID": i,
        "LevelName": f"Confidentiality Level {int_to_roman(i)}",
        "MaxAllowedRoleID": max_role,
        "Description": descriptions[i-1]
    })

df_policies = pd.DataFrame(policies)

NUM_DOCS = 2000

docs = []
for i in range(1, NUM_DOCS + 1):
    # 1. Randomly select a user and immediately extract the first row as a Series
    # .iloc is necessary to access the individual row's data
    owner_series = df_users.sample(n=1).iloc[0]

    owner_id = owner_series["UserID"]
    org_id = owner_series["OrganizationID"]

    # 2. Set creation date
    created_at = fake.date_time_between(start_date="-1y", end_date="-1m")
    x = random.choice(["_Report", "", " Doc", "-Presentation", " data", "_lecture", "_brief", "Deck"])

    # Logical Constraint Used : Modified date must be after creation
    # Adding random days AND random hours/minutes/seconds so times differ
    last_modified = created_at + timedelta(
        days=random.randint(1, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

    docs.append({
        "DocID": i,
        "DocName": f"{fake.word().capitalize()}{x}.pdf",
        "DocSize": random.randint(500, 15000), # in KB
        "NumberOfPages": random.randint(1, 100),
        "FilePath": f"/secure/storage/doc_{i}.pdf",
        "ConfidentialityLevel": random.choice(df_policies["LevelName"]),
        "IsPasswordProtected": random.choice([True, False]),
        "OwnerUserID": owner_id,
        "OrganizationID": org_id, # Logically linked per source requirements
        "CreatedAt": created_at,
        "LastModifiedAt": last_modified
    })

df_docs = pd.DataFrame(docs)

permissions = []
existing_permissions = set()
permission_counter = 1

# Precompute for performance

# Map: LevelName -> MaxAllowedRoleID
policy_dict = df_policies.set_index("LevelName")["MaxAllowedRoleID"].to_dict()

# Group users by Organization for fast lookup
users_by_org = {
    org_id: group for org_id, group in df_users.groupby("OrganizationID")
}

# ---- Generate Permissions ----

for _, doc in df_docs.iterrows():

    doc_id = doc["DocID"]
    org_id = doc["OrganizationID"]
    owner_id = doc["OwnerUserID"]
    doc_created = doc["CreatedAt"]

    max_role_allowed = policy_dict[doc["ConfidentialityLevel"]]

    # ---------------------------
    # 1️⃣ Guarantee Owner Permission
    # ---------------------------
    owner_key = (doc_id, owner_id, "Edit")

    if owner_key not in existing_permissions:
        existing_permissions.add(owner_key)

        permissions.append({
            "PermissionID": permission_counter,
            "DocID": doc_id,
            "UserID": owner_id,
            "AccessType": "Edit",
            "GrantedAt": doc_created
        })

        permission_counter += 1

    # ---------------------------
    # 2️⃣ Additional Random Permissions
    # ---------------------------

    if org_id not in users_by_org:
        continue

    org_users = users_by_org[org_id]

    # Filter by confidentiality role constraint
    valid_users = org_users[org_users["RoleID"] <= max_role_allowed]

    if valid_users.empty:
        continue

    num_extra_permissions = random.randint(1, 3)

    for _ in range(num_extra_permissions):

        user = valid_users.sample(n=1).iloc[0]

        role_id = user["RoleID"]

        # AccessType by role
        if role_id == 1:
            access_type = random.choice(["View", "Edit", "Delete"])
        elif role_id == 2:
            access_type = random.choice(["View", "Edit"])
        else:
            access_type = "View"

        key = (doc_id, user["UserID"], access_type)

        if key in existing_permissions:
            continue

        existing_permissions.add(key)

        granted_at = fake.date_time_between(
            start_date=doc_created,
            end_date="now"
        )

        permissions.append({
            "PermissionID": permission_counter,
            "DocID": doc_id,
            "UserID": user["UserID"],
            "AccessType": access_type,
            "GrantedAt": granted_at
        })

        permission_counter += 1


df_permissions = pd.DataFrame(permissions)


# Logs table creation
logs = []
log_counter = 1

# Precompute useful maps for speed

# DocID -> CreatedAt
doc_created_map = df_docs.set_index("DocID")["CreatedAt"].to_dict()

last_modified_map = df_docs.set_index("DocID")["LastModifiedAt"].to_dict()


# DocID -> OrganizationID
doc_org_map = df_docs.set_index("DocID")["OrganizationID"].to_dict()

# UserID -> OrganizationID
user_org_map = df_users.set_index("UserID")["OrganizationID"].to_dict()

# Permissions grouped by DocID
permissions_by_doc = {
    doc_id: group for doc_id, group in df_permissions.groupby("DocID")
}

for doc_id, perm_group in permissions_by_doc.items():

    doc_created = doc_created_map[doc_id]
    last_modified = last_modified_map[doc_id]
    doc_org = doc_org_map[doc_id]

    # Generate 1–5 logs per document
    for _ in range(random.randint(1, 5)):

        # Select valid permission row
        perm = perm_group.sample(n=1).iloc[0]

        user_id = perm["UserID"]
        access_type = perm["AccessType"]

        # Ensure same org (extra safety)
        if user_org_map[user_id] != doc_org:
            continue

        # Determine valid action types based on permission
        if access_type == "View":
            action = random.choice(["VIEW", "DOWNLOAD"])
        elif access_type == "Edit":
            action = random.choice(["VIEW", "DOWNLOAD", "UPLOAD"])
        elif access_type == "Delete":
            action = random.choice(["VIEW", "DOWNLOAD", "UPLOAD", "DELETE"])
        else:
            continue

        action_time = fake.date_time_between(
            start_date=doc_created,
            end_date="now"
        )

        logs.append({
            "LogID": log_counter,
            "UserID": user_id,
            "DocID": doc_id,
            "ActionType": action,
            "ActionTimestamp": action_time,
            "IPAddress": fake.ipv4()
        })

        log_counter += 1

df_logs = pd.DataFrame(logs)


# 8. DocumentVersion Table
versions = []

# Precompute maps for consistency
doc_created_map_v = df_docs.set_index("DocID")["CreatedAt"].to_dict()
doc_last_modified_map_v = df_docs.set_index("DocID")["LastModifiedAt"].to_dict()

# Build a map of DocID -> list of UserIDs with Edit permission
edit_perm_by_doc = (
    df_permissions[df_permissions["AccessType"] == "Edit"]
    .groupby("DocID")["UserID"]
    .apply(list)
    .to_dict()
)

# Owner fallback map
doc_owner_map = df_docs.set_index("DocID")["OwnerUserID"].to_dict()

def get_modifier(doc_id):
    """Pick a user with Edit permission on this doc."""
    if doc_id in edit_perm_by_doc and edit_perm_by_doc[doc_id]:
        return random.choice(edit_perm_by_doc[doc_id])
    return doc_owner_map[doc_id]

for doc_id in df_docs["DocID"]:
    doc_created = doc_created_map_v[doc_id]
    last_modified = doc_last_modified_map_v[doc_id]

    # ── Mandatory version at CreatedAt ──
    versions.append({
        "DocID": doc_id,
        "VersionNumber": 1,
        "ModifiedByUserID": get_modifier(doc_id),
        "ModifiedAt": doc_created,
        "ChangeSummary": "Initial version"
    })

    # ── Mandatory version at LastModifiedAt ──
    versions.append({
        "DocID": doc_id,
        "VersionNumber": 2,
        "ModifiedByUserID": get_modifier(doc_id),
        "ModifiedAt": last_modified,
        "ChangeSummary": fake.sentence()[:-1]
    })

    # ── Extra versions for ~40% of docs (1-3 more, between created & last modified) ──
    if random.random() < 0.4:
        num_extra = random.randint(1, 3)
        for _ in range(num_extra):
            modified_at = fake.date_time_between(
                start_date=doc_created,
                end_date=last_modified
            )
            versions.append({
                "DocID": doc_id,
                "VersionNumber": 0,
                "ModifiedByUserID": get_modifier(doc_id),
                "ModifiedAt": modified_at,
                "ChangeSummary": fake.sentence()[:-1]
            })

df_versions = pd.DataFrame(versions)

# Sort entire table by ModifiedAt globally
df_versions = df_versions.sort_values("ModifiedAt").reset_index(drop=True)

# Assign VersionID based on global ModifiedAt order
df_versions["VersionID"] = range(1, len(df_versions) + 1)

# Re-number VersionNumber sequentially per doc (ordered by ModifiedAt)
df_versions["VersionNumber"] = df_versions.groupby("DocID").cumcount() + 1

# Reorder columns for clarity
df_versions = df_versions[["VersionID", "DocID", "VersionNumber", "ModifiedByUserID", "ModifiedAt", "ChangeSummary"]]

print(f"Total versions: {len(df_versions)}")
print(f"Docs covered:  {df_versions['DocID'].nunique()} / {len(df_docs)}")

# 9. PasswordProtection Table
passwords = []
protected_docs = df_docs[df_docs["IsPasswordProtected"] == True]["DocID"].tolist()
for i, doc_id in enumerate(protected_docs, 1):
    passwords.append({
        "ProtectionID": i,
        "DocID": doc_id,
        "PasswordHash": fake.sha256(),
        "EncryptionMethod": "AES-256",
        "LastUpdatedAt": fake.date_time_between(start_date="-6m", end_date="now")
    })
df_passwords = pd.DataFrame(passwords)

# 10. Tag table
from datetime import datetime

tags = []

tag_data = [
    ("Legal", "Compliance"),
    ("Tax", "Finance"),
    ("Draft", "Internal"),
    ("Final", "Internal"),
    ("HR", "Administration"),
    ("Technical", "Engineering"),
    ("Invoice", "Finance")
]

for i, (name, category) in enumerate(tag_data, 1):
    tags.append({
        "TagID": i,
        "TagName": name,
        "TagCategory": category,
        "CreatedAt": fake.date_time_between(start_date="-2y", end_date="now")
    })

df_tags = pd.DataFrame(tags)


# 11. Document Tags table
doc_tags = []
existing_doc_tags = set()
df_tags = pd.DataFrame(tags)

for _, doc in df_docs.iterrows():

    doc_id = doc["DocID"]
    org_id = doc["OrganizationID"]

    # Assign 1–3 tags per document
    num_tags = random.randint(1, 3)

    # Choose unique tags for this document
    tag_choices = random.sample(
        df_tags["TagID"].tolist(),
        k=min(num_tags, len(df_tags))
    )

    for tag_id in tag_choices:

        key = (doc_id, tag_id)

        if key in existing_doc_tags:
            continue

        existing_doc_tags.add(key)

        doc_tags.append({
            "DocID": doc_id,
            "TagID": tag_id,
            "OrgID": org_id  # Logically derived from Document
        })

df_doc_tags = pd.DataFrame(doc_tags)

=


# 3. Exporting to SQL
tables = {
    'Roles': df_roles,
    'Organizations': df_orgs,
    'Users': df_users,
    'Policies': df_policies,
    'Documents': df_docs,
    'Permissions': df_permissions,
    'Logs': df_logs,
    'Versions': df_versions,
    'Passwords': df_passwords,
    'Tags': df_tags,
    'Document_Tags': df_doc_tags
}

for table_name, df in tables.items():
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
            conn.commit()
        df.to_sql(name=table_name, con=engine, if_exists='fail', index=False, chunksize=1000)
        print(f"Table '{table_name}' success.")
    except Exception as e:
        print(f" Error in '{table_name}': {e}")

print("\n Done!")
