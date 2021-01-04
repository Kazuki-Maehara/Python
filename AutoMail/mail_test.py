MAIL_SERVER= "MAIL_SERVER_ADDRESS"
PORT_NUMBER = int("PORT_NUMBER_FOR_MAIL_SERVER")
MY_ACCOUNT = "YOUR_ACCOUNT_ID"
MY_PASSWORD = "YOUR_PASSWORD" 
SUCCESS_MESSAGE = "A mail is sent correctly"
ACCEPT_MESSAGE = "Press ENTER: Send a message, Press Ctrl+C: Stop sending a message"


# create a class for colorized strings
class Color:
    GREEN = '\033[32m'
    RESET = '\033[0m'

# import modules for connection  
import smtplib


def main():

    # SMTP server - Gmail
    smtp_server = MAIL_SERVER
    port_number = PORT_NUMBER

    # log-in information
    account = MY_ACCOUNT
    password = MY_PASSWORD

    # specify a SMTP server
    server = smtplib.SMTP(smtp_server, port_number)

    # check a SMTP server response
    res_server = server.noop()
    print(res_server)

    # start a encrypted connection
    res_starttls = server.starttls()
    print(res_starttls)


    # lon in
    res_login = server.login(account, password)
    print(res_login)


    # get json data of dictionary
    json_dict = jsonGet()


    for sub_dict in json_dict.values():
        to_address = sub_dict["address"]
        subject = sub_dict["subject"]
        representative = sub_dict["representative"]
        name = sub_dict["name"]
        repr_dept = sub_dict["repr_dept"]
        
        # prepare a mail
        msg, body_text = prepareMail(to_address = to_address, subject = subject,
                representative = representative, name = name, repr_dept = repr_dept)
        
        # print a message before sending an e-mail
        print(ACCEPT_MESSAGE, end = "")
        input()
        
        print("TO: {address}".format(address = to_address))
        print("SUBJECT: {subject}".format(subject = subject))
        print(body_text)

        #send a mail
        server.send_message(msg)
        print(f"\n{Color.GREEN}{SUCCESS_MESSAGE}{Color.RESET}\n\n")

    # close a connection with SMTP server
    server.quit

    print("Process Completed!")


# import modules for sending a mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def prepareMail(to_address, subject, representative, name, repr_dept):
    # prepare a message
    msg = MIMEMultipart()

    # set subject and mail-address
    msg["Subject"] = subject
    from_email_address = MY_ACCOUNT
    msg["From"] = from_email_address
    msg["To"] = to_address

    fp = open("mail_body.txt", mode = "r", encoding = "utf-8")
    body_temp = fp.read()
    fp.close()

    body_text = body_temp.format(
            company = name,
            department = repr_dept,
            person = representative
            )

    body = MIMEText(body_text)
    msg.attach(body)
    
    return msg, body_text


# import a module for json data
import json

def jsonGet():
    with  open("./database.json", mode = "r", encoding = "utf-8") as fp:
        json_dict = json.load(fp)

    return json_dict





if __name__ == "__main__":
    main()
