# We need to hard code access to firestore database emails
# We don't want to use a FastAPI for that, because the url is publicly usable and that would potentially give access to people's email addresses 