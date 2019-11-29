def get_content_type(response):
    return next(x for x in response.headers if x[0] == "Content-Type")[1]
