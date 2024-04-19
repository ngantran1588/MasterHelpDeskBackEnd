from ..const import const
from . import connector
from ..models.organization import Organization as Org
from ..models.auth import Auth 

class Organization:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()
        self.org = Org()
        self.auth = Auth()

    def add_organization(self, name: str, contact_phone: str, contact_email: str, description: str, username: str) -> bool:
        organization_id = self.auth.generate_id(name)
        organization_status = const.STATUS_ACTIVE

        org_member = []

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
            organization_info = result[0]
            organization = {
                "name": organization_info[0],
                "organization_status": organization_info[1],
                "description": organization_info[2]
            }
               
            return organization
        except Exception as e:
            print("Error querying organization:", e)

    def get_all_organizations(self, username: str):
        query = """SELECT organization_id, name, organization_status, description FROM tbl_organization WHERE %s = ANY(org_member)"""
        values = (username,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            organizations = []
            for org_info in result:
                organization = {
                    "organization_id": org_info[0],
                    "name": org_info[1],
                    "organization_status": org_info[2],
                    "description": org_info[3]
                }
                organizations.append(organization)

            return organizations
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

    def add_user(self, organization_id: str, new_user: str) -> bool:
        # Query to fetch the current member list of the organization
        select_query = "SELECT org_member FROM tbl_organization WHERE organization_id = %s"
        select_values = (organization_id,)
        
        try:
            # Fetch the current member list from the database
            current_members = self.db.execute_query(select_query, select_values)
            if current_members:
                current_member_list = current_members[0][0]
                
                # Check if the new user is already a member of the organization
                if new_user in current_member_list:
                    print(f"User '{new_user}' already exists in the organization.")
                    return False
                
                # Add the new user to the organization's member list
                current_member_list.append(new_user)

                # Update the organization's member list in the database
                update_query = "UPDATE tbl_organization SET org_member = %s WHERE organization_id = %s"
                update_values = (current_member_list, organization_id)
                self.db.execute_query(update_query, update_values)

                msg = "Users added to organization successfully!"
                return True, msg
            else:
                msg = "Organization not found."
                return False, msg
        except Exception as e:
            msg = f"Error adding user(s) to organization: {e}"
            return False, msg


    def remove_user(self, organization_id: str, remove_username: str) -> bool:
        try:
            # Fetch the current member list of the organization from the database
            select_query = "SELECT org_member FROM tbl_organization WHERE organization_id = %s"
            select_values = (organization_id,)
            result = self.db.execute_query(select_query, select_values)
            
            if result:
                org_member_list = result[0][0]
                creator_username = org_member_list[0]
                
                # Check if the user to be removed is the creator of the organization
                if remove_username == creator_username:
                    msg = "Cannot remove the creator of the organization."
                    return False, msg
                
                # Check if the member list will have at least one member after removal
                if len(org_member_list) == 1:
                    msg = "Cannot remove the last member of the organization."
                    return False, msg
                
                # Check if the user to be removed is in the member list
                if remove_username not in org_member_list:
                    msg = f"User '{remove_username}' is not a member of the organization."
                    return False, msg
                
                # Remove the user from the member list
                org_member_list.remove(remove_username)
                
                # Update the member list in the database
                update_query = "UPDATE tbl_organization SET org_member = %s WHERE organization_id = %s"
                update_values = (org_member_list, organization_id)
                self.db.execute_query(update_query, update_values)
                
                msg = "User removed from organization successfully!"
                return True, msg
            else:
                msg = "Organization not found."
                return False, msg
        except Exception as e:
            msg = f"Error removing user from organization:{e}"
            return False, msg


    def check_organization_name_exist(self, name: str) -> bool:
        query = "SELECT COUNT(*) FROM tbl_organization WHERE name = %s"
        values = (name,)
        try:
            result = self.db.execute_query(query, values)
            return result[0][0] > 0
        except Exception as e:
            print("Error checking organization name existence:", e)
            return False
    def get_remain_slot(self, username: str):
        try:
            total_slot = self.get_total_slot(username)
            if not total_slot:
                print("Error checking organization slot:", e)
                return False
            
            current_slot = self.get_current_slot(username)
            if not current_slot:
                print("Error checking organization slot:", e)
                return False
            remain_slot = total_slot - current_slot
            return remain_slot
        except Exception as e:
            print("Error checking organization slot:", e)
            return False

    def check_organization_slot(self, username: str):
        try:
            total_slot = self.get_total_slot(username)
            if not total_slot:
                print("Error checking organization slot:", e)
                return False
            
            current_slot = self.get_current_slot(username)
            if not current_slot:
                print("Error checking organization slot:", e)
                return False
            
            return current_slot < total_slot
        except Exception as e:
            print("Error checking organization slot:", e)
            return False

    def get_current_slot(self, username: str):
        try:
            # Get customer_id from tbl_customer using username
            query_customer_id = "SELECT customer_id FROM tbl_customer WHERE username = %s"
            values_customer_id = (username,)
            customer_id = self.db.execute_query(query_customer_id, values_customer_id)[0][0]

            # Count current organization for customer_id
            query_count_org = "SELECT COUNT(*) FROM tbl_organization WHERE customer_id = %s"
            values_count_org = (customer_id,)
            current_slot = self.db.execute_query(query_count_org, values_count_org)[0][0]

            return current_slot 
        except Exception as e:
            print("Error checking current organization slot:", e)
            return False
        
    def get_total_slot(self, username: str):
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
            
            return total_slot 
        except Exception as e:
            print("Error checking total organization slot:", e)
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
        query = """SELECT name,customer_id,organization_status,subscription_id,description,contact_phone,contact_email,org_member FROM tbl_organization WHERE organization_id = %s"""
        values = (organization_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            organizations = []
            for org_info in result:
                # Extract organization information and create a dictionary
                organization = {
                    "name": org_info[0],
                    "customer_id": org_info[1],
                    "organization_status": org_info[2],
                    "subscription_id": org_info[3],
                    "description": org_info[4],
                    "contact_phone": org_info[5],
                    "contact_email": org_info[6],
                    "org_member": org_info[7]
                }
                organizations.append(organization)

            return organizations
        except Exception as e:
            print("Error querying organization:", e)

    def delete_organization(self, organization_id: str) -> bool:
        query = """DELETE FROM tbl_organization WHERE organization_id = %s"""
        try:
            self.db.execute_query(query, (organization_id,))
            print("Organization deleted successfully!")
            return True
        except Exception as e:
            print("Error deleting organization:", e)
            return False

    def get_user_organization(self, organization_id: str):
        query = """SELECT org_member FROM tbl_organization WHERE organization_id = %s"""
        values = (organization_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query organization successful!")
            if len(result) == 0:
                return None
            
            user_roles = []
            for org_info in result:
                org_members = org_info[0]  # Assuming org_member is a list of usernames
                for username in org_members:
                    roles = self.get_user_roles(username)
                    user_roles.append({"username": username, "roles": roles})

            return user_roles
        except Exception as e:
            print("Error getting user organization:", e)

    def get_user_roles(self, username: str):
        query = """
            SELECT DISTINCT r.role_name 
            FROM tbl_customer c 
            JOIN tbl_role r ON r.role_id = ANY(c.role_id) 
            WHERE c.username = %s
        """
        values = (username,)

        try:
            result = self.db.execute_query(query, values)
            if len(result) == 0:
                return None
            
            # Extract role names from the result
            role_names = [role[0] for role in result]
            return role_names
        except Exception as e:
            print("Error getting user roles:", e)
