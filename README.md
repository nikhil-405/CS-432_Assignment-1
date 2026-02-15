# CS-432_Assignment-1
## Assignment 1: SafeDocs

**GitHub Repository:**  
https://github.com/nikhil-405/CS-432_Assignment-1

**Team Members:**  
Harshita Singh, Dhruv Goel, Nikhil Goyal, Chinmay Pendse, Vedant Sharan  

**Date:** February 15, 2026

---

## 1. Project Overview

Our system, **SafeDocs**, a Secure PDF Management System, focuses on enforcing data integrity, normalization, and systematic conceptual modeling. The design ensures that document storage is not only scalable but also adheres to strict role-based access control and audit requirements.

The development of SafeDocs followed a structured database design methodology to ensure correctness, scalability, and security. The design process began with requirement analysis, where the core objectives of secure document management, access control, and auditability were identified.

The system was first modeled conceptually using a UML Class Diagram to represent entities, attributes, behaviors, and relationships at a high level. This allowed clear visualization of ownership, dependencies, and system responsibilities without focusing on implementation constraints.

Next, the UML model was transformed into an Entity-Relationship (ER) model by removing behavioral methods and focusing on data representation, keys, and constraints. Relationships were refined using cardinality and participation constraints to maintain referential integrity and eliminate ambiguity.

Normalization principles were applied to reduce redundancy and ensure consistency across tables. Associative entities were introduced where necessary to resolve many-to-many relationships. Integrity constraints such as primary keys, foreign keys, and logical constraints were incorporated to preserve correctness of data throughout the system lifecycle.

This methodology ensured a smooth transition from conceptual design to logical database modeling while maintaining security, modularity, and extensibility.

---

## 2. Methodology

To obtain the data, we used a Python script [data_generation.py] that generated Pandas dataframes, which were then converted into SQL tables. Later, additional definitions, such as primary key, not null, etc., were manually added in MySQL Workbench for added safety. For creating the diagrams, we used the Mermaid platform, which converts code into high-definition flowcharts. The codes for the main ER Diagram and the UML diagram have been provided in the [/Figures] section. All the high-definition figures have been provided in the [/Figures] folder. We have considered making some function-wise UML diagrams, which also illustrate the inner workings. 

Main UML
![UML](Figures/SafeDocs_main_UML.png)

Main ER
![ER](Figures/SafeDocs_ER_Diagram.png)

---

## 3. Core Technical Functionalities

The system implements various functionalities; the five core functionalities out of these are as follows:

1. **Identity & Access Management (IAM):**  
   Utilizing the User, Role, and Permission entities to manage authenticated access.

2. **Dynamic Policy Enforcement:**  
   The Policy entity classifies documents and restricts access based on MaxAllowedRoleID.

3. **Audit Logging & Tracking:**  
   The Log entity records actions, timestamps, and IP addresses to maintain a transparent audit trail.

4. **Version Control:**  
   Automatic tracking of document changes via the Version entity, allowing for historical rollbacks.

5. **Security & Encryption:**  
   Management of document security through password hashing and encryption method metadata.

A detailed overview of other functionalities can be viewed in the UML diagram.

---

## 4. Conceptual Modeling: UML Class Diagram

The UML diagram serves as our high-level conceptual blueprint. It identifies classes, their internal attributes, and functional methods.

### 4.1 Key Classes and Attributes

- **User (Member Table):** Includes required attributes such as Name, Age, Email, and ContactNumber.
- **Document:** The central entity containing metadata like ConfidentialityLevel and IsPasswordProtected.
- **Methods:** Behavior is defined through methods such as `verifyAccess(UserID)` in the Document class and `exportAuditTrail()` in the Log class.

### 4.2 Structural Relationships

The design utilizes composition and aggregation to show ownership:

- **Composition:** The Permission and Version entities are shown with a black diamond, indicating they are part of the Document lifecycle and cannot exist independently.
- **Multiplicity:** Standard UML conventions are followed (e.g., 1..* for Organization to User) to represent hierarchy.

### 4.3 Entities Present

- Document  
- Document Tag (Associative Entity)  
- Log  
- Organization  
- Password  
- Permission  
- Policy  
- Role  
- Tag  
- User  
- Version  

### 4.4 Attributes in Each Table

- **Document:** DocID, DocName, DocSize, NumberOfPages, FilePath, ConfidentialityLevel, IsPasswordProtected, OwnerUserID, OrganizationID, CreatedAt, LastModifiedAt

- **Document Tag:** DocID, TagID, OrgID

- **Log:** LogID, UserID, DocID, ActionType, ActionTimestamp, IPAddress

- **Organization:** OrganizationID, OrgName, OrgType, Address, CreatedAt

- **Password:** ProtectionID, DocID, PasswordHash, EncryptionMethod, LastUpdatedAt

