from unittest import TestCase, mock
from bvb.share import Share
from bvb.scraper_service import ScraperService


# print(mocked_requests_get('abc', 200).text)
class TestScraperService(TestCase):
    def test_standardize_list_parameter(self):

        # VALUE MEANING ALL
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value=''),
            ['REGS', 'AERO', 'MTS']
        )
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value='all'),
            ['REGS', 'AERO', 'MTS']
        )
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value='ALL'),
            ['REGS', 'AERO', 'MTS']
        )

        # VALUE GIVEN AS STR
        # test value given as str -> valid value
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value='AERO'),
            ['AERO']
        )
        # test value given as str -> valid value with lower case
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value=['mts']),
            ['MTS']
        )
        # test value given as str -> invalid value
        try:
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value='INV')
            assert False
        except ValueError:
            assert True

        # VALUE GIVEN AS LIST
        # test for valid value; len(list) = 1
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS'], value=['AERO']),
            ['AERO']
        )
        # test for valid value; len(list) > 1
        self.assertListEqual(
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS', 'NEW'],
                                                         value=['AERO', 'REGS']),
            ['AERO', 'REGS']
        )
        # test for invalid value; len(list) = 1
        try:
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS', 'NEW'],
                                                         value=['INVALID'])
            assert False
        except ValueError:
            assert True
        # test for invalid value; len(list) > 1 containing both valid and invalid inputs
        try:
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS', 'NEW'],
                                                         value=['REGS', 'INVALID'])
            assert False
        except ValueError:
            assert True

        # TEST FOR TYPE ERRORS
        try:
            ScraperService()._standardize_list_parameter(possible_values={'REGS': '', 'AERO': '', 'MTS': '', 'NEW': ''},
                                                         value=['REGS'])
            assert False
        except TypeError:
            assert True
        try:
            ScraperService()._standardize_list_parameter(possible_values=['REGS', 'AERO', 'MTS', 'NEW'],
                                                         value={'REGS': ''})
            assert False
        except TypeError:
            assert True

    @mock.patch('bvb.scraper_service.requests')
    def test_get_shares(self, mock_requests):
        mock_response = mock.MagicMock()

        # test response code 200 + all valid rows should be returned
        mock_response.status_code = 200
        mock_response.text = ""
        with open("./tests/resources/test_get_shares/mockup_data", newline='\r\n') as f:
            mock_response.text = f.read()
        mock_requests.get.return_value = mock_response

        # test without filter
        resp = ScraperService().get_shares()
        resp_exp = [Share(symbol="AAG"), Share(symbol="MABE"), Share(symbol="ABC")]
        assert len(resp) == len(resp_exp)
        for i in range(len(resp)):
            assert resp[i] == resp_exp[i]

        # test with market filter
        resp = ScraperService().get_shares(market='REGS')
        resp_exp = [Share(symbol="AAG"), Share(symbol="ABC")]
        assert len(resp) == len(resp_exp)
        for i in range(len(resp)):
            assert resp[i] == resp_exp[i]

        # test with market and tier filter
        resp = ScraperService().get_shares(market='REGS', tier="MTS_INTL")
        resp_exp = []
        assert len(resp) == len(resp_exp)

        # test with market list - one element from list is not in mocking data
        resp = ScraperService().get_shares(market=['MTS', 'REGS'])
        resp_exp = [Share(symbol="AAG"), Share(symbol="ABC")]
        assert len(resp) == len(resp_exp)
        for i in range(len(resp)):
            assert resp[i] == resp_exp[i]

