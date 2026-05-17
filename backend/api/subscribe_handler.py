from storage.abstract_storage import AbstractStorageClient

try:
    from email_validator import EmailNotValidError, validate_email
except ImportError:  # fallback for type checking
    validate_email = None  # type: ignore[assignment]
    EmailNotValidError = Exception  # type: ignore[misc,assignment]


def handle_subscribe(
    body: dict,  # type: ignore[type-arg]
    storage: AbstractStorageClient,
) -> tuple[int, dict]:  # type: ignore[type-arg]
    email = body.get("email")
    if not email:
        return 400, {"error": "missing email"}

    try:
        if validate_email is not None:
            validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return 400, {"error": "invalid email"}

    added = storage.add_subscriber(email)
    if added:
        return 201, {"message": "subscribed"}
    return 200, {"message": "already subscribed"}


def handle_unsubscribe(
    email: str,
    storage: AbstractStorageClient,
) -> tuple[int, dict]:  # type: ignore[type-arg]
    removed = storage.remove_subscriber(email)
    if removed:
        return 200, {"message": "unsubscribed"}
    return 200, {"message": "not found"}
