from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

# Set up logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def migrate(src: str, dst: str, batch_size: int = 100):
    """
    Migrate collections from source to destination Qdrant instance.

    Args:
        src: Source Qdrant URL
        dst: Destination Qdrant URL
        batch_size: Number of points to transfer in each batch
    """
    src_client = QdrantClient(url=src)
    dst_client = QdrantClient(url=dst)

    collections = src_client.get_collections().collections
    total_collections = len(collections)

    for i, coll in enumerate(collections, 1):
        print("================================")
        logger.info(f"Migrating collection {coll.name} ({i}/{total_collections})")

        # Get source collection info
        collection_info = src_client.get_collection(collection_name=coll.name)
        params = collection_info.config.params.vectors

        if params is not None:
            try:
                # Recreate collection in destination
                dst_client.recreate_collection(
                    collection_name=coll.name, vectors_config=params
                )

                points_migrated = 0
                next_batch_offset = None

                while True:
                    response = src_client.scroll(
                        collection_name=coll.name,
                        limit=batch_size,
                        offset=next_batch_offset,
                        with_payload=True,
                        with_vectors=True,
                    )

                    points, next_batch_offset = response

                    if not points:
                        break

                    # Prepare points for upload
                    upsert_points = []
                    for point in points:
                        upsert_points.append(
                            models.PointStruct(
                                id=point.id,
                                vector=point.vector,
                                payload=point.payload,
                            )
                        )

                    if upsert_points:
                        dst_client.upsert(
                            collection_name=coll.name, points=upsert_points
                        )

                    points_migrated += len(points)
                    logger.info(f"Migrated {points_migrated} points in {coll.name}")

                    if next_batch_offset is None:
                        break

                src_count = src_client.count(collection_name=coll.name).count
                dst_count = dst_client.count(collection_name=coll.name).count

                if src_count == dst_count:
                    logger.info(
                        f"Successfully migrated {coll.name}: {src_count} points"
                    )
                else:
                    logger.error(
                        f"Point count mismatch in {coll.name}: source={src_count}, dest={dst_count}"
                    )
                    logger.error(f"Points processed: {points_migrated}")

            except Exception as e:
                logger.error(f"Error migrating collection {coll.name}: {str(e)}")
                raise


if __name__ == "__main__":
    migrate("http://10.181.131.244:6333", "http://10.181.131.250:6333")
