## Database design

### Database Schema

Credentials(<ins>username</ins>, password, type)
> This table will hold the credentials of the users and organizers. 
- username is a key here.
- password will be currently stored in plain text.
- type here refers to either user or organizer.
- In the future we can look into hashing passwords in our database


UserPreferences(<ins>username</ins>, safesearch, view, type)
> This table stores the user preferences.
- safesearch can be true or false for both user/organizer.
- An organizer will be able to see their own events in their dashboard regardless of safesearch preference.
- view would be if user prefers calendar or list views.
- type indicates if it is a user or an organizer.


OrganizerDetails(<ins>username</ins>, <ins>name</ins>, averageRating, minRating, maxRating, numRating, <ins>logoID</ins>)
> This table details about the organizer
- username may only belong to organizers.
- averageRating, minRating, maxRating are self-explanatory.
- numRating is the number of ratings the organizer has received.


OrganizerEventDetails(username, <ins>eventID</ins>)
> This table stores details about the events that belong to an organizer
- username may only belong to organizers.
- eventIDs for the events an organizer has organized


UserDetails(<ins>username</ins>, campus, degree, year, department, sex)
> Contains information that can help organizers target certain target user audiences
- username here only includes user, organizers do not need to provide details.
- campus can take one of three values: UTSG, UTSC, UTM
- degree can be either undergraduate/graduate programs
- year is a value between (1, 2, 3, 4, PEY)
- department is the list of departments under the University of Toronto
- sex refers to the either male or female


EventDetails(<ins>eventID</ins>, name, description, eventType, venue, startDate, endDate, startTime, endTime, link, bannerID, additionalInfo)
> This table contains information about a specific event
- name is the name of the event, we can set a 50 character limit here to avoid misuse
- description is a text based summary of the event. We can limit it by 100 characters to keep it short and sweet.
- eventType can be online, in-person, hybrid
- venue can be the place for in-person events for in-person events or hybrid events.
- venue can be set to the platform for online events like Zoom, Google Meet etc.
- startDate, endDate, startTime, endTime are self-explanatory
- link can be either a link to the online venue or a redirection to another website. It can also be set to NULL
- bannerID is the id of the image which will need to be loaded for the event
- additionalInfo is a place for the organizer to add details/notes/instructuons for potential attendees.


EventGraphicsBucket(<ins>bannerID</ins>, bannerImage)
> This is a bucket that maps bannerIDs to actual images
- Stores images for a specific bannerID
- Note bannerImages is not a key and can hold duplicates.


OrganizerLogoBucket(<ins>logoID</ins>, logoImage)
> This is a bucket that maps logoIDs to actual images
- Stores images for a specific logoID
- Note logoImages is not a key and can hold duplicates.

UserDetails(<ins>username</ins>, campus, degree, year, department, sex)


### Database Integrity Constraints
- Credentials[type] = {'user', 'organizer'}
- UserPreferences[safesearch] = {'true', 'false'}; The deafult is false
- UserPreferences[view] = {'calendar', 'list'}; The default is list
- UserPreferences[username] \<subset\> Credentials[username]
- OrganizerDetails[username] \<subset\> Credentials[username, type = 'organizer']
- OrganizerDetails[averageRating] = [0, 5]; Precision upto 1 decimal place
- OrganizerDetails[minRating] = [0, 5]; Only integers
- OrganizerDetails[maxRating] = [0, 5]; Only integers
- OrganizerDetails[logoID] \<subset\> OrganizerLogoBucket[logoID]
- OrganizerEventDetails[username] \<subset\> Credentials[username, type = 'organizer']
- OrganizerEventDetails[eventID] \<subset\> EventDetails[eventID]
- UserDetails[username] \<subset\> Credentials[username, type = 'user']
- UserDetails[campus] = {'UTSG', 'UTSC', 'UTM'}
- UserDetails[degree] = {'UG', 'M', 'PG'}; undergrad, master and postgrad respectively
- UserDetails[year] = {'1', '2', '3', '4', 'PEY', '5'}; 5 is for post grads in their fifth year or repeat students
- UserDetails[department] = {'Engineering', 'Arts And Science', 'Rotman'}; Others can be added later
- UserDetails[sex] = {'M', 'F'}
- EventDetails[bannerID] \<subset\> EventGraphicsBucket[bannerID]
- EventDetails[eventType] = {'online', 'in-person', 'hybrid'}