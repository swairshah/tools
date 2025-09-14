#!/usr/bin/env python3
"""
command-line tool to download and convert Gmail emails to markdown
"""

import os
import json
import base64
import re
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from convert import convert

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def setup_gmail_api():
    """Set up Gmail API authentication"""
    creds = None

    # Check for existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You'll need to create credentials.json from Google Cloud Console
            # Enable Gmail API and download OAuth 2.0 credentials
            if not os.path.exists('credentials.json'):
                print("ERROR: credentials.json not found!")
                print("Please:")
                print("1. Go to Google Cloud Console")
                print("2. Enable Gmail API")
                print("3. Create OAuth 2.0 credentials")
                print("4. Download as credentials.json")
                return None

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def build_gmail_query(args):
    """Build Gmail query string from command line arguments"""
    query_parts = []

    # Sender filter
    if args.sender:
        if '*' in args.sender or '?' in args.sender:
            # Pattern matching - Gmail doesn't support wildcards directly
            # So we'll use the pattern without wildcards
            sender_clean = args.sender.replace('*', '').replace('?', '')
            query_parts.append(f'from:{sender_clean}')
        else:
            query_parts.append(f'from:{args.sender}')

    # Subject filter
    if args.subject:
        if '"' in args.subject:
            query_parts.append(f'subject:{args.subject}')
        else:
            query_parts.append(f'subject:"{args.subject}"')

    # Date range filters
    if args.after:
        query_parts.append(f'after:{args.after}')

    if args.before:
        query_parts.append(f'before:{args.before}')

    # Additional query
    if args.query:
        query_parts.append(args.query)

    query = ' '.join(query_parts)
    print(f"Gmail query: {query}")
    return query

def get_message_ids(service, args):
    """Get email message IDs based on search criteria"""
    query = build_gmail_query(args)

    if not query:
        print("Warning: No search criteria specified. This will fetch ALL emails!")
        if not args.force:
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                return []

    print("Fetching email IDs...")

    message_ids = []
    next_page_token = None

    while True:
        try:
            params = {
                'userId': 'me',
                'maxResults': args.max_results if args.max_results else 500
            }

            if query:
                params['q'] = query

            if next_page_token:
                params['pageToken'] = next_page_token

            results = service.users().messages().list(**params).execute()

            messages = results.get('messages', [])
            message_ids.extend([msg['id'] for msg in messages])

            if args.max_results and len(message_ids) >= args.max_results:
                message_ids = message_ids[:args.max_results]
                break

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

            print(f"Found {len(message_ids)} emails so far...")

        except Exception as e:
            print(f"Error fetching message IDs: {e}")
            break

    print(f"Total emails found: {len(message_ids)}")
    return message_ids

def process_email_for_storage(message):
    """Process email message and decode Base64 content"""
    processed = {
        'id': message.get('id', ''),
        'threadId': message.get('threadId', ''),
        'labelIds': message.get('labelIds', []),
        'snippet': message.get('snippet', ''),
        'headers': {},
        'body': {
            'text': '',
            'html': ''
        }
    }

    # Extract headers
    if 'payload' in message and 'headers' in message['payload']:
        for header in message['payload']['headers']:
            processed['headers'][header['name']] = header['value']

    # Extract and decode body content
    if 'payload' in message:
        text_content = extract_content_from_payload(message['payload'], 'text/plain')
        html_content = extract_content_from_payload(message['payload'], 'text/html')

        processed['body']['text'] = text_content
        processed['body']['html'] = html_content

    return processed

