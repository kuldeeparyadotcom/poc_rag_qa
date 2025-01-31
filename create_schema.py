import weaviate
import weaviate.classes.config as wc

# Define the schema - optional as in this use case default schema is used
def create_schema(client=None):

    # Create only if client is not passed
    if client is None:
        client = weaviate.connect_to_custom(
            http_host="weaviate",
            http_port=8080,
            http_secure=False,
            grpc_host="weaviate",
            grpc_port=50051,
            grpc_secure=False
        )

    collection = client.collections.create(
        name="Document",
        properties=[
            wc.Property(name="text", data_type=wc.DataType.TEXT),
        ],
    )

    client.close()
    print("Schema created successfully")

if __name__ == "__main__":
    create_schema()