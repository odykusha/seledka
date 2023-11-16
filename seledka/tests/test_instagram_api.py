
from seledka.testcase import RequestTestCase


class InstagramAPI(RequestTestCase):

    def test_check_tags(self):
        """ проверка эндпоинта {tags}
        GET https://gorest.co.in/public/v2/users
        """
        response = self.make_request(
            url='https://gorest.co.in/public/v2/users',
            status_code=200
        ).json()

        self.soft_assert_equal(
            type(response[0]['id']),
            int,
            'wrong type of id'
        )
