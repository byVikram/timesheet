from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from functools import wraps
import json
from flask import current_app, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from jose import jwt
import secrets
import string

import os
import logging
from logging.handlers import RotatingFileHandler
# from flask import Flask, request, g
# from datetime import datetime

def generateToken(userCode, roleCode, orgCode):
	secret_key = current_app.config['SECRET_KEY']
	expiration_time = current_app.config['ACCESS_TOKEN_EXPIRE_TIME']
	print("Expiration Time:", expiration_time)
	payload = {
			"user_code": userCode,
			"role_code": roleCode,
			"org_code": orgCode,
			'exp': datetime.now(timezone.utc) + timedelta(seconds=int(expiration_time))
		}
	token = jwt.encode(payload, secret_key, algorithm='HS256')
	if token:
		return token
	else:
		return False

def generateRefreshToken(userCode):
	secret_key = current_app.config['SECRET_KEY']
	expiry_seconds = int(current_app.config['REFRESH_TOKEN_EXPIRE_SECONDS'])

	payload = {
		"user_code": userCode,
		"type": "refresh",
		"exp": datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)
	}

	return jwt.encode(payload, secret_key, algorithm="HS256")


def validateRefreshToken(refresh_token):
	secret_key = current_app.config['SECRET_KEY']

	try:
		payload = jwt.decode(refresh_token, secret_key, algorithms=["HS256"])

		if payload.get("type") != "refresh":
			raise ValueError("Invalid token type")

		return True

	except jwt.ExpiredSignatureError:
		return None
	except Exception:
		return None


