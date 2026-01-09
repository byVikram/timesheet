
from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.cron_service import sendEmailsToDraftTimesheets
from app.utils.helpers import getErrorMessage, getSuccessMessage


blp = Blueprint(
	"Cron APIs",
	__name__,
	description="Cron-related APIs",
)

@blp.route("/weekly-reminder")
class WeeklyReminder(MethodView):
	@blp.doc(description="Send weekly reminder emails to users with draft timesheets")
	def post(self):
		try:
			print("post request received")

			timesheet, error = sendEmailsToDraftTimesheets()

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Emails sent successfully.",
				"",
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500