def download_email_batch(service, message_ids, output_dir, batch_size=50, dry_run=False):
    """Download emails in batches and save as JSON with decoded content"""
    if dry_run:
        print(f"\n[DRY RUN] Would download {len(message_ids)} emails")
        # Show first few email subjects as preview
        preview_count = min(5, len(message_ids))
        print(f"\nPreviewing first {preview_count} emails:")
        for i, msg_id in enumerate(message_ids[:preview_count]):
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                print(f"  {i+1}. {headers.get('Subject', 'No Subject')}")
                print(f"     From: {headers.get('From', 'Unknown')}")
                print(f"     Date: {headers.get('Date', 'Unknown')}")
            except Exception as e:
                print(f"  Error fetching preview for {msg_id}: {e}")

        if len(message_ids) > preview_count:
            print(f"\n  ... and {len(message_ids) - preview_count} more emails")
        return

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_emails_dir = output_dir / "raw_emails"
    raw_emails_dir.mkdir(exist_ok=True)

    print(f"Downloading {len(message_ids)} emails in batches of {batch_size}...")

    for i in range(0, len(message_ids), batch_size):
        batch = message_ids[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(message_ids)-1)//batch_size + 1}")

        for j, msg_id in enumerate(batch):
            try:
                # Check if already downloaded
                email_file = raw_emails_dir / f"{msg_id}.json"
                if email_file.exists():
                    print(f"  Skipping {msg_id} (already downloaded)")
                    continue

                # Download email
                message = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                # Process and decode content
                processed_message = process_email_for_storage(message)

                # Save processed JSON with decoded content
                with open(email_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_message, f, indent=2, ensure_ascii=False)

                print(f"  Downloaded {j+1}/{len(batch)}: {msg_id}")

            except Exception as e:
                print(f"  Error downloading {msg_id}: {e}")
                continue

def extract_email_content(message_data):
    """Extract readable content from Gmail message"""
    # Get headers
    headers = {}
    if 'payload' in message_data and 'headers' in message_data['payload']:
        for header in message_data['payload']['headers']:
            headers[header['name']] = header['value']

    subject = headers.get('Subject', 'No Subject')
    date_str = headers.get('Date', '')
    sender = headers.get('From', 'Unknown')

    # Parse date
    try:
        date_obj = datetime.strptime(date_str.split(' (')[0], '%a, %d %b %Y %H:%M:%S %z')
    except:
        try:
            date_obj = datetime.strptime(date_str.split(',')[1].strip().split(' +')[0], '%d %b %Y %H:%M:%S')
        except:
            date_obj = datetime.now()

    # Extract content
    content = extract_content_from_payload(message_data['payload'])

    return {
        'subject': subject,
        'date': date_obj,
        'sender': sender,
        'content': content,
        'message_id': message_data.get('id', '')
    }

def extract_content_from_payload(payload, mime_type_filter=None):
    """Recursively extract and decode content from email payload"""
    content = ""

    if 'parts' in payload:
        for part in payload['parts']:
            if mime_type_filter and part['mimeType'] == mime_type_filter:
                if 'data' in part['body']:
                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif not mime_type_filter:
                if part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/plain':
                    if 'data' in part['body'] and not content:
                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

            if 'parts' in part:
                content = extract_content_from_payload(part, mime_type_filter)
                if content:
                    break
    elif payload['mimeType'] in ['text/html', 'text/plain']:
        if not mime_type_filter or payload['mimeType'] == mime_type_filter:
            if 'data' in payload['body']:
                content = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    return content

