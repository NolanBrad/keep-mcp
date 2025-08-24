import gkeepapi
import os
from dotenv import load_dotenv
from gpsoauth import exchange_token

_keep_client = None

def get_client():
    """
    Get or initialize the Google Keep client.
    This ensures we only authenticate once and reuse the client.

    Returns:
        gkeepapi.Keep: Authenticated Keep client
    """
    global _keep_client

    if _keep_client is not None:
        return _keep_client

    # Load environment variables
    load_dotenv()

    # Get credentials from environment variables
    email = os.getenv('GOOGLE_EMAIL')
    master_token = os.getenv('GOOGLE_MASTER_TOKEN')
    auth_token:str | None = os.getenv('GOOGLE_AUTH_TOKEN')

    if not email:
        raise ValueError("Missing Google Keep credentials. Please set GOOGLE_EMAIL environment variable.")

    # Initialize the Keep API
    keep = gkeepapi.Keep()

    # Authenticate
    if auth_token is not None:
        keep.authenticate(email, auth_token, exchange_first=True)
    elif master_token is not None:
        keep.authenticate(email, master_token)
    else:
        raise ValueError("Missing Google Keep credentials. Please set GOOGLE_AUTH_TOKEN or GOOGLE_MASTER_TOKEN environment variables.")

    # Store the client for reuse
    _keep_client = keep

    return keep

def serialize_note(note):
    """
    Serialize a Google Keep note into a dictionary.

    Args:
        note: A Google Keep note object

    Returns:
        dict: A dictionary containing the note's id, title, text, pinned status, color and labels
    """
    return {
        'id': note.id,
        'title': note.title,
        'text': note.text,
        'pinned': note.pinned,
        'color': note.color.value if note.color else None,
        'labels': [{'id': label.id, 'name': label.name} for label in note.labels.all()]
    }

def can_modify_note(note):
    """
    Check if a note can be modified based on label and environment settings.

    Args:
        note: A Google Keep note object

    Returns:
        bool: True if the note can be modified, False otherwise
    """
    unsafe_mode = os.getenv('UNSAFE_MODE', '').lower() == 'true'
    return unsafe_mode or has_keep_mcp_label(note)

def has_keep_mcp_label(note):
    """
    Check if a note has the keep-mcp label.

    Args:
        note: A Google Keep note object

    Returns:
        bool: True if the note has the keep-mcp label, False otherwise
    """
    return any(label.name == 'keep-mcp' for label in note.labels.all())