- **Permission:** PermissionID, DocID, UserID, AccessType, GrantedAt

- **Policy:** PolicyID, LevelName, MaxAllowedRoleID, Description

- **Role:** RoleID, RoleName, Description

- **Tag:** TagID, TagName, TagCategory, CreatedAt

- **User:** UserID, Name, Email, ContactNumber, Age, RoleID, OrganizationID, AccountStatus

- **Version:** VersionID, DocID, VersionNumber, ModifiedByUserID, ModifiedAt, ChangeSummary

### 4.5 How Entities Are Related (Main)

- **Organization – User (Employs):** An Organization can employ multiple Users, establishing a one-to-many (1:N) relationship. Each User is associated with exactly one Organization through OrganizationID.

- **Role – User (Assigned to):** A single Role can be assigned to many Users (1:N). Each User is assigned exactly one Role.

- **Role – Policy (Defines Access Limit):** One Role may define multiple Policies (1:N).

- **Policy – Document (Classifies):** Each Document is classified under one Policy, while a Policy can classify multiple Documents (1:N).

- **User – Document (Owns):** A User can own multiple Documents (1:N). Each Document has exactly one owner.

- **Document – Version (Tracks):** A Document can have multiple Versions (1:N).

- **Document – Password (Secures):** A Document may optionally have one Password (1:0..1).

- **User – Log (Triggers):** A User can generate multiple Log entries (1:N).

- **Document – Log (Records):** A Document can have multiple associated Log entries (1:N).

- **Document – Tag (Categorization):** Document and Tag share a many-to-many (M:N) relationship resolved through the Document Tag associative entity.

### 4.6 Methods to Be Used

- **Organization:** createOrg(), getMembers(), removeOrg()  
- **Role:** getPermissions(), revokePermissions()  
- **Policy:** isRoleAllowed(RoleID)  
- **User:** login(), deactivate(), roleModification()  
- **Document:** upload(), archive(), verifyAccess(UserID)  
- **Version:** rollback()  
- **Password:** validateHash()  
- **Permission:** grant(), revoke()  
- **Log:** exportAuditTrail()

---

## 5. Logical Modeling: ER Diagram

The ER diagram converts UML classes into database entities, focusing on keys and relational constraints.

### 5.1 Entity-Relationship Mappings

- **Primary Keys (PK):** All entities have unique identifiers (e.g., OrgID, UserID, DocID).
- **Mapping Tables:** The M:N relationship between Document and Tag is resolved through the Document Tag intersection table.
- **Foreign Keys (FK):** Directed relationships indicate foreign key flow, such as RoleID assigned to User.

### 5.2 How Entities Are Related (Main)

- Organization – User (Employs)
- Role – User (Assigned)
- Role – Policy (Defines)
- Policy – Document (Classifies)
- User – Document (Created By / Owns)
- Document – Version (History)
- Document – Password (Secures)
- User – Document – Permission (Governs)
- User – Log (Triggers)
- Document – Log (Records)
- Document – Tag (Has Tag / Tagged In)

### 5.3 Cardinality Constraints

- Organization – Employs – User: N:1  
- Role – Assigned – User: 1:N  
- Role – Defines – Policy: 1:N  
- Policy – Classifies – Document: 1:N  
- User – Created By – Document: 1:N  
- Document – History – Version: 1:N  
- Document – Secures – Password: 1:0..1  
- User – Triggers – Log: 1:N  
- Document – Records – Log: 1:N  
- Document – Has Tag – Document Tag: 1:N  
- Tag – Tagged In – Document Tag: 1:N  
- User – Holds – Permission: 1:N  
- Document – Governs – Permission: 1:N  

### 5.4 Participation Constraints

- Version has total participation in the History relationship.
- Password has total participation in the Secures relationship.
- Document has total participation in identifying relationships for Version and Password.
- Log has total participation in both Records and Triggers relationships.
- Organization, Role, Tag, and Policy show partial participation.

---

## 6. Transition and Normalization Logic

### 6.1 UML to ER Transition

The transition involved several critical steps:

- **Method Stripping:** UML methods were abstracted into application-layer functionality while ER focused on data representation.
- **Cardinality Adjustment:** UML associations were translated into foreign key constraints to ensure referential integrity.

### 6.2 Integrity Constraints

- **NOT NULL Constraints:** At least three columns in every table are marked NOT NULL.
- **Referential Integrity:** Foreign keys prevent orphaned records.
- **Logical Constraints:** Rules such as `LastModifiedAt >= CreatedAt` are enforced at the schema level.

---

## 7. Team Contributions

- **Harshita Singh:** Documentation  
- **Dhruv Goel:** Formal Verification and Documentation  
- **Nikhil Goyal:** Python Scripting and Diagram Generation  
- **Chinmay Pendse:** Integration with SQL and Diagram Editing  
- **Vedant Sharan:** Code / Constraints Verification
