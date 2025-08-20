import os.path
import json
import base64
import csv
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():
    """Authenticates with the Gmail API."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_labels(service):
    """Gets all labels from the user's account."""
    try:
        results = service.users().labels().list(userId="me").execute()
        return results.get("labels", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_messages_by_labels(service, label_names):
    """Gets messages that have all the specified labels, searching by name."""
    try:
        # Quote each label name to handle spaces and special characters.
        query = " ".join([f'label:"{name}"' for name in label_names])
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
    """Gets the full content of a message."""
    try:
        return (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_email_body(message_payload):
    """
    Recursively search for the 'text/plain' part of an email message
    and return the decoded body.
    """
    if 'parts' in message_payload:
        for part in message_payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            # Recurse into multipart parts
            if 'parts' in part:
                body = get_email_body(part)
                if body:
                    return body
    # Handle non-multipart messages
    elif 'body' in message_payload and 'data' in message_payload['body']:
        if message_payload['mimeType'] == 'text/plain':
            return base64.urlsafe_b64decode(message_payload['body']['data']).decode('utf-8')
    return ""


def get_attachment_filenames(message_payload):
    """
    Recursively search for parts with filenames and return a list of them.
    """
    filenames = []
    if 'parts' in message_payload:
        for part in message_payload['parts']:
            if part.get('filename'):
                filenames.append(part['filename'])
            # Recurse into multipart parts
            if 'parts' in part:
                filenames.extend(get_attachment_filenames(part))
    return filenames


def main():
    """Main function to download emails with specific labels."""
    service = authenticate_gmail()
    if not service:
        return

    all_labels = get_labels(service)
    if not all_labels:
        print("Could not retrieve labels.")
        return

    label_map = {label["name"]: label["id"] for label in all_labels}
    id_to_label_map = {v: k for k, v in label_map.items()}

    label_names = []
    if os.path.exists("labels.csv"):
        print("Found labels.csv, using labels from file.")
        with open("labels.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    label_names.append(row[0].strip())

        invalid_labels = [name for name in label_names if name not in label_map]
        if invalid_labels:
            print(f"Error: The following labels from labels.csv are invalid: {', '.join(invalid_labels)}")
            print("Please correct the file or remove it to select labels manually.")
            return

    else:
        print("labels.csv not found. Please select labels from the list below.")
        print("Available labels:")
        # Sort the labels alphabetically for easier reading
        for label_name in sorted(label_map.keys()):
            print(f"- {label_name}")

        while True:
            label_names_input = input(
                "Enter the names of the labels to filter by, separated by commas: "
            )
            label_names = [name.strip() for name in label_names_input.split(",")]

            # Validate that the entered labels exist.
            if all(name in label_map for name in label_names):
                break
            else:
                print("One or more label names are invalid. Please try again.")

    print("Getting messages...")
    messages = get_messages_by_labels(service, label_names)

    if not messages:
        print("No messages found with the specified labels.")
        return

    print(f"Found {len(messages)} message(s). Fetching content...")

    all_emails = []
    total_messages = len(messages)
    for i, message_info in enumerate(messages):
        print(f"Downloading email {i + 1} of {total_messages}...")
        message_content = get_message_content(service, message_info["id"])
        if message_content:
            # Extract headers
            headers = message_content.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

            # Decode the body
            body = get_email_body(message_content.get('payload', {}))

            # Get labels
            labels = [id_to_label_map.get(label_id, label_id) for label_id in message_content.get('labelIds', [])]

            # Get attachments
            attachments = get_attachment_filenames(message_content.get('payload', {}))

            email_data = {
                'id': message_content['id'],
                'threadId': message_content['threadId'],
                'sender': sender,
                'recipient': recipient,
                'date': date,
                'subject': subject,
                'labels': labels,
                'body': body,
                'attachments': attachments,
            }
            all_emails.append(email_data)

    num_emails = len(all_emails)
    if num_emails > 0:
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
        filename = f"email_{timestamp}_{num_emails}.json"
        with open(filename, "w") as f:
            json.dump(all_emails, f, indent=4)
        print(f"Success! Downloaded {num_emails} email(s) and saved to {filename}.")
    else:
        # This case is already handled by the `if not messages:` check,
        # but as a safeguard, we can add this.
        pass


if __name__ == "__main__":
    main()
