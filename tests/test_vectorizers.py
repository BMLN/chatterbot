import unittest






from src.chatbot.instances import vectorizers





from numpy import shape







class HFVectorizerTest(unittest.TestCase):
    
    def test_DPREncoding(self):
        to_test = vectorizers.HFVectorizer.vectorize


        args = {
            "self": vectorizers.HFVectorizer("facebook/dpr-ctx_encoder-multiset-base"),
            "text": "This is a test sentence."
        }
        result = to_test(**args)


        self.assertEqual(len(result[0]), 768)


    def test_qwenEncoding1(self):
        to_test = vectorizers.HFVectorizer.vectorize


        args = {
            "self": vectorizers.HFVectorizer("Qwen/Qwen3-Embedding-4B"),
            "text": "This is a test sentence."
        }
        result = to_test(**args)

        self.assertEqual(len(result[0]), 2560)


    def test_qwenEncoding2(self):
        to_test = vectorizers.HFVectorizer("Qwen/Qwen3-Embedding-4B").vectorize


        queries = [
            "What is the capital of China?",
            "Explain gravity"
        ]
        documents = [
            "The capital of China is Beijing.",
            "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun."
        ]

        

        result = ( 
            to_test(queries),
            to_test(documents)
        )
        self.assertEqual(
            shape(result),
            (2, 2, 2560) 
        )
    


class HFTokenPredictorTest(unittest.TestCase):

    def test1(self):
        to_test = vectorizers.HFTokenPredictor.vectorize
        
        model_name = "Qwen/Qwen3-0.6B"
        args = {
            "self": vectorizers.HFTokenPredictor(model_name),
            "text": "What comes next will shock you: "
        }

        res = to_test(**args)
        self.assertEqual(
            (len(res), len(res[0])),
            (1, 151936)
        )
    
    def test2(self):
        to_test = vectorizers.HFTokenPredictor.vectorize
        
        model_name = "Qwen/Qwen3-0.6B"
        args = {
            "self": vectorizers.HFTokenPredictor(model_name),
            "text": [ "What comes next will shock you: " ]
        }

        res = to_test(**args)
        self.assertEqual(
            (len(res), len(res[0])),
            (1, 151936)
        )
    
    def test3(self):
        to_test = vectorizers.HFTokenPredictor.vectorize
        
        model_name = "Qwen/Qwen3-0.6B"
        args = {
            "self": vectorizers.HFTokenPredictor(model_name),
            "text": [ "What comes next will shock you: ", "Or did it?" ]
        }

        res = to_test(**args)
        self.assertEqual(
            (len(res), len(res[0])),
            (2, 151936)
        )



class HFTargetPredictorProbabilityTest(unittest.TestCase):
    
    def test1(self):
        to_test = vectorizers.HFTargetPredictor.logsoftmax_prob

        #args
        args = [
            [
                [12.625, 20.75 ],
                [13, 20.25 ]
            ]
        ]

        #test
        res = to_test(*args)

        self.assertGreater(res[0][1], 0.8)
        self.assertGreater(res[1][1], 0.8)



class HFTargetPredictorTest(unittest.TestCase):

    def test1(self):
        to_test = vectorizers.HFTargetPredictor.vectorize
        
        model_name = "Qwen/Qwen3-0.6B"
        args = {
            "self": vectorizers.HFTargetPredictor(model_name, targets=["yes", "no", "maybe"]), # I don't know, Can you repeat the question?
            "text": "What comes next will shock you: "
        }

        res = to_test(**args)
        self.assertEqual(
            shape(res),
            (1, 3)
        )

    def test2(self):
        to_test = vectorizers.HFTargetPredictor.vectorize
        
        model_name = "Qwen/Qwen3-0.6B"
        args = {
            "self": vectorizers.HFTargetPredictor(model_name, targets=["yes", "no", "maybe"]), # I don't know, Can you repeat the question?
            "text": ["What comes next will shock you: ", "Do you understand?" ]
        }

        res = to_test(**args)
        self.assertEqual(
            shape(res),
            (2, 3)
        )


    def test3(self):
        to_test = vectorizers.HFTargetPredictor.vectorize

        model_name = "Qwen/Qwen3-Reranker-0.6B"
        prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        queries = [
            "What is the capital of China?",
            "Explain gravity"
        ]
        documents = [
            "The capital of China is Beijing.",
            "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun."
        ]

        tp = vectorizers.HFTargetPredictor(model_name, ["no", "yes"])


        #test
        def frmt(a, b, instruction=None):
            if not instruction:
                instruction = "Given a web search query, retrieve relevant passages that answer the query"
    
            
            return f"<Instruct>: {instruction}\n<Query>: {a}\n<Document>: {b}".format(instruction=instruction,a=a, b=b)
        
        tp = vectorizers.HFTargetPredictor(model_name, ["no", "yes"])
        prefix = tp.tokenizer(prefix, add_special_tokens=False)["input_ids"][0]
        suffix = tp.tokenizer(suffix, add_special_tokens=False)["input_ids"][0]
        tp.tokenizer.prefix = prefix
        tp.tokenizer.suffix = suffix
        inputs = list(frmt(a, b) for a, b in zip(queries, documents))

        res = vectorizers.HFTargetPredictor.logsoftmax_prob(to_test(tp, inputs))

        self.assertEqual(
            shape(res),
            (2, 2)
        )
        self.assertAlmostEqual(
            res[0][1], 
            1,
            places=2
        )
        self.assertAlmostEqual(
            res[1][1],
            1,
            places=2
        )








#TODO
# class LightweightHFVectorizerTest(unittest.TestCase):
#     def test_lightweightDPREncoding(self):
#         to_test = vectorizers.HFVectorizer.vectorize


#         args = {
#             "self": vectorizers.HFVectorizer("facebook/dpr-ctx_encoder-multiset-base"),
#             "text": "This is a test sentence."
#         }
#         result = to_test(**args)


#         self.assertEqual(len(result[0]), 768)

















if __name__ == "__main__":
    unittest.main()