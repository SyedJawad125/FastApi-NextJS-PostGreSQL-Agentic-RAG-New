from app.database import SessionLocal
from app.models import User
from app.utils.hashing import get_password_hash
from sqlalchemy.exc import SQLAlchemyError

def populate():
    db = SessionLocal()

    try:
        # Step 1: Check/Create superuser
        superuser = db.query(User).filter(User.username == "adminuser1").first()
        if not superuser:
            superuser = User(
                username="adminuser1",
                email="syedjawadali92@gmail.com",
                hashed_password=get_password_hash("password123"),
                is_superuser=True,
                is_active=True
            )
            db.add(superuser)
            db.commit()
            db.refresh(superuser)
            print("✅ Superuser created.")
        else:
            print("✅ Superuser already exists.")

        # ✅ Skip creating role and assigning it to superuser
        print("ℹ️ Skipping role and permission assignment for superuser. Superuser has all permissions by default.")

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Error:", str(e))
    finally:
        db.close()

if __name__ == "__main__":
    populate()
