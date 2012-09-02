import wsgiref.handlers
from public_request_handlers import *

#entrypoint
def main():
	application = webapp.WSGIApplication(
                                       [('/(.*)', RepsRequestHandler)],
                                       debug=True)
	
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
	main()
