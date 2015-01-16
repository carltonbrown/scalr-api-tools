import unittest

from ScalrAccessor import ScalrApiContext

# The purpose of this script was generate data to help determine which roles/recipes are being referenced by scalr,
# and correlate farmname_rolenames to roles and recipes being used
# The output of the script was saved as instances_to_query.json
# which was fed to eric_report.rb to query chef for runlist information corresponding to those ec2 ids

# Prerequisite:   Add your machine IP to the API whitelist in scalr
# Caveat:   The object ID's may have drifted since this was written.
# Output:  printing a python hash looks exactly like json, as seen below:
#  [{'unique': 'mysql-custom_ol-mysql-master', 'nodename': 'i-47f8fd20'}, {'unique': 'mysql-custom_ol-mysql-slave', 'nodename': 'i-2abd8744'}]

class TestScalrApi(unittest.TestCase):
    def setUp(self):
        api_key = '162a5c5f521d04cc'
        secret_key = 'wrBsLKT1qHJ8PLhicHNEhV6mJg+A15PEAL37+k5cKXZ2764IPSSV2/p+XPxef9MdZvkhsaXQ2N8MS1zKMbrTS/myRouZ9RHjwXn/89iAz3dKLQTtMnRMrXf2dzuk5wjo'
        self.context = ScalrApiContext('https://api.scalr.net/', api_key, secret_key)
        

    def _test_retrieve_farmid_from_api(self):
        farm_ids = self.context.get_farm_ids()
        self.assertEqual(63, len(farm_ids))
        self.assertTrue('5140' in farm_ids)
        
    def _test_get_farms(self):
        farms = self.context.get_farms()
        self.assertEqual(63, len(farms))
    
    def _test_get_farm_details(self):
        farm = self.context.get_farm(13166)
        self.assertEqual('custom-production',farm.name())

    def _test_get_unique_instances_by_farm(self):
        farm = self.context.get_farm(13166)
        instances = farm.get_unique_instances()
        self.assertEqual(6, len(instances))
        
    def test_get_all_ec2_ids(self):
        # This is actually the productive payload
        uniques = []
        farms = self.context.get_farms()
        for farm in farms:
            entry = {}
            for unique in farm.get_unique_instances():
                entry = {'unique': farm.name() + "_" + unique.rolename,  'nodename': unique.servername}
                uniques.append(entry)
        # Output:  printing a python hash looks exactly like json, as seen below.    The output here drove the chef search script.
        print uniques
        