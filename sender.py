import requests
import argparse
import os

GRP_SIZE = 100

parser = argparse.ArgumentParser(
    description='Send emails with mailgun api')
parser.add_argument('key', help='the mailgun key')
parser.add_argument('domain', help='the mailgun domain name')
parser.add_argument('mlist', help='the email list file')

args = parser.parse_args()

url = "https://api.mailgun.net/v3/%s/messages" % args.domain

def send_simple_message(url, sender, receiver, subject, content):
    return requests.post(url, auth=("api", args.key),
                 data={"from": sender, "to": receiver, "subject": subject,
                    "text": content}
           )

if __name__ == "__main__":
    sender = os.environ['Sender']
    all_receivers = open(args.mlist).read().split()
    subject = os.environ['MailTitle']
    content = os.environ['MailContent']
    rec_grps = [all_receivers[i: i + GRP_SIZE] for i in range(0,
                                                len(all_receivers), GRP_SIZE)]
    for grp in rec_grps:
        print('send mail to %s' % grp)
        res = send_simple_message(url, sender, grp, subject, content)
        print(res)
