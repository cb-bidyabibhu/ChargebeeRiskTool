# backend/api/assessment_routes.py
# COMPLETE FILE - Copy this entire content to: backend/api/assessment_routes.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import asyncio
import uuid
from datetime import datetime
import time
import logging
import asyncio
import concurrent.futures

# Import core modules with error handling
try:
    from core.enhanced_risk_assessment import get_enhanced_risk_assessment
    ENHANCED_AVAILABLE = True
    print("✅ Enhanced risk assessment imported successfully")
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️ Enhanced risk assessment not available: {e}")

# Import utilities with error handling
try:
    from utils.data_validator import validate_domain_input
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    # Fallback validation function
    def validate_domain_input(domain: str):
        import re
        if not domain or len(domain) < 3:
            return False, "Domain too short"
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', domain):
            return False, "Invalid domain format"
        return True, "Valid domain"

try:
    from utils.scraper_coordinator import coordinate_scrapers, quick_scraper_test
    COORDINATOR_AVAILABLE = True
except ImportError:
    COORDINATOR_AVAILABLE = False
    def quick_scraper_test(domain: str):
        return {"error": "Scraper coordinator not available", "domain": domain}

# Import existing risk assessment
try:
    import risk_assessment
    STANDARD_AVAILABLE = True
    print("✅ Standard risk assessment imported successfully")
except ImportError as e:
    STANDARD_AVAILABLE = False
    print(f"⚠️ Standard risk assessment not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["assessments"])

# Global storage for assessment progress (in production, use Redis)
assessment_progress = {}

@router.post("/assessment/domain/{domain}")
async def create_domain_assessment(
    domain: str, 
    background_tasks: BackgroundTasks,
    assessment_type: str = "enhanced"
) -> Dict[str, Any]:
    """
    Create a new risk assessment for a domain
    
    - **domain**: The domain to assess (e.g., shopify.com)
    - **assessment_type**: Type of assessment (enhanced, standard)
    """
    
    # Validate domain input
    is_valid, validation_message = validate_domain_input(domain)
    if not is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid domain format: {validation_message}"
        )
    
    # Check if enhanced assessment is available
    if assessment_type == "enhanced" and not ENHANCED_AVAILABLE:
        logger.warning("Enhanced assessment requested but not available, falling back to standard")
        assessment_type = "standard"
    
    # Check if any assessment is available
    if not ENHANCED_AVAILABLE and not STANDARD_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Assessment service not available"
        )
    
    # Generate unique assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Initialize progress tracking
    assessment_progress[assessment_id] = {
        "assessment_id": assessment_id,
        "domain": domain,
        "assessment_type": assessment_type,
        "status": "initializing",
        "progress": 0,
        "started_at": datetime.now().isoformat(),
        "current_step": "Preparing assessment...",
        "estimated_completion": None,
        "result": None
    }
    
    # Start background assessment
    if assessment_type == "enhanced":
        background_tasks.add_task(
            run_enhanced_domain_assessment,
            assessment_id,
            domain
        )
        estimated_time = "3-5 minutes"
    else:
        background_tasks.add_task(
            run_standard_domain_assessment,
            assessment_id,
            domain
        )
        estimated_time = "1-2 minutes"
    
    logger.info(f"Started {assessment_type} assessment for domain: {domain}")
    
    return {
        "assessment_id": assessment_id,
        "domain": domain,
        "assessment_type": assessment_type,
        "status": "started",
        "estimated_completion_time": estimated_time,
        "progress_endpoint": f"/api/v1/assessment/progress/{assessment_id}"
    }

