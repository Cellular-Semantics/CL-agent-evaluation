from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'CL',
     'default_range': 'string',
     'description': 'A template for Cell Type Processes',
     'id': 'https://w3id.org/ontogpt/cell_processes',
     'imports': ['linkml:types', 'core'],
     'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
     'name': 'cell-processes-template',
     'prefixes': {'BFO': {'prefix_prefix': 'BFO',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/BFO_'},
                  'CL': {'prefix_prefix': 'CL',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/CL_'},
                  'GO': {'prefix_prefix': 'GO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/GO_'},
                  'RO': {'prefix_prefix': 'RO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/RO_'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'rdf': {'prefix_prefix': 'rdf',
                          'prefix_reference': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'}},
     'source_file': 'templates/cell_process.yaml',
     'title': 'Cell Type Processes Template'} )

class NullDataOptions(str, Enum):
    UNSPECIFIED_METHOD_OF_ADMINISTRATION = "UNSPECIFIED_METHOD_OF_ADMINISTRATION"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_MENTIONED = "NOT_MENTIONED"



class ExtractionResult(ConfiguredBaseModel):
    """
    A result of extracting knowledge on text
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core'})

    input_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'input_id', 'domain_of': ['ExtractionResult']} })
    input_title: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'input_title', 'domain_of': ['ExtractionResult']} })
    input_text: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'input_text', 'domain_of': ['ExtractionResult']} })
    raw_completion_output: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'raw_completion_output', 'domain_of': ['ExtractionResult']} })
    prompt: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'prompt', 'domain_of': ['ExtractionResult']} })
    extracted_object: Optional[Any] = Field(default=None, description="""The complex objects extracted from the text""", json_schema_extra = { "linkml_meta": {'alias': 'extracted_object', 'domain_of': ['ExtractionResult']} })
    named_entities: Optional[list[Any]] = Field(default=None, description="""Named entities extracted from the text""", json_schema_extra = { "linkml_meta": {'alias': 'named_entities', 'domain_of': ['ExtractionResult']} })


class NamedEntity(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'http://w3id.org/ontogpt/core'})

    id: str = Field(default=..., description="""A unique identifier for the named entity""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['this is populated during the grounding and normalization step'],
         'domain_of': ['NamedEntity', 'Publication']} })
    label: Optional[str] = Field(default=None, description="""The label (name) of the named thing""", json_schema_extra = { "linkml_meta": {'alias': 'label',
         'aliases': ['name'],
         'annotations': {'owl': {'tag': 'owl',
                                 'value': 'AnnotationProperty, AnnotationAssertion'}},
         'domain_of': ['NamedEntity',
                       'CellType',
                       'BiologicalProcess',
                       'CellularComponent'],
         'slot_uri': 'rdfs:label'} })
    original_spans: Optional[list[str]] = Field(default=None, description="""The coordinates of the original text span from which the named entity was extracted, inclusive. For example, \"10:25\" means the span starting from the 10th character and ending with the 25th character. The first character in the text has index 0. Newlines are treated as single characters. Multivalued as there may be multiple spans for a single text.""", json_schema_extra = { "linkml_meta": {'alias': 'original_spans',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['This is determined during grounding and normalization',
                      'But is based on the full input text'],
         'domain_of': ['NamedEntity']} })

    @field_validator('original_spans')
    def pattern_original_spans(cls, v):
        pattern=re.compile(r"^\d+:\d+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid original_spans format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid original_spans format: {v}"
            raise ValueError(err_msg)
        return v


class CompoundExpression(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'http://w3id.org/ontogpt/core'})

    pass


class Triple(CompoundExpression):
    """
    Abstract parent for Relation Extraction tasks
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True, 'from_schema': 'http://w3id.org/ontogpt/core'})

    subject: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'subject', 'domain_of': ['Triple']} })
    predicate: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'predicate', 'domain_of': ['Triple']} })
    object: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'object', 'domain_of': ['Triple']} })
    qualifier: Optional[str] = Field(default=None, description="""A qualifier for the statements, e.g. \"NOT\" for negation""", json_schema_extra = { "linkml_meta": {'alias': 'qualifier', 'domain_of': ['Triple']} })
    subject_qualifier: Optional[str] = Field(default=None, description="""An optional qualifier or modifier for the subject of the statement, e.g. \"high dose\" or \"intravenously administered\"""", json_schema_extra = { "linkml_meta": {'alias': 'subject_qualifier', 'domain_of': ['Triple']} })
    object_qualifier: Optional[str] = Field(default=None, description="""An optional qualifier or modifier for the object of the statement, e.g. \"severe\" or \"with additional complications\"""", json_schema_extra = { "linkml_meta": {'alias': 'object_qualifier', 'domain_of': ['Triple']} })


