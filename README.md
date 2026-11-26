## Features

### User Features

can Register + log-in
can browse events
can add money to wallet
can view transaction history
can book events
can view booking history


### Organization Features

can create events
can edit or delete earlier-created events
can view organization analytics
can mark bookings as consumed


### Superuser Features

can create org accounts


## Database Models and Relationships

### 1. User

Django built-in user model
used for Authentication


### 2. Organization

This model represents an organization that can create and manage events.

One-to-one relationship with a Django user account.


### 3. Wallet

The Wallet model stores a user's wallet balance.

One-to-one relationship with Django user account.

Wallet creation happens automatically on user-account creation (ensured by apps.py and signals.py)

### 4. Transaction

The Transaction model records deposits and bookings.

Each transaction belongs to a wallet.
A wallet can have multiple transactions. (Many-to-one with a wallet)



### 5. Event

The Event model represents an event of an organization.

Each event belongs to one organization.
An organization can create multiple events.(Many to one with organization)
An event can have multiple bookings. (One to many with bookings)
A slot-based event can have multiple time slots. (One to many with slots)

The event_type field distinguishes between ticket-based and slot-based booking. 

### 6. EventSlot

The EventSlot model represents an individual time slot for a slot-based event.

Each slot belongs to one event. 
An event can have multiple slots.(Many to one with Event)
A slot can have multiple bookings. (One to many with bookings)


### 7. Booking

The Booking model represents a user's purchase or reservation.

Each booking belongs to one user. (many to one)
Each booking belongs to one event if event is ticketed. (many to one)
Each booking belongs to an event slot if event is slotted.(many to one)


## Authentication and Authorization

The application uses Django's built-in authentication system and group-based authorization.

### User and Organization Groups

Django groups distinguish ordinary users from organization accounts.

- **`Users`** — Regular user accounts.
- **`Organizations`** — Organization accounts.

The application checks whether the request is from Organizations grp or not and then decides to give access.

### Server-Side Authorization

Users can access their own wallet and booking history.
Organizations can manage only their own events.
Organizations can view and consume bookings associated with their own events.
Organization-only functionality rejects accounts without the required organization access.


