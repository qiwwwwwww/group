from threading import Thread

# allow send_email function to return immediately
# a useful framework for asynchronous taks 
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
