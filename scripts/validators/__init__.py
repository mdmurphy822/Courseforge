"""
Validators Module for Slideforge

Three-level validation system for presentation content:
1. Structure Validator - Data structure integrity
2. Schema Validator - JSON schema compliance
3. Semantic Validator - Quality and completeness
"""

from .structure_validator import (
    StructureValidator,
    StructureValidationResult,
    StructureError
)

from .schema_validator import (
    SchemaValidator,
    SchemaValidationResult,
    SchemaError
)

from .semantic_validator import (
    SemanticValidator,
    SemanticValidationResult,
    QualityIssue,
    QualityMetrics
)

__all__ = [
    # Structure validation
    "StructureValidator",
    "StructureValidationResult",
    "StructureError",
    # Schema validation
    "SchemaValidator",
    "SchemaValidationResult",
    "SchemaError",
    # Semantic validation
    "SemanticValidator",
    "SemanticValidationResult",
    "QualityIssue",
    "QualityMetrics"
]

__version__ = "1.0.0"
