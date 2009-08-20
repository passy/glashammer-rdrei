# -*- coding: utf-8 -*-
"""
    glashammer.crypto
    ~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Armin Ronacher
    :license: MIT
"""
import hashlib, string
from random import choice

SALT_CHARS = string.ascii_lowercase + string.digits

def gen_pwhash(password, method='sha1'):
    """Return a the password hashed with a random salt."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = gen_salt(6)
    h = hashlib.new(method, '')
    h.update(salt)
    h.update(password)
    return '%s$%s$%s' % (method, salt, h.hexdigest())

def gen_salt(length=6):
    """Generate a random string of SALT_CHARS with specified ``length``."""
    if length <= 0:
        raise ValueError('requested salt of length <= 0')
    return ''.join(choice(SALT_CHARS) for _ in xrange(length))

def check_pwhash(pwhash, password):
    """Check a password against a given hash value. Since
    many forums save md5 passwords with no salt and it's
    technically impossible to convert this to an hash
    with a salt we use this to be able to check for
    plain passwords::

        plain$$default

    md5 passwords without salt::

        md5$$c21f969b5f03d33d43e04f8f136e7682

    md5 passwords with salt::

        md5$123456$7faa731e3365037d264ae6c2e3c7697e

    sha(sha-0) passwords::

        sha$123456$118083bd04c79ab51944a9ef863efcd9c048dd9a

    sha1 passwords::

        sha1$123456$118083bd04c79ab51944a9ef863efcd9c048dd9a

    Note that the integral passwd column in the table is
    only 60 chars long. If you have a very large salt
    or the plaintext password is too long it will be
    truncated.
    """
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    if pwhash.count('$') < 2:
        return False
    method, salt, hashval = pwhash.split('$', 2)
    if method == 'plain':
        return hashval == password
    try:
        h = hashlib.new(method)
        h.update(salt)
        h.update(password)
        return h.hexdigest() == hashval
    except ValueError, e:
        return False

def gen_random_identifier(length=8):
    """Generate a random identifier."""
    if length <= 0:
        raise ValueError('requested key of length <= 0')
    return choice(IDENTIFIER_START) + \
           ''.join(choice(IDENTIFIER_CHAR) for _ in xrange(length - 1))
