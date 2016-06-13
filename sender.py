from validate_email import validate_email
import requests
import argparse
import os

GRP_SIZE = 100
RECHECK = 2

parser = argparse.ArgumentParser(
    description='Send emails with mailgun api')
parser.add_argument('key', help='the mailgun key')
parser.add_argument('domain', help='the mailgun domain name')
parser.add_argument('mlist', help='the email list file')
args = parser.parse_args()

URL = "https://api.mailgun.net/v3/%s/messages" % args.domain


def filter_mails(maillist):
    invalid_mails = []
    valid_mails = []
    for rec in maillist:
        receiver = rec.strip()
        is_valid = validate_email(receiver, verify=True, smtp_timeout=1)
        if not is_valid:
            invalid_mails.append(receiver)
        else:
            print('%s ok' % receiver)
            valid_mails.append(receiver)

    for i in range(RECHECK):
        # timeout=1s maybe not enough, so filter invalid address again
        print('\nRecheck Round %d:\n' % (i + 1))
        for rec in invalid_mails:
            is_valid = validate_email(rec, verify=True, smtp_timeout=1)
            if is_valid:
                print('%s ok' % rec)
                invalid_mails.remove(rec)
                valid_mails.append(rec)
            else:
                print('%s marked as invalid' % rec)

    print('%d in %d emails are marked as invalid and been discard' %
          (len(valid_mails), len(maillist)))
    return valid_mails


def send_simple_message(URL, sender, receiver, subject, content):
    return requests.post(URL,
                         auth=("api", args.key),
                         data={"from": sender,
                               "to": receiver,
                               "subject": subject,
                               "text": content})

if __name__ == "__main__":
    sender = os.environ['Sender']
    subject = os.environ['MailTitle']
    content = os.environ['MailContent']

    all_receivers = filter_mails(open(args.mlist).read().split())

    rec_grps = [all_receivers[i: i + GRP_SIZE]
                for i in range(0, len(all_receivers), GRP_SIZE)]
    for grp in rec_grps:
        print('send mail to %s' % grp)
        res = send_simple_message(URL, sender, grp, subject, content)
        print(res)
