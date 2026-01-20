from ..interfaces.chatbot import Chatbot
from ..interfaces.batch import is_batch, batchify, batchable

#import chromadb #DEPR
import weaviate

from typing import override



from logging import getLogger
logger = getLogger()
getLogger("httpx").setLevel(40) #logging.ERROR = 40







# #DEPR
# class ChromaKB(Chatbot.KnowledgeBase):
#     def __init__(self, host, port, collection):
#         super().__init__()
#         self.__client = chromadb.HttpClient(host, port)
#         self.__collection = self.__client.get_or_create_collection(name=collection, metadata={"hnsw:space": "cosine"})

#     @override
#     @batchable(inherent=True)
#     def create(self, key, value, id=None):
#         self.__collection.add(
#             embeddings=key,
#             documents=value,
#             ids= id if id else (str(key) if is_batch(key) == False else [str(_key) for _key in key])
#         )

#     @override
#     @batchable(inherent=True)
#     def retrieve(self, x):
#         return self.__collection.get(x)
    
#     @override
#     @batchable(inherent=True)
#     def query(self, **args):
#         return self.__collection.query(**args)
    
#     @override
#     @batchable(inherent=True)
#     def search(self, x, **args):
#         __args = {
#             "query_embeddings": x,
#             "n_results": 5,
#             "include": ["documents", "distances", "embeddings"]
#         }
#         __args = __args | {key: value for key, value in args.getitems() if key in __args }

#         output = self.__collection.query(**args)
#         output["ids"] = output["ids"][0]
#         output["distances"] = output["distances"][0]
#         output["documents"] = output["documents"][0]

#         return output
    



class WeaviateKB(Chatbot.KnowledgeBase):
    
    def __init__(self, host, port, collection):
        super().__init__()

        self.con_cfg = weaviate.connect.ConnectionParams.from_params(
            http_host=host,
            http_port=port,
            http_secure=False,
            grpc_host=host,
            grpc_port=50051,
            grpc_secure=False
        )
        self.collection = str(collection)
        #self.client = weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True)
        #self.client.close()
        
        with weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True) as conn:
            # if conn.collections.exists(str(collection)): #testing only
            #     conn.collections.delete(str(collection))

            if conn.collections.exists(self.collection) == False:
                conn.collections.create(
                    name=self.collection,
                    #vectorizer=None, #invalid param, no doc about correct no vectorizer param
                    vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw( # or "flat" or "dynamic"
                        distance_metric=weaviate.classes.config.VectorDistances.DOT, # or "cosine"
                        quantizer=None
                    ),
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
                    properties=[
                        #weaviate.classes.config.Property(name="value", data_type=weaviate.classes.config.DataType.TEXT)
                    ]
                )
                logger.info(f"{"WeaviateKB"} created {self.collection}-collection")

            #self.collection = conn.collections.get(str(collection))
            logger.info(f"{"WeaviateKB"} succesfully connected to {host}:{port}")


    def __del__(self):
        pass
        # self.client.close()



    @override
    @batchify("embedding")
    @batchable(inherent=True)
    def create(self, id, embedding, data, batch_size=100):
        if is_batch(id) == False:
            raise ValueError("id should be batchable")

        if not embedding:
            embedding = [ None ] * len(id)

        if is_batch(embedding) == False:
            raise ValueError("embedding should be batchable")
        
        if is_batch(data) == False:
            raise ValueError("data should be batchable")
            # keys = [ key ]
            # values = [ value ]
            # ids = [ id if id else weaviate.util.generate_uuid5(value) ]
        if (len(id) == len(embedding) == len(data)) == False:
            raise Exception("<todo>")


        with weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True) as conn:
            with conn.collections.get(self.collection).batch.fixed_size(batch_size=batch_size) as batch:
                for i, v, d in zip(id, embedding, data):
                    batch.add_object(
                        properties= d,
                        vector= v,
                        uuid = i
                    )


    @override
    @batchable(inherent=True)
    def retrieve(self, id):
        with weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True) as conn:
            data = conn.collections.get(self.collection).query.fetch_objects_by_ids(id)
            
            return [ 
                {"id": str(x.uuid), "data": x.properties }
                for x in data.objects
            ]


    @override
    @batchable(inherent=True)
    def query(self, filter: weaviate.classes.query.Filter= None):
        with weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True) as conn:
            data = conn.collections.get(self.collection).query.fetch_objects(
                filters=filter
            )

            return [ 
                {"id": str(x.uuid), "data": x.properties } for x in data.objects
            ]
    

    @override
    @batchify("embedding", list[list[float]])
    def search(self, embedding, **args):
        #TODO: args + kwargs
        #TODO: fully list/support (all/useful?) of the (potential) args
        __args = {
            "near_vector": embedding,
            "limit": 5,
            "return_metadata": weaviate.classes.query.MetadataQuery(distance=True)
        }
        __args = __args | {key: value for key, value in args.items() if key in __args }

        with weaviate.WeaviateClient(self.con_cfg, skip_init_checks=True) as conn:
            data = conn.collections.get(self.collection).query.near_vector(**__args).objects
            
            return [ 
                {"id": str(x.uuid), "distance": x.metadata.distance, "data": x.properties }
                for x in data
            ]

        
    @override
    @batchify("data")
    @batchable(inherent=True)
    def update(self, id, data):
        pass

    @override
    @batchable(inherent=True)
    def delete(self, id):
        self.__collection.delete(id)

    @override
    @classmethod
    def create_id(cls, data):
        return weaviate.util.generate_uuid5(data)
    
