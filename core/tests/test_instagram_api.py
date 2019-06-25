
from ..testcase import RequestTestCase


class InstagramAPI(RequestTestCase):

    def test_check_tags(self):
        """ проверка эндпоинта {tags}
        GET https://api.instagram.com/v1/tags/{tag-name}
        """
        response = self.make_request(
            url='https://api.instagram.com/v1/tags/iphone',
            status_code=400
        ).json()

        self.soft_assert_equal(
            self.response.status_code,
            400
        )

        self.soft_assert_equal(
            response['meta']['error_message'],
            'Missing client_id or access_token URL parameter.',
            'Не правильное сообщение ответа'
        )
