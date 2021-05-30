import datetime
from dateutil.relativedelta import relativedelta
import sys
from pathlib import Path
import json
import math
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


TODAY = datetime.date.today()  # For debug: datetime.date(2021, 5, 23)
DAY_TO_MAIL = TODAY.replace(day=27)
BASE_DIRECTORY_PATH = r"PATH TO A BASE DIRECTORY"
MAIL_SUBJECT = "TITLE TEXT"
FROM_ADDRESS = "FROM E-MAIL ADDRESS"
TO_ADDRESS = ["TO E-MAIL ADDRESS"]
CC_ADDRESS = ["CC E-MAIL ADDRESS"]

SMTP_SERVER = "SMTP SERVER ADDRESS"
PORT_No = 9999  # PORT NUMBER

GLOB_THIS_M = str(TODAY.year) + "." + \
    format(str(TODAY.month), '0>2') + "*.xls"
GLOB_PREV_M = str((TODAY - relativedelta(months=1)).year) + "." + \
    format(str((TODAY - relativedelta(months=1)).month), '0>2') + "*.xls"
STRFTIME_EXPRESSION = TODAY.strftime("%Y/%m/%d ")
JSON_FILE = "./src/database.json"
MESSAGE_FILE = "./src/messageBody.txt"


class NoFileException(Exception):
    pass


def getDayToMail(dayToMail):

    oneDay = datetime.timedelta(days=1)

    for i in range(3):
        dayOfWeek = dayToMail.strftime('%A')

        if(dayOfWeek == 'Sunday' or dayOfWeek == 'Saturday'):
            # print(dayOfWeek + ", " + dayToMail.strftime("%D")
            #                 + " ... No need to mail.")
            dayToMail = dayToMail - oneDay
        else:
            # print(dayOfWeek + ", " + dayToMail.strftime("%D")
            #                 + " ... Day to mail.")
            return dayToMail


def findFilename(globExpression):
    p = Path(BASE_DIRECTORY_PATH)

    filePath_list = list(p.glob(globExpression))
    filename_list = [filename.name for filename in filePath_list]

    try:
        if(len(filename_list) < 1):
            raise NoFileException(
                "Error: There is no file meeting glob-expression."
                )
        else:
            return filename_list
    except NoFileException as nofile:
        print(nofile)
        sys.exit(0)


def getPrediction(filenames):

    fp = open(JSON_FILE, mode="r", encoding="utf-8")
    data_dict = json.load(fp)
    fp.close()

    totalCount = 0
    for year in data_dict:
        for month in data_dict[year]:
            totalCount += len(data_dict[year][month])
    # print(totalCount)

    for year in data_dict:
        temp_list = sorted(data_dict[year].items())
        data_dict[year].clear()
        data_dict[year].update(temp_list)
    temp_list = sorted(data_dict.items())
    data_dict.clear()
    data_dict.update(temp_list)

    firstYear = min(data_dict)
    firstMonth = min(data_dict[firstYear])
    nextFirstDay = (TODAY + relativedelta(months=1)).replace(day=1)

    lastDate = nextFirstDay \
        - datetime.timedelta(days=1)

    timeSpan = lastDate \
        - datetime.date(year=int(firstYear), month=int(firstMonth), day=1)

    interval = nextFirstDay - TODAY

    rateParameter = totalCount / timeSpan.days
    cumulative = 1 - math.exp(- rateParameter * interval.days)

    # print(interval.days)
    # print(rateParameter)
    # print(cumulative)

    filenames = findFilename(GLOB_PREV_M)
    print("File-list in PREVIOUS month: ", filenames, end="\n\n")

    oneMonthBefore = TODAY - relativedelta(months=1)
    if str(oneMonthBefore.year) not in data_dict:
        data_dict[str(oneMonthBefore.year)] = {}
        data_dict[str(oneMonthBefore.year)][format(str(oneMonthBefore.month), '0>2')] = \
            filenames
    else:
        data_dict[str(oneMonthBefore.year)][format(str(oneMonthBefore.month), '0>2')] = \
            filenames

    fp = open(JSON_FILE, "w", encoding="utf-8")
    json.dump(data_dict, fp, ensure_ascii=False, indent=4)
    # print(json.dumps(data_dict, indent=4))

    randomNumber = random.random()
    # print(randomNumber)

    if randomNumber <= cumulative:
        return randomNumber, cumulative, 1
    else:
        return randomNumber, cumulative, 0


def sendMail(filenames, prediction, cumulative, randomNumber):

    def createBody():
        nextDayToMail = getDayToMail(DAY_TO_MAIL + relativedelta(months=1))
        bodyText = bodyTemp.format(
            DATE=TODAY.strftime(STRFTIME_EXPRESSION),
            COUNT=len(filenames),
            PREDICTED_COUNT=len(filenames)+prediction,
            FORMAT_DATE=formatdate(localtime=True),
            PYTHON_VERSION=" " + sys.version,
            FILE_NAME_LIST="\n".join(
                [4 * " " + filename for filename in filenames]
                ),
            CUMULATIVE="Cumulative distribution function in exponential distribution:\n    F(x:λ)="
            + str(cumulative),
            NEXT_DAY_TO_MAIL=" " + nextDayToMail.strftime('%A') + ", " + nextDayToMail.strftime("%D"),
            RANDOM_NUMBER=" " + str(randomNumber)
        )
        return bodyText

    def createMessage(bodyText):
        msg = MIMEMultipart()
        msg['Subject'] = MAIL_SUBJECT
        msg['From'] = FROM_ADDRESS
        msg['To'] = ",".join(TO_ADDRESS)
        msg['Cc'] = ",".join(CC_ADDRESS)
        msg['Date'] = formatdate(localtime=True)

        attachmentText = MIMEText(bodyText, 'plain', 'utf-8')
        msg.attach(attachmentText)

        return msg

    fp = open(MESSAGE_FILE, mode="r", encoding="utf-8")
    bodyTemp = fp.read()
    fp.close()

    bodyText = createBody()

    print(bodyText)

    print("Continue to send an email? (y/else):", end="")
    keyToken = input()
    if keyToken != "y":
        print("Stopped sending an email. Bye.")
        sys.exit(0)

    msg = createMessage(bodyText)
    print(msg)
    smtpObj = smtplib.SMTP(SMTP_SERVER, PORT_No)
    smtpObj.ehlo()
    smtpObj.sendmail(FROM_ADDRESS, TO_ADDRESS + CC_ADDRESS, msg.as_string())
    smtpObj.close()


if __name__ == '__main__':

    dayToMail = getDayToMail(DAY_TO_MAIL)
    # print(dayToMail)

    print(dayToMail.strftime('%A') + ", " + dayToMail.strftime("%D")
          + " is a day to mail in this month.")

    # If dayToMail is not today, quit the program
    if(dayToMail != TODAY):
        print(
            "TODAY is " + TODAY.strftime('%A') + ", " + TODAY.strftime("%D")
            + ", so not sending a mail. Exit the program."
            )
        sys.exit(0)

    filenames = findFilename(GLOB_THIS_M)
    print("File-list in THIS month: ", filenames)
    # print(filenames)

    randomNumber, cumulative, prediction = getPrediction(filenames)

    sendMail(filenames, prediction, cumulative, randomNumber)