def convert_emails_to_markdown(raw_emails_dir, output_dir):

    """Convert downloaded JSON emails to markdown"""
    raw_emails_dir = Path(raw_emails_dir)
    output_dir = Path(output_dir)

    print("Converting emails to markdown...")

    json_files = list(raw_emails_dir.glob("*.json"))
    print(f"Found {len(json_files)} email files to convert")

    successful = 0
    failed = 0

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                message_data = json.load(f)

            content = message_data['body'].get('text',None)

            try:
                essay = convert(content)

                # Create markdown filename using essay date
                date_str = essay.Date.strftime('%-d %b %y')
                clean_title = re.sub(r'[<>:"/\\|?*/?]', '', essay.PostTitle)
                clean_title = re.sub(r'\s+', ' ', clean_title).strip()[:150]
                md_filename = f"{date_str} {clean_title}.md"
                md_file = output_dir / md_filename

                # Skip if exists
                if md_file.exists():
                    continue

                # Write the markdown directly
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(essay.Content)

            except Exception as convert_error:
                print(f"  Skipping {json_file.name} (conversion failed): {convert_error}")
                continue

            print(f"  ✓ Converted: {md_filename}")
            successful += 1

        except Exception as e:
            print(f"  ✗ Error converting {json_file.name}: {e}")
            failed += 1

    print(f"\nConversion complete! Success: {successful}, Failed: {failed}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Download and convert Gmail emails to markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True

    # Download command
    download_parser = subparsers.add_parser(
        'download',
        help='Download emails from Gmail',
        epilog='''
Examples:
  # Download Money Stuff emails from Bloomberg
  %(prog)s --sender "noreply@news.bloomberg.com" --subject "Money Stuff"

  # Download emails from last 30 days
  %(prog)s --days 30 --sender "john@example.com"

  # Download emails within date range
  %(prog)s --after 2024/1/1 --before 2024/12/31

  # Preview what would be downloaded (dry run)
  %(prog)s --subject "Newsletter" --dry-run

  # Custom Gmail query
  %(prog)s --query "has:attachment larger:5M"
        '''
    )

    # Search filters for download
    download_parser.add_argument('--sender', '-s',
                        help='Email sender (supports wildcards: *@domain.com)')
    download_parser.add_argument('--subject', '-j',
                        help='Subject line (partial match supported)')
    download_parser.add_argument('--after', '-a',
                        help='Emails after this date (YYYY/MM/DD or YYYY-MM-DD)')
    download_parser.add_argument('--before', '-b',
                        help='Emails before this date (YYYY/MM/DD or YYYY-MM-DD)')
    download_parser.add_argument('--days', '-d', type=int,
                        help='Emails from last N days')
    download_parser.add_argument('--query', '-q',
                        help='Custom Gmail query (advanced users)')

    # Output options for download
    download_parser.add_argument('--output', '-o',
                        default='~/Documents/gmail_exports',
                        help='Output directory (default: ~/Documents/gmail_exports)')

    # Processing options for download
    download_parser.add_argument('--max-results', '-m', type=int,
                        help='Maximum number of emails to download')
    download_parser.add_argument('--batch-size', type=int, default=50,
                        help='Batch size for downloading (default: 50)')
    download_parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Preview what would be downloaded without actually downloading')
    download_parser.add_argument('--force', '-f', action='store_true',
                        help='Skip confirmation prompts')

    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert downloaded emails to markdown',
        epilog='''
Examples:
  # Convert all emails in default directory
  %(prog)s

  # Convert emails from specific directory
  %(prog)s --input ~/Downloads/emails/raw_emails --output ~/Documents/markdown_emails
        '''
    )

    # Input/output options for convert
    convert_parser.add_argument('--input', '-i',
                        default='~/Documents/gmail_exports/raw_emails',
                        help='Input directory with raw JSON emails (default: ~/Documents/gmail_exports/raw_emails)')
    convert_parser.add_argument('--output', '-o',
                        default='~/Documents/gmail_exports',
                        help='Output directory for markdown files (default: ~/Documents/gmail_exports)')

    args = parser.parse_args()

    # Process date arguments for download command
    if args.command == 'download' and hasattr(args, 'days') and args.days:
        # Override after date with days calculation
        date = (datetime.now() - timedelta(days=args.days)).strftime('%Y/%m/%d')
        args.after = date

    # Normalize date formats for download command
    if args.command == 'download':
        if hasattr(args, 'after') and args.after:
            args.after = args.after.replace('-', '/')
        if hasattr(args, 'before') and args.before:
            args.before = args.before.replace('-', '/')

    return args

def main():
    args = parse_arguments()

    if args.command == 'download':
        print("Gmail Email Downloader")
        print("=" * 50)

        # Expand output directory
        output_dir = os.path.expanduser(args.output)

        # Setup Gmail API
        service = setup_gmail_api()
        if not service:
            return

        print("✓ Gmail API authenticated")

        # Get message IDs based on search criteria
        message_ids = get_message_ids(service, args)
        if not message_ids:
            print("No emails found matching criteria!")
            return

        # Download emails as JSON
        download_email_batch(service, message_ids, output_dir,
                            batch_size=args.batch_size,
                            dry_run=args.dry_run)

        if not args.dry_run:
            print(f"\n✓ Downloaded emails to {output_dir}/raw_emails")

    elif args.command == 'convert':
        print("Email to Markdown Converter")
        print("=" * 50)

        # Expand input and output directories
        input_dir = os.path.expanduser(args.input)
        output_dir = os.path.expanduser(args.output)

        # Check if input directory exists
        if not os.path.exists(input_dir):
            print(f"Error: Input directory does not exist: {input_dir}")
            return

        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")

        # Convert emails to markdown
        convert_emails_to_markdown(input_dir, output_dir)

        print(f"\n✓ Converted emails saved to {output_dir}")

if __name__ == "__main__":
    main()
