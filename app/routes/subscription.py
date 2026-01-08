
from flask.views import MethodView
from flask_smorest import Blueprint
from app.constants.lookups import ROLES
from app.models.users import User, UserRole
from app.schemas.subscription_schema import SubscriptionSchema
from app.utils.helpers import authorize, getErrorMessage, getSuccessMessage, tokenValidation

from app.models import PushSubscription, db  # your SQLAlchemy model

from pywebpush import webpush, WebPushException
import json

blp = Blueprint(
	"Subscription APIs",
	__name__,
	description="Subscription-related APIs",
)

subscriptions = []

VAPID_PRIVATE_KEY = "CemhvOeliK4mq2oc4RGLMkA_CrvLVWy4NPDG7yYprBc"
VAPID_PUBLIC_KEY = "BFCt4i-AaR8Ieks9qFjimVbOMHZdQRN0DnHaccdbf4NTfREUGPBYF8WNDhu1M_KuRmCIGzB_uwZTuO6PykdkAkI"



blp = Blueprint(
	"Subscription APIs",
	__name__,
	description="Subscription-related APIs",
)

@blp.route("/subscribe")
class SubscribeAPI(MethodView):
	@blp.arguments(SubscriptionSchema)
	@tokenValidation
	@authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
	def post(self, args):
		try:
			if not args:
				return getErrorMessage("No subscription data"), 400

			# Extract subscription data from request
			subscription_data = args.get("subscription")
			
			print(subscription_data,"subscription_data")
			endpoint = subscription_data.get("endpoint")
			print(endpoint,"endpoint")
			keys = subscription_data.get("keys")
			print(keys,"keys")

			# Get current user ID from tokenValidation (assume g.user.id)
			user_id = self.userId

			# Check if subscription already exists for this endpoint
			existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
			if existing:
				return getSuccessMessage("Subscription already exists", ""), 200
			
			print("Need to add subscription")

			# Save subscription in DB
			new_sub = PushSubscription(
				user_id=user_id,
				endpoint=endpoint,
				keys=keys
			)
			db.session.add(new_sub)
			db.session.commit()

			return getSuccessMessage("Subscription saved successfully", ""), 201

		except Exception as e:
			db.session.rollback()
			return getErrorMessage(str(e)), 500
		

@blp.route("/my-subscription")
class MySubscriptionAPI(MethodView):
	@tokenValidation  # ensures user is logged in
	@authorize(["ALL"])
	def post(self):
		try:
			user_id = self.userId  # assume your tokenValidation sets g.user

			# Get the user's subscription(s) from DB
			subscriptions = PushSubscription.query.filter_by(user_id=user_id).all()

			# Return as list of dicts
			subs_data = [
				{
					"endpoint": sub.endpoint,
					"keys": sub.keys,
					"expirationTime": None  # optional, if you track it
				}
				for sub in subscriptions
			]

			return getSuccessMessage("User subscriptions fetched", subs_data), 200

		except Exception as e:
			return {"status": "error", "message": str(e), "data": ""}, 500


def send_push(subscription_info, title="Hello!", body="Test notification"):
	try:
		webpush(
			subscription_info=subscription_info,
			data=json.dumps({"title": title, "body": body}),
			vapid_private_key=VAPID_PRIVATE_KEY,
			vapid_claims={
				"sub": "mailto:you@example.com"
			}
		)
		return True
	except WebPushException as ex:
		print("Push failed:", ex)
		# Handle expired subscription
		if ex.response and ex.response.status_code == 410:  # subscription gone
			endpoint = subscription_info.get("endpoint")
			PushSubscription.query.filter_by(endpoint=endpoint).delete()
			db.session.commit()
		return False


@blp.route("/send-push")
class SendPush(MethodView):
	def post(self):
		"""
		Send push notification to all users (or can filter by role/condition)
		Example JSON body: {"title": "Hello", "body": "This is a test notification"}
		"""
		try:
			# data = json.loads(request.data or "{}")
			# title = data.get("title", "Hello!")
			# body = data.get("body", "Test notification")

			# Get all subscriptions
			# subscriptions = PushSubscription.query.all()

			# Example: only managers
			subscriptions = (
				PushSubscription.query
				.join(PushSubscription.user)          # join User
				.join(User.role)                      # join UserRole
				.filter(UserRole.name == "Super Admin")
				.all()
			)


			# Send push to each subscription
			for sub in subscriptions:
				send_push(
					subscription_info={
						"endpoint": sub.endpoint,
						"keys": sub.keys
					},
					title="Timesheet Reminder",
					body="Have you updated your timesheet"
				)

			return getSuccessMessage("Push notifications sent", "Have you updated your timesheet"), 200

		except Exception as e:
			return {"status": "error", "message": str(e), "data": ""}, 500