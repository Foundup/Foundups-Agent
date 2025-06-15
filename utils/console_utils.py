def sanitize_for_console(text):
    """
    Encodes a string to ASCII, replacing any non-compliant characters.
    This ensures compatibility with non-UTF-8 console environments like cp932.
    """
    return str(text).encode('ascii', 'replace').decode('ascii') 