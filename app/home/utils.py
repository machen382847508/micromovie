from app import db
from flask import session,request
from app.models import Userlog

class Utils:
    def InsertUserlog(self):
        userlog = Userlog(
            user_id = session["user_id"],
            ip = request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()