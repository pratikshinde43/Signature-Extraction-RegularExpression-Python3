from __future__ import absolute_import
import regex as re

SIGNATURE_MAX_LINES = 11
TOO_LONG_SIGNATURE_LINE = 60
RE_DELIMITER = re.compile('\r?\n?\t')


def get_delimiter(msg_body):
    delimiter = RE_DELIMITER.search(msg_body)
    if delimiter:
        delimiter = delimiter.group()
    else:
        delimiter = '\n'
    return delimiter


RE_SIGNATURE = re.compile(r'''
               (
                   (?:
                       ^thanks[\s,!]*$
                       |
                       ^thanks[ ]and[ ]regards[\s,!\w]*$
                       |
                       ^thanks[ ]&[ ]regards[\s,!\w]*$
                       |
                       ^regards[\s,!]*$
                       |
                       ^cheers[\s,!]*$
                       |
                       ^thanks[ ]&[ ]best[ ]regards[\s,!\w]*$
                       |
                       ^Sincerely[\s,!]*$
                   )
                   .*
               )
               ''', re.I | re.X | re.M | re.S)

# signatures appended by phone email clients
RE_PHONE_SIGNATURE = re.compile(r'''
               (
                   (?:
                       ^sent[ ]{1}from[ ]{1}my[\s,!\w]*$
                       |
                       ^sent[ ]from[ ]Mailbox[ ]for[ ]iPhone.*$
                       |
                       ^sent[ ]([\S]*[ ])?from[ ]my[ ]BlackBerry.*$
                       |
                       ^Enviado[ ]desde[ ]mi[ ]([\S]+[ ]){0,2}BlackBerry.*$
                   )
                   .*
               )
               ''', re.I | re.X | re.M | re.S)

# see _mark_candidate_indexes() for details
# c - could be signature line
# d - line starts with dashes (could be signature or list item)
# l - long line
RE_SIGNATURE_CANDIDATE = re.compile(r'''
    (?P<candidate>c+d)[^d]
    |
    (?P<candidate>c+d)$
    |
    (?P<candidate>c+)
    |
    (?P<candidate>d)[^d]
    |
    (?P<candidate>d)$
''', re.I | re.X | re.M | re.S)


def extract_signature(msg_body):
    '''
    Analyzes message for a presence of signature block (by common patterns)
    and returns tuple with two elements: message text without signature block
    and the signature itself.
    # >>> extract_signature('Hey man! How r u?\n\n--\nRegards,\nRoman')
    ('Hey man! How r u?', '--\nRegards,\nRoman')
    # >>> extract_signature('Hey man!')
    ('Hey man!', None)
    '''

    try:
        # identify line delimiter first
        delimiter = get_delimiter(msg_body)

        # make an assumption
        stripped_body = msg_body.strip()

        phone_signature = None

        # strip off phone signature
        phone_signature = RE_PHONE_SIGNATURE.search(msg_body)
        if phone_signature:
            stripped_body = stripped_body[:phone_signature.start()]
            phone_signature = phone_signature.group()

        #decide on signature candidate
        lines = stripped_body.splitlines()
        #
        return get_signature_candidate(lines)
        # candidate = delimiter.join(candidate)
        #
        # # try to extract signature
        # signature = RE_SIGNATURE.search(candidate)
        # if not signature:
        #     return 'Signature Not Found'
        #
        # else:
        #     signature = signature.group()
        #     stripped_body = delimiter.join(lines)
        #     stripped_body = stripped_body[:-len(signature)]
        #
        #     return signature
    except:

        print("Error in Extraction of Signature")


def get_signature_candidate(lines):
    """Return lines that could hold signature
    The lines should:
    * be among last SIGNATURE_MAX_LINES non-empty lines.
    * not include first line
    * be shorter than TOO_LONG_SIGNATURE_LINEget_signature_candidate
    * not include more than one line that starts with dashes
    """

    # non empty lines indexes
    non_empty = [i for i, line in enumerate(lines) if lines]

    if len(non_empty) <= 0:
        return []

    list3 = []
    for i in reversed(non_empty):
        signature = RE_SIGNATURE.search(lines[i])
        if signature:
            for j in range(i+1, len(non_empty)):
                list3.append(lines[j])
                if j > i + 1:
                    if lines[j] == RE_SIGNATURE.search(lines[i]):
                        break

    candidate = non_empty[0:]
    # signature shouldn't be longer then SIGNATURE_MAX_LINES
    candidate = candidate[-SIGNATURE_MAX_LINES:]
    return list3


mail = input("Enter the Email")

a = extract_signature(mail)
print(a)
