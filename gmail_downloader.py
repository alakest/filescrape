# This is the beginning of the gmail_downloader.py file.
# I will add the necessary code in the following steps.
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
        return None


def get_labels(service):
    """
    Gets all the labels from the user's Gmail account.
    """
    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        return labels
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_messages_by_labels(service, label_ids):
    """
    Gets all the messages from the user's Gmail account that have all the specified labels.
    """
    try:
        query = " ".join([f"label:{label_id}" for label_id in label_ids])
        response = service.users().messages().list(userId="me", q=query).execute()
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])
        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId="me", q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])
        return messages
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_message_content(service, message_id):
    """
    Gets the full content of a message.
    """
    try:
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        return message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def main():
    """
    Main function to download emails with specific labels.
    """
    service = authenticate_gmail()
    if not service:
        return

    all_labels = get_labels(service)
    if not all_labels:
        print("Could not retrieve labels.")
        return

    label_map = {label["name"]: label["id"] for label in all_labels}

    print("Available labels:")
    for label_name in label_map.keys():
        print(f"- {label_name}")

    while True:
        label_names_input = input(
            "Enter the names of the labels to filter by, separated by commas: "
        )
        label_names = [name.strip() for name in label_names_input.split(",")]

        selected_label_ids = [label_map.get(name) for name in label_names]

        if all(selected_label_ids):
            break
        else:
            print("One or more label names are invalid. Please try again.")


    print("Getting messages...")
    messages = get_messages_by_labels(service, selected_label_ids)

    if not messages:
        print("No messages found with the specified labels.")
        return

    print(f"Found {len(messages)} messages. Fetching content...")

    all_emails = []
    for message in messages:
        message_content = get_message_content(service, message["id"])
        if message_content:
            all_emails.append(message_content)

    with open("emails.json", "w") as f:
        json.dump(all_emails, f, indent=4)

    print("Emails have been downloaded and saved to emails.json")


if __name__ == "__main__":
    main()
