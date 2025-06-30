# backend/config/settings.py
# COMPLETE FILE - Copy this entire content to: backend/config/settings.py

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # API Configuration
    API_TITLE: str = "Chargebee KYB Risk Assessment API"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "Enhanced Know Your Business risk assessment with real-time data collection"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # External API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Assessment Configuration
    DEFAULT_ASSESSMENT_TYPE: str = "enhanced"
    ASSESSMENT_TIMEOUT_SECONDS: int = int(os.getenv("ASSESSMENT_TIMEOUT_SECONDS", "300"))  # 5 minutes
    MAX_CONCURRENT_ASSESSMENTS: int = int(os.getenv("MAX_CONCURRENT_ASSESSMENTS", "10"))
    
    # Scraper Configuration
    SCRAPER_TIMEOUT_SECONDS: int = int(os.getenv("SCRAPER_TIMEOUT_SECONDS", "30"))
    SCRAPER_MAX_RETRIES: int = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    SCRAPER_DELAY_SECONDS: float = float(os.getenv("SCRAPER_DELAY_SECONDS", "1.0"))
    MAX_CONCURRENT_SCRAPERS: int = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "3"))
    
    # Risk Assessment Weights
    RISK_WEIGHTS: Dict[str, float] = {
        "reputation_risk": 0.25,
        "financial_risk": 0.25,
        "technology_risk": 0.20,
        "business_risk": 0.15,
        "legal_compliance_risk": 0.15
    }
    
    # Risk Level Thresholds
    RISK_THRESHOLDS: Dict[str, float] = {
        "low_risk_threshold": 7.0,
        "medium_risk_threshold": 4.0,
        "high_risk_threshold": 0.0
    }
    
    # Industry Classification
    SUPPORTED_INDUSTRIES: List[str] = [
        "software_saas",
        "ecommerce_retail",
        "fintech_financial",
        "media_social",
        "healthcare",
        "manufacturing",
        "professional_services",
        "other"
    ]
    
    # Geopolitical Risk Countries
    RISKY_COUNTRIES: List[str] = [
        "CU", "IR", "KP", "SY", "RU", "BY", "MM", "VE", "YE", "ZW",
        "SD", "SS", "LY", "SO", "CF", "CD", "UA"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://chargebee-kyb.vercel.app",  # Add your frontend URL
    ]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))  # 1 hour
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    # Data Validation
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.5"))
    REQUIRE_DOMAIN_VALIDATION: bool = os.getenv("REQUIRE_DOMAIN_VALIDATION", "True").lower() == "true"
    
    # Feature Flags
    ENABLE_ENHANCED_ASSESSMENT: bool = os.getenv("ENABLE_ENHANCED_ASSESSMENT", "True").lower() == "true"
    ENABLE_SCRAPER_COORDINATION: bool = os.getenv("ENABLE_SCRAPER_COORDINATION", "True").lower() == "true"
    ENABLE_CROSS_VALIDATION: bool = os.getenv("ENABLE_CROSS_VALIDATION", "True").lower() == "true"
    ENABLE_INDUSTRY_CLASSIFICATION: bool = os.getenv("ENABLE_INDUSTRY_CLASSIFICATION", "True").lower() == "true"
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Monitoring and Health Checks
    HEALTH_CHECK_INTERVAL_SECONDS: int = int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "300"))  # 5 minutes
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, bool]:
        """Validate that required configuration is present"""
        validation_results = {
            "google_api_key": bool(cls.GOOGLE_API_KEY),
            "supabase_url": bool(cls.SUPABASE_URL),
            "supabase_key": bool(cls.SUPABASE_KEY),
            "secret_key": cls.SECRET_KEY != "your-secret-key-change-in-production",
            "risk_weights_sum": abs(sum(cls.RISK_WEIGHTS.values()) - 1.0) < 0.01  # Should sum to 1.0
        }
        
        return validation_results
    
    @classmethod
    def get_scraper_config(cls) -> Dict[str, any]:
        """Get scraper-specific configuration"""
        return {
            "timeout_seconds": cls.SCRAPER_TIMEOUT_SECONDS,
            "max_retries": cls.SCRAPER_MAX_RETRIES,
            "delay_seconds": cls.SCRAPER_DELAY_SECONDS,
            "max_concurrent": cls.MAX_CONCURRENT_SCRAPERS,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        }
    
    @classmethod
    def get_ai_config(cls) -> Dict[str, any]:
        """Get AI-specific configuration"""
        return {
            "model_name": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 8192,
            "timeout_seconds": 60,
            "retry_attempts": 3
        }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, str]:
        """Get database configuration"""
        return {
            "url": cls.SUPABASE_URL,
            "key": cls.SUPABASE_KEY,
            "table_name": "risk_assessments",
            "timeout_seconds": 30
        }
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, any]:
        """Get CORS configuration"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"]
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def get_feature_flags(cls) -> Dict[str, bool]:
        """Get all feature flags"""
        return {
            "enhanced_assessment": cls.ENABLE_ENHANCED_ASSESSMENT,
            "scraper_coordination": cls.ENABLE_SCRAPER_COORDINATION,
            "cross_validation": cls.ENABLE_CROSS_VALIDATION,
            "industry_classification": cls.ENABLE_INDUSTRY_CLASSIFICATION,
            "caching": cls.ENABLE_CACHING,
            "metrics": cls.ENABLE_METRICS
        }

# Create global settings instance
settings = Settings()

# Configuration validation
def validate_environment():
    """Validate environment configuration on startup"""
    validation_results = settings.validate_configuration()
    
    missing_config = [key for key, valid in validation_results.items() if not valid]
    
    if missing_config:
        print("⚠️ Configuration validation warnings:")
        for config in missing_config:
            print(f"  - {config}: Not properly configured")
    
    # Critical configurations
    critical_missing = []
    if not settings.GOOGLE_API_KEY:
        critical_missing.append("GOOGLE_API_KEY")
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        critical_missing.append("Supabase credentials")
    
    if critical_missing:
        print("❌ Critical configuration missing:")
        for config in critical_missing:
            print(f"  - {config}")
        print("Some features may not work properly.")
    else:
        print("✅ Core configuration validated successfully")
    
    return len(critical_missing) == 0

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    CORS_ORIGINS = ["*"]  # Allow all origins in development

class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    REQUIRE_DOMAIN_VALIDATION = True
    RATE_LIMIT_REQUESTS = 50  # Stricter rate limiting

class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG = True
    LOG_LEVEL = "WARNING"
    ASSESSMENT_TIMEOUT_SECONDS = 60  # Faster timeouts for tests
    SCRAPER_TIMEOUT_SECONDS = 10

def get_settings() -> Settings:
    """Get environment-appropriate settings"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Export the appropriate settings
settings = get_settings()

if __name__ == "__main__":
    # Test configuration
    print("🔧 KYB System Configuration")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")
    print(f"API Version: {settings.API_VERSION}")
    
    print("\n📊 Feature Flags:")
    for feature, enabled in settings.get_feature_flags().items():
        print(f"  {feature}: {'✅' if enabled else '❌'}")
    
    print("\n🔍 Configuration Validation:")
    validate_environment()