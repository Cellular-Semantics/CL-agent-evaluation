from __future__ import annotations
from datetime import datetime, date
from enum import Enum

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, ConfigDict, Field, field_validator
import re
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
    pass


class GOBiologicalProcessType(str):

    dummy = "dummy"


class GOCellComponentType(str):

    dummy = "dummy"


class GOMolecularFunctionType(str):

    dummy = "dummy"


class NullDataOptions(str, Enum):

    UNSPECIFIED_METHOD_OF_ADMINISTRATION = "UNSPECIFIED_METHOD_OF_ADMINISTRATION"

    NOT_APPLICABLE = "NOT_APPLICABLE"

    NOT_MENTIONED = "NOT_MENTIONED"


class ExtractionResult(ConfiguredBaseModel):
    """
    A result of extracting knowledge on text
    """

    input_id: Optional[str] = Field(None)
    input_title: Optional[str] = Field(None)
    input_text: Optional[str] = Field(None)
    raw_completion_output: Optional[str] = Field(None)
    prompt: Optional[str] = Field(None)
    extracted_object: Optional[Any] = Field(
        None, description="""The complex objects extracted from the text"""
    )
    named_entities: Optional[List[Any]] = Field(
        default_factory=list, description="""Named entities extracted from the text"""
    )


class NamedEntity(ConfiguredBaseModel):

    id: str = Field(..., description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(
        None, description="""The label (name) of the named thing"""
    )


class BiologicalProcess(NamedEntity):

    id: str = Field(..., description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(
        None, description="""The label (name) of the named thing"""
    )


class CellularComponent(NamedEntity):

    id: str = Field(..., description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(
        None, description="""The label (name) of the named thing"""
    )


class MolecularFunction(NamedEntity):

    id: str = Field(..., description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(
        None, description="""The label (name) of the named thing"""
    )


class CompoundExpression(ConfiguredBaseModel):

    None


class Triple(CompoundExpression):
    """
    Abstract parent for Relation Extraction tasks
    """

    subject: Optional[str] = Field(None)
    predicate: Optional[str] = Field(None)
    object: Optional[str] = Field(None)
    qualifier: Optional[str] = Field(
        None,
        description="""A qualifier for the statements, e.g. \"NOT\" for negation""",
    )
    subject_qualifier: Optional[str] = Field(
        None,
        description="""An optional qualifier or modifier for the subject of the statement, e.g. \"high dose\" or \"intravenously administered\"""",
    )
    object_qualifier: Optional[str] = Field(
        None,
        description="""An optional qualifier or modifier for the object of the statement, e.g. \"severe\" or \"with additional complications\"""",
    )


class TextWithTriples(ConfiguredBaseModel):
    """
    A text containing one or more relations of the Triple type.
    """

    publication: Optional[Publication] = Field(None)
    triples: Optional[List[Triple]] = Field(default_factory=list)


class TextWithEntity(ConfiguredBaseModel):
    """
    A text containing one or more instances of a single type of entity.
    """

    publication: Optional[Publication] = Field(None)
    entities: Optional[List[str]] = Field(default_factory=list)


class Document(TextWithEntity):
    """
    A document that contains biological or biomedical concepts.
    """

    biologicalprocesses: Optional[List[str]] = Field(
        default_factory=list,
        description="""One or more biological processes, as defined by the Gene Ontology.""",
    )
    cellularcomponents: Optional[List[str]] = Field(
        default_factory=list,
        description="""One or more cellular components, as defined by the Gene Ontology.""",
    )
    molecularfunctions: Optional[List[str]] = Field(
        default_factory=list,
        description="""One or more molecular functions, as defined by the Gene Ontology.""",
    )
    publication: Optional[Publication] = Field(None)
    entities: Optional[List[str]] = Field(default_factory=list)


class RelationshipType(NamedEntity):

    id: str = Field(..., description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(
        None, description="""The label (name) of the named thing"""
    )


class Publication(ConfiguredBaseModel):

    id: Optional[str] = Field(None, description="""The publication identifier""")
    title: Optional[str] = Field(None, description="""The title of the publication""")
    abstract: Optional[str] = Field(
        None, description="""The abstract of the publication"""
    )
    combined_text: Optional[str] = Field(None)
    full_text: Optional[str] = Field(
        None, description="""The full text of the publication"""
    )


class AnnotatorResult(ConfiguredBaseModel):

    subject_text: Optional[str] = Field(None)
    object_id: Optional[str] = Field(None)
    object_text: Optional[str] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExtractionResult.model_rebuild()
NamedEntity.model_rebuild()
BiologicalProcess.model_rebuild()
CellularComponent.model_rebuild()
MolecularFunction.model_rebuild()
CompoundExpression.model_rebuild()
Triple.model_rebuild()
TextWithTriples.model_rebuild()
TextWithEntity.model_rebuild()
Document.model_rebuild()
RelationshipType.model_rebuild()
Publication.model_rebuild()
AnnotatorResult.model_rebuild()
