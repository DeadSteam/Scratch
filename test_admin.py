"""Test script to check if admin user exists and can authenticate."""
import asyncio
from src.core.database import get_users_db_session
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.core.config import settings


async def test_admin():
    """Test admin user creation and authentication."""
    user_repo = UserRepository()
    user_service = UserService(user_repo)
    
    async for session in get_users_db_session():
        try:
            # Check if admin exists
            print(f"Checking for admin user: {settings.ADMIN_USERNAME}")
            admin = await user_repo.get_by_username(settings.ADMIN_USERNAME, session)
            
            if admin:
                print(f"✅ Admin user found:")
                print(f"   ID: {admin.id}")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Active: {admin.is_active}")
                print(f"   Password hash exists: {bool(admin.password_hash)}")
                
                # Try to authenticate
                print(f"\nTrying to authenticate...")
                try:
                    result = await user_service.authenticate(
                        settings.ADMIN_USERNAME,
                        settings.ADMIN_PASSWORD,
                        session
                    )
                    print(f"✅ Authentication successful!")
                    print(f"   Access token: {result['access_token'][:50]}...")
                    print(f"   User ID: {result['user'].id}")
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
            else:
                print(f"❌ Admin user NOT found!")
                print(f"   Expected username: {settings.ADMIN_USERNAME}")
                print(f"   Please check if database is initialized")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(test_admin())





