class TextWithTriples(ConfiguredBaseModel):
    """
    A text containing one or more relations of the Triple type.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core'})

    publication: Optional[Publication] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'publication',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'domain_of': ['TextWithTriples', 'TextWithEntity']} })
    triples: Optional[list[Triple]] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'triples', 'domain_of': ['TextWithTriples']} })


class TextWithEntity(ConfiguredBaseModel):
    """
    A text containing one or more instances of a single type of entity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core'})

    publication: Optional[Publication] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'publication',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'domain_of': ['TextWithTriples', 'TextWithEntity']} })
    entities: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'entities', 'domain_of': ['TextWithEntity']} })


class RelationshipType(NamedEntity):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core',
         'id_prefixes': ['RO', 'biolink']})

    id: str = Field(default=..., description="""A unique identifier for the named entity""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['this is populated during the grounding and normalization step'],
         'domain_of': ['NamedEntity', 'Publication']} })
    label: Optional[str] = Field(default=None, description="""The label (name) of the named thing""", json_schema_extra = { "linkml_meta": {'alias': 'label',
         'aliases': ['name'],
         'annotations': {'owl': {'tag': 'owl',
                                 'value': 'AnnotationProperty, AnnotationAssertion'}},
         'domain_of': ['NamedEntity',
                       'CellType',
                       'BiologicalProcess',
                       'CellularComponent'],
         'slot_uri': 'rdfs:label'} })
    original_spans: Optional[list[str]] = Field(default=None, description="""The coordinates of the original text span from which the named entity was extracted, inclusive. For example, \"10:25\" means the span starting from the 10th character and ending with the 25th character. The first character in the text has index 0. Newlines are treated as single characters. Multivalued as there may be multiple spans for a single text.""", json_schema_extra = { "linkml_meta": {'alias': 'original_spans',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['This is determined during grounding and normalization',
                      'But is based on the full input text'],
         'domain_of': ['NamedEntity']} })

    @field_validator('original_spans')
    def pattern_original_spans(cls, v):
        pattern=re.compile(r"^\d+:\d+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid original_spans format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid original_spans format: {v}"
            raise ValueError(err_msg)
        return v


class Publication(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core'})

    id: Optional[str] = Field(default=None, description="""The publication identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id', 'domain_of': ['NamedEntity', 'Publication']} })
    title: Optional[str] = Field(default=None, description="""The title of the publication""", json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['Publication']} })
    abstract: Optional[str] = Field(default=None, description="""The abstract of the publication""", json_schema_extra = { "linkml_meta": {'alias': 'abstract', 'domain_of': ['Publication']} })
    combined_text: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'combined_text', 'domain_of': ['Publication']} })
    full_text: Optional[str] = Field(default=None, description="""The full text of the publication""", json_schema_extra = { "linkml_meta": {'alias': 'full_text', 'domain_of': ['Publication']} })


class AnnotatorResult(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://w3id.org/ontogpt/core'})

    subject_text: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'subject_text', 'domain_of': ['AnnotatorResult']} })
    object_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'object_id', 'domain_of': ['AnnotatorResult']} })
    object_text: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'object_text', 'domain_of': ['AnnotatorResult']} })


class CellType(NamedEntity):
    """
    Represents a specific cell type with links to biological processes in GO.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/ontogpt/cell_processes', 'tree_root': True})

    label: Optional[str] = Field(default=None, description="""The concise name of the cell type""", json_schema_extra = { "linkml_meta": {'alias': 'label',
         'domain_of': ['NamedEntity',
                       'CellType',
                       'BiologicalProcess',
                       'CellularComponent'],
         'slot_uri': 'rdfs:label'} })
    biological_processes: Optional[list[str]] = Field(default=None, description="""semicolon-separated list of cell type to biological processes relationships""", json_schema_extra = { "linkml_meta": {'alias': 'biological_processes',
         'annotations': {'prompt': {'tag': 'prompt',
                                    'value': 'semicolon-separated list of biological '
                                             'processes that this cell type plays. '
                                             'These should be short descriptive terms '
                                             'corresponding to ontology terms in the '
                                             'GO biological process hierarchy.'}},
         'domain_of': ['CellType'],
         'slot_uri': 'RO:0002215'} })
    cellular_component: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'alias': 'cellular_component',
         'annotations': {'description': {'tag': 'description',
                                         'value': 'semicolon-separated list of cell '
                                                  'type to cellular components '
                                                  'relationships'},
                         'owl': {'tag': 'owl',
                                 'value': 'SubClassOf, ObjectSomeValuesFrom'},
                         'prompt': {'tag': 'prompt',
                                    'value': 'semicolon-separated list of cellular '
                                             'components that this cell type have. '
                                             'These should be short descriptive terms '
                                             'corresponding to ontology terms in the '
                                             'GO cellular component hierarchy.'}},
         'domain_of': ['CellType'],
         'slot_uri': 'BFO:0000051'} })
    id: str = Field(default=..., description="""A unique identifier for the named entity""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['this is populated during the grounding and normalization step'],
         'domain_of': ['NamedEntity', 'Publication']} })
    original_spans: Optional[list[str]] = Field(default=None, description="""The coordinates of the original text span from which the named entity was extracted, inclusive. For example, \"10:25\" means the span starting from the 10th character and ending with the 25th character. The first character in the text has index 0. Newlines are treated as single characters. Multivalued as there may be multiple spans for a single text.""", json_schema_extra = { "linkml_meta": {'alias': 'original_spans',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['This is determined during grounding and normalization',
                      'But is based on the full input text'],
         'domain_of': ['NamedEntity']} })

    @field_validator('original_spans')
    def pattern_original_spans(cls, v):
        pattern=re.compile(r"^\d+:\d+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid original_spans format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid original_spans format: {v}"
            raise ValueError(err_msg)
        return v


class BiologicalProcess(NamedEntity):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'annotators': {'tag': 'annotators', 'value': 'sqlite:obo:go'}},
         'from_schema': 'https://w3id.org/ontogpt/cell_processes',
         'id_prefixes': ['GO']})

    label: Optional[str] = Field(default=None, description="""The GO identifier for the biological process.""", json_schema_extra = { "linkml_meta": {'alias': 'label',
         'domain_of': ['NamedEntity',
                       'CellType',
                       'BiologicalProcess',
                       'CellularComponent'],
         'slot_uri': 'rdfs:label'} })
    definition: Optional[str] = Field(default=None, description="""Detailed description of the biological process as per Gene Ontology.""", json_schema_extra = { "linkml_meta": {'alias': 'definition',
         'domain_of': ['BiologicalProcess', 'CellularComponent'],
         'slot_uri': 'skos:definition'} })
    id: str = Field(default=..., description="""A unique identifier for the named entity""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['this is populated during the grounding and normalization step'],
         'domain_of': ['NamedEntity', 'Publication']} })
    original_spans: Optional[list[str]] = Field(default=None, description="""The coordinates of the original text span from which the named entity was extracted, inclusive. For example, \"10:25\" means the span starting from the 10th character and ending with the 25th character. The first character in the text has index 0. Newlines are treated as single characters. Multivalued as there may be multiple spans for a single text.""", json_schema_extra = { "linkml_meta": {'alias': 'original_spans',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['This is determined during grounding and normalization',
                      'But is based on the full input text'],
         'domain_of': ['NamedEntity']} })

    @field_validator('original_spans')
    def pattern_original_spans(cls, v):
        pattern=re.compile(r"^\d+:\d+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid original_spans format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid original_spans format: {v}"
            raise ValueError(err_msg)
        return v


class CellularComponent(NamedEntity):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'annotators': {'tag': 'annotators', 'value': 'sqlite:obo:go'}},
         'from_schema': 'https://w3id.org/ontogpt/cell_processes',
         'id_prefixes': ['GO']})

    label: Optional[str] = Field(default=None, description="""The GO identifier for the cellular component.""", json_schema_extra = { "linkml_meta": {'alias': 'label',
         'domain_of': ['NamedEntity',
                       'CellType',
                       'BiologicalProcess',
                       'CellularComponent'],
         'slot_uri': 'rdfs:label'} })
    definition: Optional[str] = Field(default=None, description="""Detailed description of the cellular component of cell as per Gene Ontology.""", json_schema_extra = { "linkml_meta": {'alias': 'definition',
         'domain_of': ['BiologicalProcess', 'CellularComponent'],
         'slot_uri': 'skos:definition'} })
    id: str = Field(default=..., description="""A unique identifier for the named entity""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['this is populated during the grounding and normalization step'],
         'domain_of': ['NamedEntity', 'Publication']} })
    original_spans: Optional[list[str]] = Field(default=None, description="""The coordinates of the original text span from which the named entity was extracted, inclusive. For example, \"10:25\" means the span starting from the 10th character and ending with the 25th character. The first character in the text has index 0. Newlines are treated as single characters. Multivalued as there may be multiple spans for a single text.""", json_schema_extra = { "linkml_meta": {'alias': 'original_spans',
         'annotations': {'prompt.skip': {'tag': 'prompt.skip', 'value': 'true'}},
         'comments': ['This is determined during grounding and normalization',
                      'But is based on the full input text'],
         'domain_of': ['NamedEntity']} })

    @field_validator('original_spans')
    def pattern_original_spans(cls, v):
        pattern=re.compile(r"^\d+:\d+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid original_spans format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid original_spans format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExtractionResult.model_rebuild()
NamedEntity.model_rebuild()
CompoundExpression.model_rebuild()
Triple.model_rebuild()
TextWithTriples.model_rebuild()
TextWithEntity.model_rebuild()
RelationshipType.model_rebuild()
Publication.model_rebuild()
AnnotatorResult.model_rebuild()
CellType.model_rebuild()
BiologicalProcess.model_rebuild()
CellularComponent.model_rebuild()

