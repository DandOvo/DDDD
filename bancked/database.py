from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos.container import ContainerProxy
from typing import Optional, List, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class CosmosDBClient:
    def __init__(self):
        self.client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
        self.database = None
        self.users_container = None
        self.body_metrics_container = None
        self.workouts_container = None
        self.nutrition_container = None
        self.progress_photos_container = None

    def initialize(self):
        """Initialize database and containers"""
        try:
            # Create database if it doesn't exist
            self.database = self.client.create_database_if_not_exists(
                id=settings.cosmos_database_name
            )
            logger.info(f"Database '{settings.cosmos_database_name}' is ready")

            # Create users container if it doesn't exist
            self.users_container = self.database.create_container_if_not_exists(
                id="users",
                partition_key=PartitionKey(path="/id"),
                offer_throughput=400,
            )
            logger.info("Users container is ready")

            # Create body_metrics container if it doesn't exist
            self.body_metrics_container = self.database.create_container_if_not_exists(
                id="body_metrics",
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400,
            )
            logger.info("Body metrics container is ready")

            # Create workouts container if it doesn't exist
            self.workouts_container = self.database.create_container_if_not_exists(
                id="workouts",
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400,
            )
            logger.info("Workouts container is ready")

            # Create nutrition container if it doesn't exist
            self.nutrition_container = self.database.create_container_if_not_exists(
                id="nutrition",
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400,
            )
            logger.info("Nutrition container is ready")

            # Create progress_photos container if it doesn't exist
            self.progress_photos_container = self.database.create_container_if_not_exists(
                id="progress_photos",
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400,
            )
            logger.info("Progress photos container is ready")

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise

    # User operations
    def create_user(self, user_data: dict) -> dict:
        """Create a new user"""
        try:
            return self.users_container.create_item(body=user_data)
        except exceptions.CosmosResourceExistsError:
            raise ValueError("User already exists")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            query = "SELECT * FROM users u WHERE u.email = @email"
            parameters = [{"name": "@email", "value": email}]
            items = list(
                self.users_container.query_items(
                    query=query, parameters=parameters, enable_cross_partition_query=True
                )
            )
            return items[0] if items else None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            return self.users_container.read_item(item=user_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise

    # Body Metrics operations
    def create_body_metric(self, metric_data: dict) -> dict:
        """Create a new body metric record"""
        try:
            return self.body_metrics_container.create_item(body=metric_data)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create body metric: {e}")
            raise

    def get_body_metric_by_id(self, metric_id: str, user_id: str) -> Optional[dict]:
        """Get body metric by ID"""
        try:
            return self.body_metrics_container.read_item(item=metric_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get body metric by ID: {e}")
            raise

    def get_user_body_metrics(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """Get paginated list of user's body metrics"""
        try:
            query = "SELECT * FROM c WHERE c.userId = @userId"
            parameters = [{"name": "@userId", "value": user_id}]

            if start_date:
                query += " AND c.recordedAt >= @startDate"
                parameters.append({"name": "@startDate", "value": start_date})
            if end_date:
                query += " AND c.recordedAt <= @endDate"
                parameters.append({"name": "@endDate", "value": end_date})

            query += " ORDER BY c.recordedAt DESC"

            count_query = query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.body_metrics_container.query_items(query=count_query, parameters=parameters)
            )
            total = count_result[0] if count_result else 0

            offset = (page - 1) * page_size
            query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.body_metrics_container.query_items(query=query, parameters=parameters)
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user body metrics: {e}")
            raise

    def update_body_metric(self, metric_id: str, user_id: str, updates: dict) -> dict:
        """Update body metric"""
        try:
            existing = self.get_body_metric_by_id(metric_id, user_id)
            if not existing:
                raise ValueError("Body metric not found")
            existing.update(updates)
            return self.body_metrics_container.replace_item(item=metric_id, body=existing)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update body metric: {e}")
            raise

    def delete_body_metric(self, metric_id: str, user_id: str) -> bool:
        """Delete body metric"""
        try:
            self.body_metrics_container.delete_item(item=metric_id, partition_key=user_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete body metric: {e}")
            raise

    # Workouts operations
    def create_workout(self, workout_data: dict) -> dict:
        """Create a new workout record"""
        try:
            return self.workouts_container.create_item(body=workout_data)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create workout: {e}")
            raise

    def get_workout_by_id(self, workout_id: str, user_id: str) -> Optional[dict]:
        """Get workout by ID"""
        try:
            return self.workouts_container.read_item(item=workout_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get workout by ID: {e}")
            raise

    def get_user_workouts(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        workout_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """Get paginated list of user's workouts"""
        try:
            query = "SELECT * FROM c WHERE c.userId = @userId"
            parameters = [{"name": "@userId", "value": user_id}]

            if workout_type:
                query += " AND c.workoutType = @workoutType"
                parameters.append({"name": "@workoutType", "value": workout_type})
            if start_date:
                query += " AND c.startTime >= @startDate"
                parameters.append({"name": "@startDate", "value": start_date})
            if end_date:
                query += " AND c.startTime <= @endDate"
                parameters.append({"name": "@endDate", "value": end_date})

            query += " ORDER BY c.startTime DESC"

            count_query = query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.workouts_container.query_items(query=count_query, parameters=parameters)
            )
            total = count_result[0] if count_result else 0

            offset = (page - 1) * page_size
            query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.workouts_container.query_items(query=query, parameters=parameters)
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user workouts: {e}")
            raise

    def update_workout(self, workout_id: str, user_id: str, updates: dict) -> dict:
        """Update workout"""
        try:
            existing = self.get_workout_by_id(workout_id, user_id)
            if not existing:
                raise ValueError("Workout not found")
            existing.update(updates)
            return self.workouts_container.replace_item(item=workout_id, body=existing)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update workout: {e}")
            raise

    def delete_workout(self, workout_id: str, user_id: str) -> bool:
        """Delete workout"""
        try:
            self.workouts_container.delete_item(item=workout_id, partition_key=user_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete workout: {e}")
            raise

    # Nutrition operations
    def create_nutrition(self, nutrition_data: dict) -> dict:
        """Create a new nutrition record"""
        try:
            return self.nutrition_container.create_item(body=nutrition_data)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create nutrition: {e}")
            raise

    def get_nutrition_by_id(self, nutrition_id: str, user_id: str) -> Optional[dict]:
        """Get nutrition by ID"""
        try:
            return self.nutrition_container.read_item(item=nutrition_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get nutrition by ID: {e}")
            raise

    def get_user_nutrition(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """Get paginated list of user's nutrition records"""
        try:
            query = "SELECT * FROM c WHERE c.userId = @userId"
            parameters = [{"name": "@userId", "value": user_id}]

            if start_date:
                query += " AND c.recordedAt >= @startDate"
                parameters.append({"name": "@startDate", "value": start_date})
            if end_date:
                query += " AND c.recordedAt <= @endDate"
                parameters.append({"name": "@endDate", "value": end_date})

            query += " ORDER BY c.recordedAt DESC"

            count_query = query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.nutrition_container.query_items(query=count_query, parameters=parameters)
            )
            total = count_result[0] if count_result else 0

            offset = (page - 1) * page_size
            query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.nutrition_container.query_items(query=query, parameters=parameters)
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user nutrition: {e}")
            raise

    def update_nutrition(self, nutrition_id: str, user_id: str, updates: dict) -> dict:
        """Update nutrition"""
        try:
            existing = self.get_nutrition_by_id(nutrition_id, user_id)
            if not existing:
                raise ValueError("Nutrition not found")
            existing.update(updates)
            return self.nutrition_container.replace_item(item=nutrition_id, body=existing)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update nutrition: {e}")
            raise

    def delete_nutrition(self, nutrition_id: str, user_id: str) -> bool:
        """Delete nutrition"""
        try:
            self.nutrition_container.delete_item(item=nutrition_id, partition_key=user_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete nutrition: {e}")
            raise

    # Progress Photos operations
    def create_progress_photo(self, photo_data: dict) -> dict:
        """Create a new progress photo record"""
        try:
            return self.progress_photos_container.create_item(body=photo_data)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create progress photo: {e}")
            raise

    def get_progress_photo_by_id(self, photo_id: str, user_id: str) -> Optional[dict]:
        """Get progress photo by ID"""
        try:
            return self.progress_photos_container.read_item(item=photo_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get progress photo by ID: {e}")
            raise

    def get_user_progress_photos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        photo_type: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """Get paginated list of user's progress photos"""
        try:
            query = "SELECT * FROM c WHERE c.userId = @userId"
            parameters = [{"name": "@userId", "value": user_id}]

            if photo_type:
                query += " AND c.photoType = @photoType"
                parameters.append({"name": "@photoType", "value": photo_type})

            query += " ORDER BY c.recordedAt DESC"

            count_query = query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.progress_photos_container.query_items(query=count_query, parameters=parameters)
            )
            total = count_result[0] if count_result else 0

            offset = (page - 1) * page_size
            query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.progress_photos_container.query_items(query=query, parameters=parameters)
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user progress photos: {e}")
            raise

    def update_progress_photo(self, photo_id: str, user_id: str, updates: dict) -> dict:
        """Update progress photo"""
        try:
            existing = self.get_progress_photo_by_id(photo_id, user_id)
            if not existing:
                raise ValueError("Progress photo not found")
            existing.update(updates)
            return self.progress_photos_container.replace_item(item=photo_id, body=existing)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update progress photo: {e}")
            raise

    def delete_progress_photo(self, photo_id: str, user_id: str) -> bool:
        """Delete progress photo"""
        try:
            self.progress_photos_container.delete_item(item=photo_id, partition_key=user_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete progress photo: {e}")
            raise


# Global instance
cosmos_db = CosmosDBClient()
