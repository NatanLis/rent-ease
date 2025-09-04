import json
import asyncio
import os
import mimetypes
from datetime import datetime, date
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from api.core.database import engine
from api.core.security import get_password_hash

async def clear_tables(session: AsyncSession):
    """Clear all tables before loading seeds."""
    print("🧹 Clearing existing data...")
    await session.execute(text("DELETE FROM leases"))
    await session.execute(text("DELETE FROM units"))
    await session.execute(text("DELETE FROM properties"))
    await session.execute(text("DELETE FROM files"))
    await session.execute(text("DELETE FROM users WHERE email != 'admin@rent-ease.com'"))
    await session.commit()
    print("✅ Tables cleared")

async def load_files(session: AsyncSession):
    """Load sample files from tests/seeds/sample_files directory."""
    print("📁 Loading files...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    sample_files_dir = project_root / "tests" / "seeds" / "sample_files"
    
    # Get all PDF files from the directory
    pdf_files = list(sample_files_dir.glob("*.pdf"))
    
    sample_files_config = []
    for pdf_file in pdf_files:
        # Skip Zone.Identifier files (Windows metadata)
        if not pdf_file.name.endswith(":Zone.Identifier"):
            sample_files_config.append({
                "filename": pdf_file.name,
                "mimetype": "application/pdf"
            })
    
    files_added = 0
    
    for file_config in sample_files_config:
        file_path = sample_files_dir / file_config["filename"]
        
        if file_path.exists():
            try:
                # Read the actual file
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                file_size = len(file_data)
                
                await session.execute(text("""
                    INSERT INTO files (filename, mimetype, size, data, created_at)
                    VALUES (:filename, :mimetype, :size, :data, NOW())
                """), {
                    'filename': file_config['filename'],
                    'mimetype': file_config['mimetype'],
                    'size': file_size,
                    'data': file_data
                })
                
                print(f"   ✅ Added {file_config['filename']} ({file_size} bytes)")
                files_added += 1
                
            except Exception as e:
                print(f"   ❌ Error reading {file_config['filename']}: {e}")
        else:
            print(f"   ⚠️  File not found: {file_path}")
            print(f"      Please add {file_config['filename']} to the tests/seeds/sample_files/ directory")
    
    await session.commit()
    print(f"   📊 Total files added: {files_added}")

async def load_seeds():
    """Load test data from JSON files into database."""
    
    print("🚀 Loading test seeds...")
    
    # Create async session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Clear existing data first
            await clear_tables(session)
            # Load users
            print("📝 Loading users...")
            with open('tests/seeds/users_test_data.json', 'r') as f:
                users_data = json.load(f)
            
            for user_data in users_data:
                await session.execute(text("""
                    INSERT INTO users (email, hashed_password, first_name, last_name, username, role, is_active, created_at) 
                    VALUES (:email, :password, :first_name, :last_name, :username, :role, :is_active, :created_at)
                    ON CONFLICT (email) DO NOTHING
                """), {
                    'email': user_data['email'],
                    'password': get_password_hash(user_data['password']),
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'username': user_data['username'],
                    'role': user_data['role'],
                    'is_active': user_data.get('is_active', True),  # Default to active if not specified
                    'created_at': datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat()).replace('Z', '+00:00'))
                })
            
            await session.commit()
            
            # Get loaded user IDs for reference
            result = await session.execute(text("SELECT id, email FROM users ORDER BY id"))
            loaded_users = result.fetchall()
            print(f"✅ Loaded {len(users_data)} users:")
            for user in loaded_users:
                print(f"   - ID {user[0]}: {user[1]}")
            
            # Load properties
            print("🏠 Loading properties...")
            with open('tests/seeds/properties_test_data.json', 'r') as f:
                properties_data = json.load(f)
            
            for prop_data in properties_data:
                # Check if owner exists by email
                owner_check = await session.execute(text("""
                    SELECT id FROM users WHERE email = :owner_email
                """), {'owner_email': prop_data['owner_email']})
                
                owner_result = owner_check.fetchone()
                if not owner_result:
                    print(f"⚠️ Warning: Owner with email {prop_data['owner_email']} not found, skipping property '{prop_data['title']}'")
                    continue
                
                owner_id = owner_result[0]
                
                await session.execute(text("""
                    INSERT INTO properties (title, description, address, price, owner_id) 
                    VALUES (:title, :description, :address, :price, :owner_id)
                """), {
                    'title': prop_data['title'],
                    'description': prop_data['description'],
                    'address': prop_data['address'],
                    'price': prop_data['price'],
                    'owner_id': owner_id
                })
            
            await session.commit()
            
            # Get loaded property IDs for reference
            result = await session.execute(text("SELECT id, title, owner_id FROM properties ORDER BY id"))
            loaded_properties = result.fetchall()
            print(f"✅ Loaded properties:")
            for prop in loaded_properties:
                print(f"   - ID {prop[0]}: {prop[1]} (Owner: {prop[2]})")
            
            # Load units
            print("🏢 Loading units...")
            with open('tests/seeds/units_test_data.json', 'r') as f:
                units_data = json.load(f)
            
            print(f"   📊 Found {len(units_data)} units to load")
            
            for unit_data in units_data:
                print(f"   🔍 Processing unit: {unit_data['name']} for property: {unit_data['property_title']}")
                # Check if property exists by title
                property_check = await session.execute(text("""
                    SELECT id FROM properties WHERE title = :property_title
                """), {'property_title': unit_data['property_title']})
                
                property_result = property_check.fetchone()
                if not property_result:
                    print(f"⚠️ Warning: Property with title '{unit_data['property_title']}' not found, skipping unit '{unit_data['name']}'")
                    continue
                
                property_id = property_result[0]
                
                await session.execute(text("""
                    INSERT INTO units (property_id, name, description, monthly_rent) 
                    VALUES (:property_id, :name, :description, :monthly_rent)
                """), {
                    'property_id': property_id,
                    'name': unit_data['name'],
                    'description': unit_data['description'],
                    'monthly_rent': unit_data['monthly_rent']
                })
            
            await session.commit()
            
            # Get loaded unit IDs for reference
            result = await session.execute(text("SELECT id, name, property_id FROM units ORDER BY id"))
            loaded_units = result.fetchall()
            print(f"✅ Loaded units:")
            for unit in loaded_units:
                print(f"   - ID {unit[0]}: {unit[1]} (Property: {unit[2]})")
            
            # Load leases
            print("📋 Loading leases...")
            with open('tests/seeds/leases_test_data.json', 'r') as f:
                leases_data = json.load(f)
            
            for lease_data in leases_data:
                # Check if unit exists by name and property
                unit_check = await session.execute(text("""
                    SELECT u.id FROM units u 
                    JOIN properties p ON u.property_id = p.id 
                    WHERE u.name = :unit_name AND p.title = :property_title
                """), {
                    'unit_name': lease_data['unit_name'],
                    'property_title': lease_data['property_title']
                })
                
                unit_result = unit_check.fetchone()
                if not unit_result:
                    print(f"⚠️ Warning: Unit '{lease_data['unit_name']}' in property '{lease_data['property_title']}' not found, skipping lease")
                    continue
                
                unit_id = unit_result[0]
                
                # Check if tenant exists by email
                tenant_check = await session.execute(text("""
                    SELECT id FROM users WHERE email = :tenant_email
                """), {'tenant_email': lease_data['tenant_email']})
                
                tenant_result = tenant_check.fetchone()
                if not tenant_result:
                    print(f"⚠️ Warning: Tenant with email {lease_data['tenant_email']} not found, skipping lease")
                    continue
                
                tenant_id = tenant_result[0]
                
                # Convert date strings to date objects
                try:
                    start_date = datetime.strptime(lease_data['start_date'], '%Y-%m-%d').date()
                    end_date = datetime.strptime(lease_data['end_date'], '%Y-%m-%d').date() if lease_data['end_date'] else None
                except ValueError as e:
                    print(f"⚠️ Warning: Invalid date format in lease data: {e}, skipping lease")
                    continue
                
                await session.execute(text("""
                    INSERT INTO leases (unit_id, tenant_id, start_date, end_date, is_active) 
                    VALUES (:unit_id, :tenant_id, :start_date, :end_date, :is_active)
                """), {
                    'unit_id': unit_id,
                    'tenant_id': tenant_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': lease_data['is_active']
                })
            
            await session.commit()
            print(f"✅ Loaded {len(leases_data)} leases")
            
            # Load files
            await load_files(session)
            
            print("🎉 All test seeds loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading seeds: {str(e)}")
            print(f"❌ Exception type: {type(e).__name__}")
            await session.rollback()
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    asyncio.run(load_seeds())