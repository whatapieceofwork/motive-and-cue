# from flask import current_app, render_template
# from flask_mail import Message
# from threading import Thread

# def send_async_email(current_app, msg):
#     from app import mail
#     print("Async mail called")
#     with current_app._get_current_object():
#         mail.send(msg)

# def send_email(to, subject, template, **kwargs):
#     print("Send mail called")
#     msg = Message(current_app.config["MAIL_SUBJECT_PREFIX"] + subject, 
#                 sender=current_app.config["MAIL_SENDER"], recipients=[to])
#     msg.body = render_template(template + ".txt", **kwargs)
#     msg.html = render_template(template + ".html", **kwargs)
#     with current_app._get_current_object():
#         thr = Thread(target=send_async_email, args=[current_app, msg])
#         thr.start()
#     return thr
