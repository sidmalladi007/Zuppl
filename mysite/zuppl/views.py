from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.core.urlresolvers import reverse
from datetime import datetime, timezone
import hashlib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from .models import Event, Comment, Profile
from django.contrib.auth.models import User

# Redirect to index page. Show "Sign In" on the navigation if user is not
# logged in, or "Sign Out" if the user has already been authenticated.
def index(request):
    if request.user.is_authenticated():
        context = {'logged_in': True}
    else:
        context = {'logged_in': False}
    return render(request, 'zuppl/index.html', context)

# Basic view for 'Sign Up' link on homepage to redirect to sign up page.
def sign_up(request):
    return render(request, 'zuppl/signup.html')

# Basic view for navigation link to redirect to login page.
def sign_in(request):
    return render(request, 'zuppl/login-page.html')

# If there is 1 existing user instance with a selected username, return true.
def username_exists(username):
    if User.objects.filter(username=username).count():
        return True
    else:
        return False

# If an account has previously been created with an email account, return True.
def email_exists(email):
    if User.objects.filter(email=email).count():
        return True
    else:
        return False

# Ensures that there is at least one number and one letter in the proposed
# password to make it valid.
def password_valid(password):
    one_letter = False
    one_number = False
    for char in password:
        # Check for number.
        if char.isdigit():
            one_number = True
        # Check for letter.
        if char.isalpha():
            one_letter = True
    if one_letter and one_number:
        return True
    else:
        return False

# Retrieves user's credentials and creates a new account after validating the 
# form.
def create_account(request):
    # Enforces the use of POST data for user creation.
    if request.method == "GET":
        return render(request, 'zuppl/signup.html')
    if request.method == "POST":
        # Retrieve form data or empty string if none exists.
        fName = request.POST.get('firstname', '')
        lName = request.POST.get('lastname', '')
        userEmail = request.POST.get('email', '')
        uName = request.POST.get('username', '')
        uPwd = request.POST.get('password', '')
        uPwdConfirm = request.POST.get('confirm-password', '')
        userUniversity = request.POST.get('college', '')
    # Ensure that the username has not already been taken.
    if username_exists(uName):
        context = {'error_usernameTaken': True}
        return render(request, 'zuppl/signup.html', context)
    # Ensure that an account has not already been made with the inputted email.
    if email_exists(userEmail):
        context = {'error_emailExists': True}
        return render(request, 'zuppl/signup.html', context)
    # Ensure that each password has at least one letter and one number.
    if not password_valid(uPwd):
        context = {'error_passwordStructure': True}
        return render(request, 'zuppl/signup.html', context)
    # For now, Zuppl was built to be available only at CMU and Pitt.
    if (userUniversity == "No Option"):
        context = {'error_university': True}
        return render(request, 'zuppl/signup.html', context)
    # Ensure that none of the sign up fields were left blank.
    if (fName == '' or lName == '' or userEmail == '' or uName == '' or 
        uPwd == '' or uPwdConfirm == '' or userUniversity == ''):
        context = {'incomplete_fields': True}
        return render(request, 'zuppl/signup.html', context)
    # Make sure that the hash of 'Password' and 'Confirm Password' match.
    if hash(uPwd) != hash(uPwdConfirm):
        context = {'password_mismatch': True}
        return render(request, 'zuppl/signup.html', context)
    # Execute the following if all sign up validation criteria are met.
    securePass = hashlib.sha224(uPwd.encode('utf-8')).hexdigest()
    # Uses Django's built-in create_user helper function to work with login.
    new_user = User.objects.create_user(username=uName, email=userEmail, 
        password=securePass, first_name=fName, last_name=lName)
    # Create and save a new instance of Profile for every User instance created.
    new_profile = Profile(user=new_user, college=userUniversity)
    new_profile.save()
    # Customize login screen to include user information (i.e. full name).
    context = {'new_user': new_user}
    return render(request, 'zuppl/login-page.html', context)

# Obtain information from the database to populate on the user's profile page.
def getProfileContext(user, profile):
    profileContext = {}
    college = profile.college
    profileContext['college'] = college
    # Only the events at the user's campus are relevant.
    collegeEvents = Event.objects.filter(campus=college)
    numCollegeEvents = len(collegeEvents)
    profileContext['numCollegeEvents'] = numCollegeEvents
    # Organize user-created and RSVPed Zuppls.
    attendingEvents = profile.eventset.all()
    numAttendingEvents = len(attendingEvents)
    profileContext['numAttendingEvents'] = numAttendingEvents
    user_fullName = user.get_full_name()
    createdEvents = Event.objects.filter(created_by=user_fullName)
    numCreatedEvents = len(createdEvents)
    profileContext['numCreatedEvents'] = numCreatedEvents
    return profileContext