@router.post("/assessment/company/{company_name}")
async def create_company_assessment(
    company_name: str,
    background_tasks: BackgroundTasks,
    assessment_type: str = "standard"
) -> Dict[str, Any]:
    """
    Create a new risk assessment for a company name
    
    - **company_name**: The company name to assess
    - **assessment_type**: Type of assessment (enhanced, standard)
    """
    
    if not company_name or len(company_name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Company name must be at least 2 characters long"
        )
    
    # For enhanced assessment with company name, try to guess domain
    if assessment_type == "enhanced" and ENHANCED_AVAILABLE:
        # Simple domain guessing heuristic
        guessed_domain = f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        return await create_domain_assessment(guessed_domain, background_tasks, "enhanced")
    
    # Check if standard assessment is available
    if not STANDARD_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Assessment service not available"
        )
    
    # Generate unique assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Initialize progress tracking
    assessment_progress[assessment_id] = {
        "assessment_id": assessment_id,
        "company_name": company_name,
        "assessment_type": assessment_type,
        "status": "initializing",
        "progress": 0,
        "started_at": datetime.now().isoformat(),
        "current_step": "Preparing assessment...",
        "estimated_completion": None,
        "result": None
    }
    
    # Start background assessment
    background_tasks.add_task(
        run_standard_company_assessment,
        assessment_id,
        company_name
    )
    
    logger.info(f"Started {assessment_type} assessment for company: {company_name}")
    
    return {
        "assessment_id": assessment_id,
        "company_name": company_name,
        "assessment_type": assessment_type,
        "status": "started",
        "estimated_completion_time": "1-2 minutes",
        "progress_endpoint": f"/api/v1/assessment/progress/{assessment_id}"
    }

@router.get("/assessment/progress/{assessment_id}")
async def get_assessment_progress(assessment_id: str) -> Dict[str, Any]:
    """
    Get the progress of an ongoing assessment
    
    - **assessment_id**: The unique assessment identifier
    """
    
    if assessment_id not in assessment_progress:
        raise HTTPException(
            status_code=404,
            detail=f"Assessment with ID {assessment_id} not found"
        )
    
    progress_data = assessment_progress[assessment_id]
    
    # Add runtime calculation
    if progress_data["status"] in ["running", "initializing"]:
        start_time = datetime.fromisoformat(progress_data["started_at"])
        runtime_seconds = (datetime.now() - start_time).total_seconds()
        progress_data["runtime_seconds"] = round(runtime_seconds, 1)
    
    return progress_data

@router.get("/assessment/result/{assessment_id}")
async def get_assessment_result(assessment_id: str) -> Dict[str, Any]:
    """
    Get the final result of a completed assessment
    
    - **assessment_id**: The unique assessment identifier
    """
    
    if assessment_id not in assessment_progress:
        raise HTTPException(
            status_code=404,
            detail=f"Assessment with ID {assessment_id} not found"
        )
    
    progress_data = assessment_progress[assessment_id]
    
    if progress_data["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Assessment is not completed. Current status: {progress_data['status']}"
        )
    
    if "result" not in progress_data or not progress_data["result"]:
        raise HTTPException(
            status_code=500,
            detail="Assessment completed but result is not available"
        )
    
    return {
        "assessment_id": assessment_id,
        "status": "completed",
        "result": progress_data["result"],
        "completion_time": progress_data.get("completed_at"),
        "total_runtime": progress_data.get("total_runtime_seconds")
    }

