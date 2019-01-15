#写入日志
from app.models import Oplog,Adminlog
from app import db
from flask import session,request

class Utils:

    def InsertOplog(self,adminreason):
        oplog = Oplog(
            admin_id = session["admin_id"],
            ip = request.remote_addr,
            reason = adminreason
        )
        db.session.add(oplog)
        db.session.commit()

    def InsertAdminlog(self):
        adminlog = Adminlog(
            admin_id = session["admin_id"],
            ip = request.remote_addr,
        )
        db.session.add(adminlog)
        db.session.commit()