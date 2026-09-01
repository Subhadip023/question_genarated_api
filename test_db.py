from app.database import SessionLocal
from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.user import User

db = SessionLocal()
inactive = db.query(User.email, User.password).join(OrganizationUser, OrganizationUser.user_id == User.id).join(Organization, Organization.id == OrganizationUser.org_id).filter(Organization.is_active == False).first()
active = db.query(User.email, User.password).join(OrganizationUser, OrganizationUser.user_id == User.id).join(Organization, Organization.id == OrganizationUser.org_id).filter(Organization.is_active == True).first()

print("INACTIVE:", inactive)
print("ACTIVE:", active)