# Background task functions
async def run_enhanced_domain_assessment(assessment_id: str, domain: str):
    """Background task for enhanced domain assessment with better error handling"""
    
    try:
        # Update progress: Industry Classification
        assessment_progress[assessment_id].update({
            "status": "running",
            "progress": 10,
            "current_step": "Classifying industry and extracting website content..."
        })
        await asyncio.sleep(1)
        
        # Update progress: Data Collection
        assessment_progress[assessment_id].update({
            "progress": 30,
            "current_step": "Collecting data from multiple sources..."
        })
        await asyncio.sleep(2)
        
        # Update progress: Security Analysis
        assessment_progress[assessment_id].update({
            "progress": 50,
            "current_step": "Running security and reputation checks..."
        })
        await asyncio.sleep(2)
        
        # Update progress: Business Intelligence
        assessment_progress[assessment_id].update({
            "progress": 70,
            "current_step": "Analyzing business presence and traffic data..."
        })
        await asyncio.sleep(1)
        
        # Update progress: AI Assessment
        assessment_progress[assessment_id].update({
            "progress": 85,
            "current_step": "Running AI-powered risk assessment..."
        })
        
        # Run the enhanced assessment in a thread pool to avoid blocking
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                get_enhanced_risk_assessment, 
                domain
            )
        
        # Store the result if successful
        if STANDARD_AVAILABLE and "error" not in result:
            company_name = result.get("company_name", domain.split('.')[0].capitalize())
            risk_assessment.store_risk_assessment(company_name, result)
        
        # Mark as completed
        assessment_progress[assessment_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "Assessment completed successfully",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "total_runtime_seconds": (
                datetime.now() - datetime.fromisoformat(assessment_progress[assessment_id]["started_at"])
            ).total_seconds()
        })
        
        logger.info(f"Enhanced assessment completed successfully for domain: {domain}")
        
    except Exception as e:
        logger.error(f"Enhanced assessment failed for {domain}: {e}")
        assessment_progress[assessment_id].update({
            "status": "failed",
            "progress": 0,
            "current_step": f"Assessment failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })
async def run_standard_domain_assessment(assessment_id: str, domain: str):
    """Background task for standard domain assessment with domain input"""
    
    try:
        # Extract company name from domain
        company_name = domain.split('.')[0].capitalize()
        
        # Update progress
        assessment_progress[assessment_id].update({
            "status": "running",
            "progress": 30,
            "current_step": f"Running standard assessment for {company_name}..."
        })
        await asyncio.sleep(2)
        
        # Run standard assessment
        result = risk_assessment.get_risk_assessment(company_name)
        
        # Add domain information to result
        result["domain"] = domain
        result["assessment_type"] = "standard_from_domain"
        
        # Store the result
        risk_assessment.store_risk_assessment(company_name, result)
        
        # Mark as completed
        assessment_progress[assessment_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "Assessment completed successfully",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "total_runtime_seconds": (
                datetime.now() - datetime.fromisoformat(assessment_progress[assessment_id]["started_at"])
            ).total_seconds()
        })
        
    except Exception as e:
        logger.error(f"Standard assessment failed for {domain}: {e}")
        assessment_progress[assessment_id].update({
            "status": "failed",
            "progress": 0,
            "current_step": f"Assessment failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })

async def run_standard_company_assessment(assessment_id: str, company_name: str):
    """Background task for standard company assessment"""
    
    try:
        # Update progress
        assessment_progress[assessment_id].update({
            "status": "running",
            "progress": 50,
            "current_step": f"Running assessment for {company_name}..."
        })
        await asyncio.sleep(2)
        
        # Run standard assessment
        result = risk_assessment.get_risk_assessment(company_name)
        
        # Store the result
        risk_assessment.store_risk_assessment(company_name, result)
        
        # Mark as completed
        assessment_progress[assessment_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "Assessment completed successfully",
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "total_runtime_seconds": (
                datetime.now() - datetime.fromisoformat(assessment_progress[assessment_id]["started_at"])
            ).total_seconds()
        })
        
    except Exception as e:
        logger.error(f"Standard assessment failed for {company_name}: {e}")
        assessment_progress[assessment_id].update({
            "status": "failed",
            "progress": 0,
            "current_step": f"Assessment failed: {str(e)}",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })

@router.post("/assessment/test/scrapers/{domain}")
async def test_scrapers_for_domain(domain: str) -> Dict[str, Any]:
    """Test scrapers for a specific domain"""
    
    # Validate domain
    is_valid, validation_message = validate_domain_input(domain)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain format: {validation_message}"
        )
    
    if not COORDINATOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Scraper coordinator not available"
        )
    
    try:
        # Run quick scraper test
        result = quick_scraper_test(domain)
        
        return {
            "domain": domain,
            "test_status": "completed",
            "scrapers_tested": len(result),
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scraper test failed for {domain}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraper test failed: {str(e)}"
        )

@router.get("/assessment/health")
async def assessment_health_check() -> Dict[str, Any]:
    """Health check for assessment service"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "enhanced_assessment": ENHANCED_AVAILABLE,
            "standard_assessment": STANDARD_AVAILABLE,
            "data_validation": VALIDATOR_AVAILABLE,
            "scraper_coordination": COORDINATOR_AVAILABLE
        },
        "active_assessments": len([
            a for a in assessment_progress.values() 
            if a.get("status") in ["initializing", "running"]
        ]),
        "total_assessments": len(assessment_progress)
    }