def tokenValidation(func):
	"""
	Token verification decorator.
	Pass @tokenValidation above a MethodView function (like get).
	If token is valid, it sets self.userCode in the view instance.
	"""

	@wraps(func)
	def wrapper(self, *args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if not auth_header:
			return {"status": "error", "message": "Access is denied"}, 401

		token_parts = auth_header.split(' ')
		if len(token_parts) != 2:
			return {"status": "error", "message": "Access is denied"}, 401

		token = token_parts[1]

		secret_key = current_app.config.get('SECRET_KEY')
		try:
			payload = jwt.decode(token, secret_key, algorithms=['HS256'])

			expiry_time_unix = payload.get('exp')
			if expiry_time_unix:
				expiry_time = datetime.fromtimestamp(expiry_time_unix, tz=timezone.utc)
				current_time = datetime.now(timezone.utc)

				if current_time > expiry_time:
					return {"status": "error", "message": "Your session has timed out. Please log in again."}, 401

			userCode = payload.get('user_code')
			orgCode = payload.get('org_code')

			if not userCode:
				return {"status": "error", "message": "Invalid token: user code missing."}, 401

			# Attach userCode to the instance
			self.userCode = userCode
			self.orgCode = orgCode

			# Call the original function
			return func(self, *args, **kwargs)

		except Exception as e:
			print("Token validation error:", str(e))
			return {"status": "error", "message": "Your session has timed out. Please log in again."}, 401

	return wrapper


def authorize(required_roles):
	"""
	Role-based authorization decorator.
	Usage: @authorize(['admin', 'manager'])
	Works with MethodView instance methods that have self.userCode set by tokenValidation.
	"""

	def decorator(func):
		@wraps(func)
		def wrapper(self, *args, **kwargs):
			# Make sure self.userCode exists (tokenValidation must run first)
			if not hasattr(self, 'userCode'):
				return {"status": "error", "message": "Unauthorized: missing user info"}, 401

			from app.services.user_service import getUserAssignedRole

			user_roles, user_id, org_id,  error = getUserAssignedRole(self.userCode)  # Implement this function

			self.userRole = user_roles
			self.userId = user_id
			self.orgId = org_id

			if error:
				return {"status": "error", "message": error}, 403


			if "ALL" not in required_roles and not any(role in user_roles for role in required_roles):
				return {"status": "error", "message": "Forbidden: insufficient permissions"}, 403


			# Check if user has at least one required role
			# if not any(role in user_roles for role in required_roles):
			# 	return {"status": "error", "message": "Forbidden: insufficient permissions"}, 403

			# Call the original method
			return func(self, *args, **kwargs)
		return wrapper
	return decorator




# def getSuccessMessage(message, data, dataCount=0, page=None, perPage=None, total=None):
# 	"""
# 	Generates a standardized success response.

# 	Args:
# 		message (str): Success message
# 		data (any): The payload (list, dict, or object)
# 		dataCount (int): Count of items (optional)
# 		page (int): Current page number for paginated responses (optional)
# 		per_page (int): Items per page (optional)
# 		total (int): Total items across all pages (optional)

# 	Returns:
# 		dict: Standardized response
# 	"""
# 	message_body = {
# 		"status": "success",
# 		"message": message,
# 		"data": data,
# 	}

# 	# Add data count
# 	if isinstance(data, list):
# 		message_body["dataCount"] = dataCount if dataCount != 0 else len(data)

# 	# Add pagination metadata if provided
# 	if page is not None and perPage is not None and total is not None:
# 		message_body["pagination"] = {
# 			"page": page,
# 			"per_page": perPage,
# 			"total": total,
# 			"total_pages": (total // perPage) + (1 if total % perPage > 0 else 0),
# 		}

# 	return message_body

def getSuccessMessage(message, data):
	"""
	Generates a standardized success response.

	Args:
		message (str): Success message
		data (any): The payload (list, dict, or object)
		dataCount (int): Count of items (optional)
		page (int): Current page number for paginated responses (optional)
		per_page (int): Items per page (optional)
		total (int): Total items across all pages (optional)

	Returns:
		dict: Standardized response
	"""
	message_body = {
		"status": "success",
		"message": message,
		"data": data,
	}

	return jsonify(message_body)


def getErrorMessage(message):
	message_body =  {
		"status": "error",
		"title": "Oops... Something went wrong!",
		"message": message,
	}

	return jsonify(message_body)


def hashPassword(password: str) -> str:
	"""Hash a password for storing in DB."""
	return generate_password_hash(password)


def verifyPassword(hashed_password: str, plain_password: str) -> bool:
	"""Verify a stored password against one provided by user."""
	return check_password_hash(hashed_password, plain_password)


def current_utc_time():
	"""Return current UTC datetime."""
	return datetime.datetime.utcnow()


def paginateQuery(query, page=1, per_page=10):
	"""
	Paginate a SQLAlchemy query and return results + metadata.
	"""
	page = max(1, int(page))
	per_page = max(1, int(per_page))

	total = query.count()  # total items in the query
	items = query.offset((page - 1) * per_page).limit(per_page).all()

	total_pages = (total + per_page - 1) // per_page

	meta = {
		"page": page,
		"per_page": per_page,
		"total": total,
		"total_pages": total_pages,
	}

	return items, meta



def formatDatetime(dt, fmt="%d/%m/%Y"):
	"""
	Format a datetime or date object into a string.

	Args:
		dt (datetime or date): The date or datetime object to format.
		fmt (str): Format type: "iso" (default) or a custom strftime pattern.

	Returns:
		str: Formatted date string.
	"""
	if dt is None:
		return None

	if fmt == "iso":
		return dt.isoformat()
	else:
		return dt.strftime(fmt)


def emailSender(emailAddress, emailSubject, emailBody):

	"""
	Sends an HTML email using Gmail SMTP.

	Parameters:
		emailAddress (str): Recipient's email address
		emailSubject (str): Subject line of the email
		emailBody (str): HTML content of the email

	Returns:
		bool: True if email sent successfully, False otherwise
	"""

	try:
		senderEmail = current_app.config['APP_EMAIL_ADDRESS']
		senderEmailPwd = current_app.config['APP_EMAIL_ADDRESS_PASSWORD']


		msg = MIMEMultipart()
		msg['From'] = senderEmail
		msg['To'] = emailAddress
		msg['Subject'] = emailSubject

		msg.attach(MIMEText(emailBody, 'html'))

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(senderEmail, senderEmailPwd)
		text = msg.as_string()
		server.sendmail(senderEmail, emailAddress, text)
		server.quit()

		current_app.logger.error("returning from emailSender")
		return True

	except smtplib.SMTPDataError as e:
		current_app.logger.error("SMTPDataError: %s", str(e))
		return False

	except Exception as e:
		current_app.logger.error(f"Error while sending email inside emailSender Definition inside util.py: {str(e)}")
		return False



def sendEmailFromTemplate(templatePath, subject, userData):
	"""
	Reads an HTML email template, replaces placeholders with user-specific data,
	and sends a welcome email.

	Args:
		template_path (str): Path to the HTML template file.
		subject (str): Subject line for the email.
		user_data (dict): Dictionary containing the following keys:
			- 'first_name': Recipient's first name
			- 'email_address': Recipient's email address
			- 'password_url': URL for setting the password

	Returns:
		bool: True if the email was sent successfully, False otherwise.
	"""
	try:
		with open(templatePath, "r", encoding="utf-8") as file:

			html_template = file.read()

		# Replace placeholders with actual user data
		htmlContent = (
			html_template
			.replace("[LOGIN_URL]", current_app.config['LOGIN_URL'])
			.replace("[RESET_URL]", current_app.config['RESET_URL'])
			.replace("[EMAIL]", userData.get('email', ''))
			.replace("[NAME]", userData.get('name', ''))
			.replace("[TEMP_PASSWORD]", userData.get('TEMP_PASSWORD', ''))
			.replace("[HR_EMAIL]", current_app.config['HR_EMAIL'])
			.replace("[HR_PHONE]", current_app.config['HR_PHONE'])
			.replace("[CURRENT_YEAR]", str(datetime.now().year))
		)

		return emailSender(userData.get('email', ''), subject, htmlContent)

	except Exception as e:
		current_app.logger.error(
			"Error while sending welcome email in send_email_from_template: %s", str(e)
		)
		return False




def generatepwd(length: int = 12) -> str:
    chars = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*()_+-="
    )
    return "".join(secrets.choice(chars) for _ in range(length))



