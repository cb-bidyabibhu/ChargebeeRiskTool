# backend/database/supabase_client.py
# COMPLETE FILE - Enhanced Supabase client for KYB system

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Enhanced Supabase client for KYB risk assessments"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
        self.table_name = "risk_assessments"
        
        print(f"✅ Supabase client initialized for table: {self.table_name}")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Simple query to test connection
            response = self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
    
    async def store_assessment(self, company_name: str, assessment_data: Dict, domain: Optional[str] = None) -> str:
        """Store risk assessment in database"""
        try:
            # Prepare the data
            data_to_store = {
                "company_name": company_name,
                "risk_assessment_data": assessment_data,
                "created_at": datetime.now().isoformat(),
                "assessment_type": assessment_data.get("assessment_type", "standard")
            }
            
            # Add domain if provided
            if domain:
                data_to_store["domain"] = domain
            
            # Insert into database
            response = self.client.table(self.table_name).insert(data_to_store).execute()
            
            if response.data and len(response.data) > 0:
                assessment_id = response.data[0]["id"]
                print(f"✅ Assessment stored with ID: {assessment_id}")
                return str(assessment_id)
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            print(f"❌ Failed to store assessment for {company_name}: {e}")
            raise Exception(f"Database storage failed: {str(e)}")
    
    async def get_latest_assessment(self, company_name: str) -> Optional[Dict]:
        """Get the latest assessment for a company"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("company_name", company_name)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Failed to fetch latest assessment for {company_name}: {e}")
            raise Exception(f"Failed to fetch assessment: {str(e)}")
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Dict]:
        """Get assessment by ID"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", assessment_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Failed to fetch assessment {assessment_id}: {e}")
            raise Exception(f"Failed to fetch assessment: {str(e)}")
    
    async def get_all_assessments(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get all assessments with pagination"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return response.data if response.data else []
                
        except Exception as e:
            print(f"❌ Failed to fetch all assessments: {e}")
            raise Exception(f"Failed to fetch assessments: {str(e)}")
    
    async def get_company_assessments(self, company_name: str) -> List[Dict]:
        """Get all assessments for a specific company"""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("company_name", company_name)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
                
        except Exception as e:
            print(f"❌ Failed to fetch assessments for {company_name}: {e}")
            raise Exception(f"Failed to fetch company assessments: {str(e)}")
    
    async def delete_assessment(self, assessment_id: str) -> bool:
        """Delete an assessment"""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("id", assessment_id)\
                .execute()
            
            return True
                
        except Exception as e:
            print(f"❌ Failed to delete assessment {assessment_id}: {e}")
            return False
    
    async def update_assessment(self, assessment_id: str, updates: Dict) -> bool:
        """Update an existing assessment"""
        try:
            # Add updated timestamp
            updates["updated_at"] = datetime.now().isoformat()
            
            response = self.client.table(self.table_name)\
                .update(updates)\
                .eq("id", assessment_id)\
                .execute()
            
            return True
                
        except Exception as e:
            print(f"❌ Failed to update assessment {assessment_id}: {e}")
            return False
    
    async def search_assessments(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Search assessments by company name or domain"""
        try:
            # Search in company_name field
            response = self.client.table(self.table_name)\
                .select("*")\
                .ilike("company_name", f"%{search_term}%")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            results = response.data if response.data else []
            
            # Also search in domain field if it exists
            try:
                domain_response = self.client.table(self.table_name)\
                    .select("*")\
                    .ilike("domain", f"%{search_term}%")\
                    .order("created_at", desc=True)\
                    .limit(limit)\
                    .execute()
                
                if domain_response.data:
                    # Combine results and remove duplicates
                    existing_ids = {item["id"] for item in results}
                    for item in domain_response.data:
                        if item["id"] not in existing_ids:
                            results.append(item)
            except:
                pass  # Domain field might not exist in older records
            
            return results[:limit]  # Ensure we don't exceed the limit
                
        except Exception as e:
            print(f"❌ Failed to search assessments for '{search_term}': {e}")
            raise Exception(f"Failed to search assessments: {str(e)}")
    
    async def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk assessment statistics"""
        try:
            # Get all assessments
            all_assessments = await self.get_all_assessments(limit=1000)
            
            stats = {
                "total_assessments": len(all_assessments),
                "risk_distribution": {"Low": 0, "Medium": 0, "High": 0, "Unknown": 0},
                "assessment_types": {},
                "recent_assessments": len([a for a in all_assessments if self._is_recent(a["created_at"])]),
                "average_score": 0.0,
                "score_distribution": {"0-3": 0, "3-5": 0, "5-7": 0, "7-10": 0}
            }
            
            total_score = 0
            valid_scores = 0
            
            for assessment in all_assessments:
                # Risk level distribution
                risk_level = assessment.get("risk_assessment_data", {}).get("risk_level", "Unknown")
                stats["risk_distribution"][risk_level] = stats["risk_distribution"].get(risk_level, 0) + 1
                
                # Assessment type distribution
                assessment_type = assessment.get("assessment_type", "standard")
                stats["assessment_types"][assessment_type] = stats["assessment_types"].get(assessment_type, 0) + 1
                
                # Score statistics
                score = assessment.get("risk_assessment_data", {}).get("weighted_total_score")
                if score is not None:
                    total_score += score
                    valid_scores += 1
                    
                    # Score distribution
                    if score < 3:
                        stats["score_distribution"]["0-3"] += 1
                    elif score < 5:
                        stats["score_distribution"]["3-5"] += 1
                    elif score < 7:
                        stats["score_distribution"]["5-7"] += 1
                    else:
                        stats["score_distribution"]["7-10"] += 1
            
            # Calculate average score
            if valid_scores > 0:
                stats["average_score"] = round(total_score / valid_scores, 2)
            
            return stats
                
        except Exception as e:
            print(f"❌ Failed to get risk statistics: {e}")
            raise Exception(f"Failed to get statistics: {str(e)}")
    
    def _is_recent(self, created_at_str: str, days: int = 7) -> bool:
        """Check if assessment is recent (within specified days)"""
        try:
            from datetime import datetime, timedelta
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            cutoff_date = datetime.now() - timedelta(days=days)
            return created_at > cutoff_date
        except:
            return False
    
    async def cleanup_old_assessments(self, days_to_keep: int = 90) -> int:
        """Clean up assessments older than specified days"""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Get old assessments
            response = self.client.table(self.table_name)\
                .select("id")\
                .lt("created_at", cutoff_date)\
                .execute()
            
            old_assessments = response.data if response.data else []
            
            if not old_assessments:
                return 0
            
            # Delete old assessments
            old_ids = [a["id"] for a in old_assessments]
            delete_response = self.client.table(self.table_name)\
                .delete()\
                .in_("id", old_ids)\
                .execute()
            
            print(f"✅ Cleaned up {len(old_ids)} old assessments")
            return len(old_ids)
                
        except Exception as e:
            print(f"❌ Failed to cleanup old assessments: {e}")
            return 0

# Compatibility functions for backward compatibility
def store_risk_assessment(company_name: str, data: dict):
    """Legacy function for storing assessments"""
    import asyncio
    client = SupabaseClient()
    return asyncio.run(client.store_assessment(company_name, data))

def get_assessment_history(company_name: str) -> list:
    """Legacy function for getting assessment history"""
    import asyncio
    client = SupabaseClient()
    return asyncio.run(client.get_company_assessments(company_name))

def delete_assessment(assessment_id: str) -> bool:
    """Legacy function for deleting assessments"""
    import asyncio
    client = SupabaseClient()
    return asyncio.run(client.delete_assessment(assessment_id))

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_client():
        """Test the Supabase client"""
        try:
            client = SupabaseClient()
            
            # Test connection
            connected = await client.test_connection()
            print(f"Connection test: {'✅ Connected' if connected else '❌ Failed'}")
            
            # Get recent assessments
            assessments = await client.get_all_assessments(limit=5)
            print(f"Recent assessments: {len(assessments)} found")
            
            # Get statistics
            stats = await client.get_risk_statistics()
            print(f"Statistics: {stats}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    asyncio.run(test_client())