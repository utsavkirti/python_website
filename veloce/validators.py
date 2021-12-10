from django.core import validators
from django.core.exceptions import ValidationError
from upload_validator import FileTypeValidator
import re

PanValidator = validators.RegexValidator(
    regex='^[A-Z]{3}[PCHABGJLFT][A-Z][0-9]{4}[A-Z]$',
    message='Invalid PAN number.'
)


PhoneValidator = validators.RegexValidator(
    regex='^[0-9]{10}$',
    message='Invalid phone number.'
)


NameValidator = validators.RegexValidator(
    regex='^[A-Za-z]{2,20}$',
    message='Invalid characters in name.'
)


PinCodeValidator = validators.RegexValidator(
    regex='^[0-9]{6}$'
)


AadharValidator = validators.RegexValidator(
    regex='^[0-9]{12}$',
    message='Aadhar No. should have exactly 12 digits.'
)


BankNumberValidator = validators.RegexValidator(
    regex='^[0-9]{9,20}$',
    message='BAN should have exactly 25 digits.'
)


IFSCValidator = validators.RegexValidator(
    regex='^[a-zA-Z0-9]{11}$',
    message='IFSC should be an 11-digit alphanumeric code.'
)


FileValidator = FileTypeValidator(
    allowed_types=['application/pdf', 'image/jpeg', 'image/png'],
)
FileValidator.invalid_message = 'Invalid file type. Valid file types include: pdf, jpeg, png.'
FileValidator.type_message = 'Invalid file type. Valid file types include: pdf, jpeg, png.'
FileValidator.extension_message = 'Valid file types include: pdf, jpeg, png.'


EmailValidatorBase = validators.EmailValidator(
    message='Invalid email.'
)


def EmailValidator(value):
    EmailValidatorBase(value)
    # TODO: Add domain check in the future


def PasswordValidator(value):
    if not len(value) >= 8 or not len(value) <= 50:
        raise ValidationError(
            'Password should be between 8-50 characters long.'
        )
    if not re.search('[A-Z]', value) or not re.search('[a-z]', value) \
            or not re.search('[0-9]', value) or not re.search('[^A-Za-z0-9]', value):
        raise ValidationError(
            'Password should contain at least one numeric, uppercase, lowercase and special letter.'
        )