def setupLogger(app):
	"""
	Configure logging for production.
	Logs every API request and uncaught exceptions.
	"""
	# Ensure log folder exists
	log_folder = os.path.join(os.getcwd(), 'logs')
	os.makedirs(log_folder, exist_ok=True)
	# log_file = os.path.join(log_folder, 'app.log')
	log_file = os.path.join(log_folder, f"logs_{datetime.now().strftime('%Y_%m_%d')}.log")


	# Remove default handlers
	if app.logger.handlers:
		for handler in app.logger.handlers:
			app.logger.removeHandler(handler)

	# File handler with rotation
	file_handler = RotatingFileHandler(
		log_file, maxBytes=5 * 1024 * 1024, backupCount=5
	)
	file_handler.setLevel(logging.INFO)
	file_formatter = logging.Formatter(
		'[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
	)
	file_handler.setFormatter(file_formatter)

	# Console handler for errors
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.ERROR)
	console_handler.setFormatter(file_formatter)

	# Attach handlers
	app.logger.addHandler(file_handler)
	app.logger.addHandler(console_handler)
	app.logger.setLevel(logging.INFO)

	app.logger.info("Production logger initialized successfully")

	# -------------------------------
	# Log every request
	# -------------------------------
	@app.before_request
	def log_request_info():
		g.start_time = datetime.utcnow()
		app.logger.info(
			f"Request start: {request.method} {request.path} | "
			f"IP: {request.remote_addr} | "
			f"Args: {request.args.to_dict()} | "
			f"JSON: {request.get_json(silent=True)}"
		)

	@app.after_request
	def log_response_info(response):
		duration = (datetime.utcnow() - g.start_time).total_seconds()
		log_msg = (
			f"Request end: {request.method} {request.path} | "
			f"Status: {response.status_code} | Duration: {duration:.3f}s"
		)

		# Include response data for errors
		if response.status_code >= 400:
			log_msg += f" | Response: {json.loads(response.get_data(as_text=True))}"

		app.logger.info(log_msg)
		return response


	# -------------------------------
	# Global exception logging
	# -------------------------------
	@app.errorhandler(Exception)
	def handle_exception(e):
		app.logger.exception(f"Unhandled Exception: {str(e)}")
		return {"status": "error", "message": "Internal Server Error"}, 500


def setupLambdaLogger(app):
	"""
	Logger setup for Flask app running in AWS Lambda.
	Logs every API request and exceptions to CloudWatch (stdout).
	"""

	# Remove default handlers
	if app.logger.handlers:
		for handler in app.logger.handlers:
			app.logger.removeHandler(handler)

	# Stream handler (stdout) — Lambda automatically sends this to CloudWatch
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	formatter = logging.Formatter(
		'[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
	)
	console_handler.setFormatter(formatter)

	app.logger.addHandler(console_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info("Lambda logger initialized successfully")

	# -------------------------------
	# Log every request
	# -------------------------------
	@app.before_request
	def log_request_info():
		g.start_time = datetime.utcnow()
		app.logger.info(
			f"Request start: {request.method} {request.path} | "
			f"IP: {request.remote_addr} | "
			f"Args: {request.args.to_dict()} | "
			f"JSON: {request.get_json(silent=True)}"
		)

	@app.after_request
	def log_response_info(response):
		duration = (datetime.utcnow() - g.start_time).total_seconds()
		log_msg = (
			f"Request end: {request.method} {request.path} | "
			f"Status: {response.status_code} | Duration: {duration:.3f}s"
		)

		# Include response body for errors
		if response.status_code >= 400:
			log_msg += f" | Response: {json.loads(response.get_data(as_text=True))}"

		app.logger.info(log_msg)
		return response

	# -------------------------------
	# Global exception logging
	# -------------------------------
	@app.errorhandler(Exception)
	def handle_exception(e):
		app.logger.exception(f"Unhandled Exception: {str(e)}")
		return {"status": "error", "message": "Internal Server Error"}, 500
