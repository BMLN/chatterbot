import unittest
from os import environ





from src.chatbot.instances import knowledgebases













class WeaviateTest(unittest.TestCase):
    

    def test_createid(self):
        
        data = {
            "embedding": [0,1,1,1,0,0,0,0.5],
            "data": {
                "text": "this is a test",
                "metadata1": 1,
                "metadata2": 2
            }
        }

        #confirm it's uuid
        self.assertRegex(
            knowledgebases.WeaviateKB.create_id([data]), 
            r"[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
        )




    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_init(self):
        to_test = knowledgebases.WeaviateKB

        args = {
            "host" : environ.get("KB_HOST"),
            "port" : environ.get("KB_PORT"),
            "collection" : environ.get("KB_COLLECTION")
        }


        #test
        self.assertIsNotNone(to_test(**args))





    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_create_with_id(self):
        to_test = knowledgebases.WeaviateKB.create

        args = {
            "self" : knowledgebases.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION")),
            "id": knowledgebases.WeaviateKB.create_id({
                "text": "this is a test",
                "metadata1": 1,
                "metadata2": 2
            }),
            "embedding": [0,1,1,1,0,0,0,0.5],
            "data": {
                "text": "this is a test",
                "metadata1": 1,
                "metadata2": 2
            }
        }
        

        #test
        self.assertNoLogs(to_test(**args))





    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_create_without_id(self):
        to_test = knowledgebases.WeaviateKB.create

        args = {
            "self" : knowledgebases.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION")),
            "embedding": [0,1,1,1,0,0,0,0.5],
            "data": {
                "text": "this is a test",
                "metadata1": 1,
                "metadata2": 2
            }
        }
        

        #test
        self.assertNoLogs(to_test(**args))







    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_retrieve(self):
        to_test = knowledgebases.WeaviateKB.retrieve

        args = {
            "self" : knowledgebases.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION")),
            "id": [
                knowledgebases.WeaviateKB.create_id(
                    {
                        "text": "this is a test",
                        "metadata1": 1,
                        "metadata2": 2
                    }
                )
            ]
        }
        

        #test
        self.assertTrue(all([ "id" in x and "data" in x for x in to_test(**args) ]))



    


    @unittest.skipIf(not environ.get("KB_HOST"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_PORT"), "no env variable set")
    @unittest.skipIf(not environ.get("KB_COLLECTION"), "no env variable set")
    def test_search(self):
        to_test = knowledgebases.WeaviateKB.search

        args = {
            "self" : knowledgebases.WeaviateKB(environ.get("KB_HOST"), environ.get("KB_PORT"), environ.get("KB_COLLECTION")),
            "embedding": [[0,1,1,1,0,0,0,0.5], [0,0,1,1,0,0,0,0.5]]
        }


        #test
        self.assertTrue(all(
            [
                "id" in xx and "distance" in xx and "data" in xx 
                for x in to_test(**args)
                for xx in x
            ]
        ))





if __name__ == "__main__":
    unittest.main()