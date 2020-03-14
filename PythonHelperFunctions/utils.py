import os


def load_dropbox_path(user_path=None):

    """ Provide a single point of entry for user-, platform-, or machine-specific Dropbox installations """

    if not user_path:

        if os.environ['USERNAME'] == 'kmccarthy':

            if os.environ['COMPUTERNAME'] == 'IDMPPTSS03':
                user_path = os.path.join('D:', os.sep, 'kmccarthy')

            if os.environ['COMPUTERNAME'] == 'IDMPPWKS097':
                user_path = os.path.join('C:', os.sep, 'Users', 'kmccarthy')

        else: #Add more users here
            dropbox_path = None

    dropbox_path = os.path.join(user_path, 'Dropbox (IDM)')

    return dropbox_path