# Uses Django's built-in authenticate and login functionalities to automate
# creating user sessions, but I did not use the built-in view to handle the
# process.
# The following code was inspired by Django's recommended implementation on:
# https://docs.djangoproject.com/en/1.8/topics/auth/default/
def profile(request):
    if not request.user.is_authenticated():
        # Never crashes if there is no POST data. Will revert to empty string.
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # Checks the hashed values of entered password and actual password using
        # Python's built-in hashlib module.
        securePass = hashlib.sha224(password.encode('utf-8')).hexdigest()
        user = authenticate(username=username, password=securePass)
        if user is not None:
            if user.is_active:
                # Creates a user session.
                login(request, user)
                # Create context to customize profile with welcome text using 
                #the user's information (i.e. full name).
                user = User.objects.get(username=username)
                profile = user.profile
                context = getProfileContext(user, profile)
                context['just_logged_in'] = True
                return render(request, 'zuppl/profile.html', context)
            else:
                # Create provision for disabled accounts that violated terms of 
                # use.
                context = {'disabled': True}
                return render(request, 'zuppl/login-page.html', context)
        else:
            # Redirect back to the login page if username and/or password
            # credentials are incorrect.
            context = {'incorrect_creds': True}
            return render(request, 'zuppl/login-page.html', context)
    # If the user is already logged in, allow him/her to access the profile
    # page directly without further authentication processes.
    else:
        user = request.user
        profile = request.user.profile
        context = getProfileContext(user, profile)
        return render(request, 'zuppl/profile.html', context)

# Pass the event objects that the user has created (and holds administrative
# rights over) to the template.
def my_events(request):
    user_fullName = request.user.get_full_name
    preliminary_list = Event.objects.filter(created_by=user_fullName)
    # Order the Zuppls from most recent to least recent.
    events_list = preliminary_list.order_by('-created_date')
    context = {'events': events_list, 'myEvents': True}
    # Indicate if there are no "My Events", and display an appropriate message.
    if len(events_list) == 0:
        context['noMyEvents'] = True
    return render(request, 'zuppl/my-zuppls.html', context)

# Display the events to which the user has RSVPed to attend.
def attending_events(request):
    user = request.user
    profile = user.profile
    preliminary_list = profile.eventset.all()
    # Order the events in the order of occurrence.
    events_list = preliminary_list.order_by('-start_time')
    context = {'events': events_list, 'attendingEvents': True}
    # Display a custom message if the user has not RSVPed to any Zuppls.
    if len(events_list) == 0:
        context['noAttendingEvents'] = True
    return render(request, 'zuppl/my-zuppls.html', context)

"""
The following few funtions are important and algorithmically complex
because they are used to calculate how "trending" all the events are. This
intelligent event indexing mechanism shows the user only the most relevant
and 'hot' information upfront. Since Zuppl is a product targeted towards
college-going demographics and psychographics, showing them real-time insights
of the buzz is an important value proposition.

The trendRank algorithm uses five metrics to gauge the trend of each Zuppl. The
total number of attendees and the number of comments are indicators of 
trendiness, and they inflate the trendScore. On the other hand, elapsed time 
since the event's creation, total number of students who attend that campus, 
and costs of attending (especially for free events where commitment is low) 
often tend to deflate the trendScore (though not always).
"""

# Uses elapsed time in seconds to exponentially decrease the trendScore by
# returning a multiplier that's < 1.
def timeComponent(startingTime):
    endingTime = datetime.now(timezone.utc)
    timeDelta = endingTime - startingTime
    elapsedTime = timeDelta.total_seconds()
    # This is the proportion of the trendScore that would remain after each
    # elapsed second.
    deflationPerSecond = 0.99999999
    finalMultiplier = deflationPerSecond**elapsedTime
    return finalMultiplier

