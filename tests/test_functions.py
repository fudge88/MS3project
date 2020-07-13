import unittest

class TestUserFunctions(unittest.TestCase):

    def test_register(self, username, confirm):
        return self.app.post(
            '/register',
            data=dict(username=username, confirm=confirm),
            follow_redirects=True
        )

    def test_login(self, username):
        return self.app.post(
            '/login',
            data=dict(username=username),
            follow_redirects=True
        )

    def test_logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )