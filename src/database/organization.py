from ..const import const
from . import connector
from ..models.organization import Organization as Org

class Organization:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()
        self.org = Org()

    def add_organization(self, name: str, contact_phone: str, contact_email: str, description: str, username: str, org_member: list[str]) -> bool:
        organization_id = self.org.generate_organization_id(name)
        organization_status = const.STATUS_ACTIVE

        query_user = """SELECT customer_id FROM tbl_customer WHERE username = %s"""
        value_user = (username,)

        user_data = self.db.execute_query(query_user, value_user)

        query_subcription = """SELECT subscription_id FROM tbl_subscription WHERE customer_id = %s"""
        value_subscription = (str(user_data[0][0]),)
        
        org_member.append(username)

        subscription_id = self.db.execute_query(query_subcription, value_subscription)
        

        if len(user_data) == 0:
            print("Error in querying user data")
            return False

        query = """
            INSERT INTO tbl_organization (
                organization_id, name, customer_id, organization_status,
                subscription_id, description, contact_phone, contact_email, org_member
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (str(organization_id), name, str(user_data[0][0]), organization_status, str(subscription_id[0][0]), description, contact_phone, contact_email, org_member,)

        try:
            self.db.execute_query(query, values)
            print("Add organization successful!")
            return True
        except Exception as e:
            print("Error adding organization:", e)
            return False

    def get_organization_by_id(self, username: str, organization_id: str) :
        query = """SELECT name, organization_status, description FROM tbl_organization WHERE organization_id = %s AND %s = ANY(org_member)"""
        values = (organization_id, username,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            return result
        except Exception as e:
            print("Error querying organization:", e)

    def get_all_organizations(self, username: str):
        query = """SELECT name, organization_status, description FROM tbl_organization WHERE %s = ANY(org_member)"""
        values = (username,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            return result
        except Exception as e:
            print("Error querying organization:", e)

    def check_user_access(self, username: str, organization_id: str) -> bool:
        query = """ SELECT COUNT(*) FROM tbl_organization WHERE organization_id = %s AND  %s = ANY(org_member) """
        values = (organization_id, username,)
        try:
            result = self.db.execute_query(query, values)
            access_granted = result[0][0] > 0
            return access_granted
        except Exception as e:
            print("Error checking user access:", e)
            return False

    def change_organization_status(self, organization_id: str, status: str) -> bool:
        query = """UPDATE tbl_organization SET organization_status = %s WHERE organization_id = %s"""
        if status == const.STATUS_INACTIVE:
            values = (const.STATUS_INACTIVE, organization_id)
        else :
            values = (const.STATUS_ACTIVE, organization_id)
        try:
            self.db.execute_query(query, values)
            print("Organization status changed successfully!")
            return True
        except Exception as e:
            print("Error changing organization status:", e)
            return False

    def update_information(self, name: str, contact_phone: str, contact_email: str, description: str, organization_id: str) -> bool:
        query = """ UPDATE tbl_organization SET name = %s, contact_phone = %s, contact_email = %s, description = %s WHERE organization_id = %s"""
        values = (name, contact_phone, contact_email, description, organization_id,)
        try:
            self.db.execute_query(query, values)
            print("Organization information updated successfully!")
            return True
        except Exception as e:
            print("Error updating organization information:", e)
            return False

    def add_user(self, organization_id: str, new_user: list[str]) -> bool:
        query = """ UPDATE tbl_organization SET org_member = array_append(org_member, %s) WHERE organization_id = %s"""
        values = (new_user, organization_id,)
        try:
            self.db.execute_query(query, values)
            print("User added to organization successfully!")
            return True
        except Exception as e:
            print("Error adding user to organization:", e)
            return False

    def remove_user(self, organization_id: str, remove_username: str) -> bool:
        query = """UPDATE tbl_organization SET org_member = array_remove(org_member, %s) WHERE organization_id = %s"""
        values = (remove_username, organization_id,)
        try:
            self.db.execute_query(query, values)
            print("User removed from organization successfully!")
            return True
        except Exception as e:
            print("Error removing user from organization:", e)
            return False

    def check_organization_name_exist(self, name: str) -> bool:
        query = "SELECT COUNT(*) FROM tbl_organization WHERE name = %s"
        values = (name,)
        try:
            result = self.db.execute_query(query, values)
            return result[0][0] > 0
        except Exception as e:
            print("Error checking organization name existence:", e)
            return False
        
    def check_organization_slot(self, username: str):
        try:
            # Get customer_id from tbl_customer using username
            query_customer_id = "SELECT customer_id FROM tbl_customer WHERE username = %s"
            values_customer_id = (username,)
            customer_id = self.db.execute_query(query_customer_id, values_customer_id)[0][0]

            # Get subscription_type from tbl_subscription
            query_subscription = "SELECT subscription_type FROM tbl_subscription WHERE customer_id = %s"
            values_subscription = (customer_id,)
            subscription_type = self.db.execute_query(query_subscription, values_subscription)[0][0]

            # Get slot from tbl_package
            query_slot = "SELECT slot_number FROM tbl_package WHERE package_id = %s"
            values_slot = (subscription_type,)
            total_slot = self.db.execute_query(query_slot, values_slot)[0][0]

            # Count current organization for customer_id
            query_count_org = "SELECT COUNT(*) FROM tbl_organization WHERE customer_id = %s"
            values_count_org = (customer_id,)
            current_slot = self.db.execute_query(query_count_org, values_count_org)[0][0]

            return current_slot < total_slot
        except Exception as e:
            print("Error checking organization slot:", e)
            return False

    def get_number_of_users(self, organization_id: str):
        query = "SELECT org_member FROM tbl_organization WHERE organization_id = %s"
        values = (organization_id,)
        try:
            result = self.db.execute_query(query, values)
            return len(result[0][0])
        except Exception as e:
            print("Error getting organization number of members:", e)
            return False

    def get_organization_data(self, organization_id: str):
        query = """SELECT * FROM tbl_organization WHERE organization_id = %s"""
        values = (organization_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            return result
        except Exception as e:
            print("Error querying organization:", e)
    