# The total number of college users is inversely proportional to the trendscore.
# For instance, 10 RSVPs to an event would be more impressive if the total
# user adoption rate for the college was only 20.
def numCollegeUsersComponent(college):
    allProfiles = Profile.objects.filter(college=college)
    profilesCount = allProfiles.count()
    deflationPerUser = 0.99
    finalMultiplier = deflationPerUser**profilesCount
    return finalMultiplier

# If many people are willing to pay to attend events, that indicates greater
# trendiness. However, since RSVP lists often swell up for free events, there
# is a deflation mechanism to account for it.
def costComponent(cost):
    # Decrease the trendiness of an event if it's free and many people are
    # signing up, versus an event that costs money and many people sign up.
    if cost == "Free":
        finalMultiplier = 0.75
    else:
        # Attempt to iterate through the string and identify the cost.
        numDigits = 0
        for character in cost:
            if character.isdigit():
                numDigits += 1
        # A decimal point indicates a cents value, so the digits of the dollar
        # amount are decreased by two.
        if "." in cost:
            numDigits -= 2
        if numDigits == 1:
            finalMultiplier = 1.1
        elif numDigits == 2:
            finalMultiplier = 1.3
        elif numDigits > 2:
            finalMultiplier = 2.0
        else:
            finalMultiplier = 1.0
    return finalMultiplier

# Commenting on events shows that they are generating a lot of buzz and
# conversation.
def commentsComponent(event):
    comments = event.comment_set
    numComments = comments.count()
    # Each comment is worth half a trendScore point.
    scorePerComment = 0.5
    addedScore = scorePerComment * numComments
    return addedScore

# The number of people who choose to attend is the most defining factor of
# trendiness.
def attendeesComponent(event):
    attendees = event.attendees
    numAttendees = attendees.count()
    # Each attendee increases the trendScore by 1.0.
    scorePerAttendee = 1.0
    addedScore = scorePerAttendee * numAttendees
    return addedScore

# Assigns the trendScore for each individual event so that the trendRank
# function can index them accordingly.
def getTrendScore(event):
    trendScore = 0
    # Attendees and comments directly sum up to a greater trendScore.
    trendScore += attendeesComponent(event)
    trendScore += commentsComponent(event)
    startingTime = event.created_date
    timeDeflation = timeComponent(startingTime)
    # The remaining three factors have multiplied or even exponential effects
    # on the final trendScore.
    trendScore *= timeDeflation
    collegeCampus = event.campus
    totalUsersDeflation = numCollegeUsersComponent(collegeCampus)
    trendScore *= totalUsersDeflation
    eventCost = event.cost
    costDeflation = costComponent(eventCost)
    trendScore *= costDeflation
    return trendScore

# The secret sauce algorithm that orders the trending events such that the
# best and hottest receive greatest visibility.
def trendRank(events):
    trendDictionary = {}
    for event in events:
        # The unique trendScore is the key that points to the event object.
        trendScore = getTrendScore(event)
        trendDictionary[trendScore] = event
    lowestToHighestTrendsDictionary = sorted(trendDictionary)
    # Order the keys by highest to lowest trendScores.
    sortedTrendDictionary = lowestToHighestTrendsDictionary[::-1]
    trendingEvents = []
    # For the highest to lowest trendScores, append the event objects in the
    # same order to create a list of most trending to least trending Zuppls.
    for trendScore in sortedTrendDictionary:
        trendingEvents.append(trendDictionary[trendScore])
    return trendingEvents

