"""User service for business logic."""

import logging

import bcrypt
from passlib.context import CryptContext

from src.models.users import User, UserCreate, UserInDB, UserProfileUpdate, UserUpdate
from src.repositories.users import UserRepository

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """User service for business logic operations."""

    def __init__(self):
        self.user_repo = UserRepository()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        # Truncate password to 72 bytes to match hashing behavior
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            logger.debug("Password truncated to 72 bytes for verification")

        try:
            return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
        except (ValueError, TypeError) as e:
            logger.error("Password verification failed: %s", str(e))
            return False

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        # Truncate password to 72 bytes to avoid bcrypt limitation
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            logger.warning("Password truncated to 72 bytes due to bcrypt limitation")

        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode("utf-8")
        except Exception as e:
            logger.error("Password hashing failed: %s", str(e))
            raise

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        logger.info("Creating user: %s (%s)", user_create.username, user_create.email)

        # Check if email is already taken
        if await self.user_repo.is_email_taken(user_create.email):
            logger.warning("Email already registered: %s", user_create.email)
            raise ValueError("Email already registered")

        # Check if username is already taken
        if await self.user_repo.is_username_taken(user_create.username):
            logger.warning("Username already taken: %s", user_create.username)
            raise ValueError("Username already taken")

        # Hash password
        hashed_password = self.get_password_hash(user_create.password)
        logger.debug("Password hashed for user: %s", user_create.username)

        # Create user
        user_in_db = await self.user_repo.create_user(user_create, hashed_password)
        logger.info(
            "User created successfully: %s (ID: %s)", user_in_db.username, user_in_db.id
        )

        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
        )

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        user_in_db = await self.user_repo.get_by_id(user_id)
        if not user_in_db:
            return None

        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
        )

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        """Get user by email (returns UserInDB for authentication)."""
        return await self.user_repo.get_by_email(email)

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        """Get user by username (returns UserInDB for authentication)."""
        return await self.user_repo.get_by_username(username)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User | None:
        """Update user."""
        # Check if email is being changed and if it's already taken
        if user_update.email:
            existing_user = await self.user_repo.get_by_email(user_update.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")

        # Check if username is being changed and if it's already taken
        if user_update.username:
            existing_user = await self.user_repo.get_by_username(user_update.username)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Username already taken")

        user_in_db = await self.user_repo.update(user_id, user_update)
        if not user_in_db:
            return None

        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
        )

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by setting as inactive."""
        logger.info("Deactivating user with ID: %s", user_id)

        # Create an update object to set is_active to False
        user_update = UserUpdate(is_active=False)

        user_in_db = await self.user_repo.update(user_id, user_update)
        if not user_in_db:
            logger.warning("User not found for deactivation: %s", user_id)
            return False

        logger.info("User deactivated successfully: %s", user_in_db.username)
        return True

    async def get_users(
        self, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> list[User]:
        """Get all users with pagination and optional search."""
        users_in_db = await self.user_repo.get_many(
            skip=skip, limit=limit, search=search
        )
        return [
            User(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users_in_db
        ]

    async def authenticate_user(self, email: str, password: str) -> UserInDB | None:
        """Authenticate user with email and password."""
        logger.debug("Authenticating user: %s", email)

        user = await self.get_user_by_email(email)
        if not user:
            logger.warning("Authentication failed: user not found for email %s", email)
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning(
                "Authentication failed: invalid password for user %s", user.username
            )
            return None

        if not user.is_active:
            logger.warning(
                "Authentication failed: inactive user %s attempted to login",
                user.username,
            )
            return None

        logger.info("Authentication successful for user: %s", user.username)
        return user

    async def update_user_profile(
        self, user_id: str, profile_update: UserProfileUpdate
    ) -> User | None:
        """Update user profile (self-update with password verification)."""
        logger.info("Updating profile for user ID: %s", user_id)

        # Get current user data
        user_in_db = await self.user_repo.get_by_id(user_id)
        if not user_in_db:
            logger.warning("User not found for profile update: %s", user_id)
            return None

        # If password change is requested, verify current password
        if profile_update.new_password:
            if not profile_update.current_password:
                raise ValueError("Current password is required to change password")

            if not self.verify_password(
                profile_update.current_password, user_in_db.hashed_password
            ):
                logger.warning(
                    "Invalid current password for user: %s", user_in_db.username
                )
                raise ValueError("Invalid current password")

        # Check if email is being changed and if it's already taken
        if profile_update.email and profile_update.email != user_in_db.email:
            existing_user = await self.user_repo.get_by_email(profile_update.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")

        # Check if username is being changed and if it's already taken
        if profile_update.username and profile_update.username != user_in_db.username:
            existing_user = await self.user_repo.get_by_username(
                profile_update.username
            )
            if existing_user and existing_user.id != user_id:
                raise ValueError("Username already taken")

        # Create update object (exclude password fields from direct update)
        update_data = profile_update.model_dump(
            exclude_unset=True, exclude={"current_password", "new_password"}
        )

        # If new password provided, hash it
        if profile_update.new_password:
            update_data["hashed_password"] = self.get_password_hash(
                profile_update.new_password
            )

        # Create a UserUpdate object for the repository
        user_update = UserUpdate(**update_data)

        updated_user = await self.user_repo.update(user_id, user_update)
        if not updated_user:
            logger.error("Failed to update user profile: %s", user_id)
            return None

        logger.info("Profile updated successfully for user: %s", updated_user.username)
        return User(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            is_active=updated_user.is_active,
            is_admin=updated_user.is_admin,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    async def count_users(self) -> int:
        """Count total users."""
        logger.info("Counting total users")
        try:
            count = await self.user_repo.count()
            logger.info("Total users count: %d", count)
            return count
        except Exception as e:
            logger.error("Error counting users: %s", str(e))
            raise

    async def count_active_users(self) -> int:
        """Count active users."""
        logger.info("Counting active users")
        try:
            count = await self.user_repo.count({"is_active": True})
            logger.info("Active users count: %d", count)
            return count
        except Exception as e:
            logger.error("Error counting active users: %s", str(e))
            raise
