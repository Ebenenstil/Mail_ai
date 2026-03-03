from app import mail_fetcher
from app import config


def main():
    mails = mail_fetcher.fetch_todays_emails(config)
    mail_fetcher.save_to_json(mails)

    print(f"{len(mails)} Emails von heute gespeichert.")


if __name__ == "__main__":
    main()