# Generates the trending view when discovering Zuppls.
def trending_zuppls(request):
    user = request.user
    profile = user.profile
    college = profile.college
    # Only handle the events that are pertinent to the user's college campus.
    preliminary_list = Event.objects.filter(campus=college)
    # Rank them using the proprietary algorithm.
    events_list = trendRank(preliminary_list)
    context = {'events': events_list, 'trendingZuppls': True}
    # Display an appropriate message if there are no trending events.
    if len(events_list) == 0:
        context['noTrendingZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# Order the Zuppls to explore by how recently they were created.
def recent_zuppls(request):
    user = request.user
    profile = user.profile
    college = profile.college
    # Only handle the events that are pertinent to the user's college campus.
    preliminary_list = Event.objects.filter(campus=college)
    # The parameter created_date gets automatically filled in the database
    # the moment that the Zuppl gets created.
    events_list = preliminary_list.order_by('-created_date')
    context = {'events': events_list, 'recentZuppls': True}
    if len(events_list) == 0:
        context['noRecentZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# Sort Zuppls by how soon in the future the events take place.
def soon_zuppls(request):
    user = request.user
    profile = user.profile
    college = profile.college
    # Only handle the events that are pertinent to the user's college campus.
    preliminary_list = Event.objects.filter(campus=college)
    # Sort by when the event starts.
    events_list = preliminary_list.order_by('start_time')
    context = {'events': events_list, 'soonZuppls': True}
    if len(events_list) == 0:
        context['noSoonZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# The detail page shows only that one Zuppl, along with all comments and the
# ability to create comments.
def detail(request, event_id):
    event = Event.objects.get(id=event_id)
    # Comments, as I designed in models.py, are automatically sorted by when
    # they were created.
    comments = event.comment_set.all()
    if len(comments) > 0:
        context = {'event': event, 'comments': comments}
    # Display an appropriate message if no comments have been created.
    else:
        context = {'event': event, 'noComments': True}
    return render(request, 'zuppl/detail.html', context)

# Navigates to the Create Zuppl page.
def create_page(request):
    return render(request, 'zuppl/create-zuppl.html')

# Handles the POST request from the submitted Create Zuppl form to create a
# new event.
def add_zuppl(request):
    if request.method == "POST":
        user = request.user
        full_name = user.get_full_name()
        userProfile = user.profile
        # Capture all fields of the form, or an empty string if there was no
        # input.
        eventName = request.POST.get('eventname', '')
        # Automatically log the user who created the event to later grant him/
        # her administrative rights to edit or delete the Zuppl.
        created_by = full_name
        location = request.POST.get('location', '')
        university = user.profile.college
        startingTime = request.POST.get('starting', '')
        endingTime = request.POST.get('ending', '')
        price = request.POST.get('price', '')
        organizer = request.POST.get('organizer', '')
        organizerEmail = request.POST.get('organizer_email', '')
        details = request.POST.get('details', '')
        # Perform form validation, and send the user back to the Create Zuppl
        # page if there were any missing fields.
        if (eventName == '' or location == '' or startingTime == '' or 
            endingTime == '' or price == '' or organizer == '' or 
            organizerEmail == '' or details == ''):
            context = {'missed_field': True}
            return render(request, 'zuppl/create-zuppl.html', context)
        # If all fields are valid, create the event instance and save it to the
        # database.
        else:
            event = Event(name=eventName, created_by=created_by, 
                location=location, campus=university, start_time=startingTime,
                end_time=endingTime, cost=price, organizer=organizer, 
                organizer_email=organizerEmail, details=details)
            event.save()
    # Immediately redirect the user to the Recently Created Zuppls page so that
    # he/she can view the event that was just created.
    preliminary_list = Event.objects.filter(campus=university)
    events_list = preliminary_list.order_by('-created_date')
    context = {'events': events_list, 'recentZuppls': True, 
        'zupplSuccess': True}
    if len(events_list) == 0:
        context['noRecentZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# Takes the user (event creator) to the Edit Zuppl page where the fields are
# already pre-filled.
def edit_page(request, event_id):
    event = Event.objects.get(id=event_id)
    context = {'event': event}
    return render(request, 'zuppl/edit.html', context)

# Handles the POST data from editing a Zuppl, and updates the information
# in the database.
def edit_zuppl(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == "POST":
        user = request.user
        userProfile = user.profile
        # Retrieve the POST data, whether it was updated by the user or not.
        eventName = request.POST.get('eventname', '')
        location = request.POST.get('location', '')
        startingTime = request.POST.get('starting', '')
        endingTime = request.POST.get('ending', '')
        price = request.POST.get('price', '')
        organizer = request.POST.get('organizer', '')
        organizerEmail = request.POST.get('organizer_email', '')
        details = request.POST.get('details', '')
        # Perform form validation and take the user back to the Edit Zuppl page
        # if a field was not filled out.
        if (eventName == '' or location == '' or startingTime == '' or 
            endingTime == '' or price == '' or organizer == '' or 
            organizerEmail == '' or details == ''):
            context = {'missed_field': True, 'event': event}
            return render(request, 'zuppl/edit.html', context)
        else:
            # If a user-inputted attribute of an event was changed, update the
            # respective information in the database and save it.
            if event.name != eventName:
                event.name = eventName
            if event.location != location:
                event.location = location
            if event.start_time != startingTime:
                event.start_time = startingTime
            if event.end_time != endingTime:
                event.end_time = endingTime
            if event.cost != price:
                event.cost = price
            if event.organizer != organizer:
                event.organizer = organizer
            if event.organizer_email != organizerEmail:
                event.organizer_email = organizerEmail
            event.save()
            university = userProfile.college
            # Take the user back to the event discovery page, and show a
            # success message that the Zuppl was updated.
            preliminary_list = Event.objects.filter(campus=university)
            events_list = preliminary_list.order_by('-created_date')
            context = {'events': events_list, 'recentZuppls': True, 
                'zupplEdited': True}
            if len(events_list) == 0:
                context['noRecentZuppls'] = True
            return render(request, 'zuppl/discover-zuppls.html', context)

# Handles the deletion of the Zuppl that can be performed from within the
# Edit Zuppl page.
def delete_zuppl(request, event_id):
    removedEvent = Event.objects.get(id=event_id)
    removedEvent.delete()
    user = request.user
    profile = user.profile
    college = profile.college
    # After deletion, navigate the user to the Trending Zuppls page, and
    # show a confirmation message that the Zuppl was successfully deleted.
    preliminary_list = Event.objects.filter(campus=college)
    events_list = trendRank(preliminary_list)
    context = {'events': events_list, 'trendingZuppls': True, 
        'deletedZuppl': True}
    if len(events_list) == 0:
        context['noTrendingZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# Handle the RSVP functionality, and add the user to the list of event
# attendees.
def attend(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user
    profile = user.profile
    # By virtue of the Many-to-Many Relationship:
    profile.eventset.add(event)
    # Navigate the user to the Attending Events page so that he/she can view
    # the Zuppl on his/her personal profile dashboard.
    preliminary_list = profile.eventset.all()
    events_list = preliminary_list.order_by('-start_time')
    context = {'events': events_list, 'attendingEvents': True, 
        "addedEvent": True}
    if len(events_list) == 0:
        context['noAttendingEvents'] = True
    return render(request, 'zuppl/my-zuppls.html', context)

# Handles the functionality of a user 'unsubscribing' from an event.
def leave(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user
    profile = user.profile
    # By virtue of the Many-to-Many Relationship:
    profile.eventset.remove(event)
    # Navigate the user to the Attending Events page to view the remaining
    # Zuppls that he/she is still subscribed to.
    preliminary_list = profile.eventset.all()
    events_list = preliminary_list.order_by('-start_time')
    context = {'events': events_list, 'attendingEvents': True, 
        "leftEvent": True}
    if len(events_list) == 0:
        context['noAttendingEvents'] = True
    return render(request, 'zuppl/my-zuppls.html', context)

# Receives the POST data from the Create Comment form, and stores a new comment
# for a particular event.
def add_comment(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user
    if request.method == "POST":
        # Extract the comment text from the POST data.
        comment_text = request.POST.get('comment', '')
        # Perform form validation to ensure that the comment has content.
        if comment_text == '':
            context = {'event': event, 'invalid_comment': True}
            return render(request, 'zuppl/detail.html', context)
        # Once validated, save the comment and connect it with the event and 
        #user for whom it's a foreign key.
        else:
            comment = Comment(event=event, user=user, text=comment_text)
            comment.save()
            event.comment_set.add(comment)
            # Take the user back to the Zuppl detail page to see the comment.
            allComments = event.comment_set.all()
            context = {'event': event, 'comments': allComments, 
                'addedComment': True}
            return render(request, 'zuppl/detail.html', context)

# Handles the deletion of an event's comment that the same user has created
# in the first place.
def delete_comment(request, comment_id):
    desiredComment = Comment.objects.get(id=comment_id)
    desiredComment.delete()    
    user = request.user
    profile = user.profile
    college = profile.college
    # Navigate the user to the Discover Trends page, and display a message that
    # the deletion was successful.
    preliminary_list = Event.objects.filter(campus=college)
    events_list = trendRank(preliminary_list)
    context = {'events': events_list, 'trendingZuppls': True, 
        'commentDeleted': True}
    if len(events_list) == 0:
        context['noTrendingZuppls'] = True
    return render(request, 'zuppl/discover-zuppls.html', context)

# Ends the user's session, securely logs him/her out, and navigates him/her
# back to the login page.
def sign_out(request):
    logout(request)
    context = {'logout_success': True}
    return render(request, 'zuppl/login-page.html', context)