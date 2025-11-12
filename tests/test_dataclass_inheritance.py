"""Test dataclass inheritance and MRO resolution for runtime_docs."""

import dataclasses
from dataclasses import InitVar, dataclass, field
from typing import ClassVar

from runtime_docstrings import docstrings, get_docstrings

# Test basic dataclass inheritance with docstrings


@docstrings
@dataclass
class BaseDataClass:
    """Base dataclass with documented fields."""

    base_field: str
    """Base field documentation."""

    shared_field: str = "base_value"
    """Shared field from base class."""

    overridden_field: str = "base_override"
    """Field that will be overridden in child class."""


@docstrings
@dataclass
class ChildDataClass(BaseDataClass):
    """Child dataclass inheriting from BaseDataClass."""

    overridden_field: str = "child_override"
    """Overridden field in child class."""

    child_field: str = "child_value"
    """Child field documentation."""


def test_basic_dataclass_inheritance():
    """Test basic inheritance between dataclasses with docstrings."""
    # Check that each class has its own docstrings
    base_docs = get_docstrings(BaseDataClass)
    assert "base_field" in base_docs
    assert base_docs["base_field"] == "Base field documentation."
    assert "shared_field" in base_docs
    assert base_docs["shared_field"] == "Shared field from base class."
    assert "overridden_field" in base_docs
    assert base_docs["overridden_field"] == "Field that will be overridden in child class."

    child_docs = get_docstrings(ChildDataClass)
    assert "child_field" in child_docs
    assert child_docs["child_field"] == "Child field documentation."
    assert "overridden_field" in child_docs
    assert child_docs["overridden_field"] == "Overridden field in child class."

    # Base fields should not appear in child's direct docstrings
    assert "base_field" not in child_docs
    assert "shared_field" not in child_docs


# Test multi-level dataclass inheritance


@docstrings
@dataclass
class GrandparentDataClass:
    """Grandparent dataclass for multi-level inheritance testing."""

    grandparent_field: str = "grandparent_value"
    """Grandparent field documentation."""

    shared_field: str = "grandparent_shared"
    """Shared field from grandparent."""


@docstrings
@dataclass
class ParentDataClass(GrandparentDataClass):
    """Parent dataclass for multi-level inheritance testing."""

    parent_field: str = "parent_value"
    """Parent field documentation."""

    shared_field: str = "parent_shared"
    """Shared field from parent."""


@docstrings
@dataclass
class MultiLevelChildDataClass(ParentDataClass):
    """Child dataclass for multi-level inheritance testing."""

    child_field: str = "child_value"
    """Child field documentation."""

    # No docstring for this field to test inheritance of docstrings
    shared_field: str = "child_shared"


def test_multi_level_dataclass_inheritance():
    """Test multi-level inheritance between dataclasses with docstrings."""
    # Check that each class has its own docstrings
    grandparent_docs = get_docstrings(GrandparentDataClass)
    assert "grandparent_field" in grandparent_docs
    assert "shared_field" in grandparent_docs

    parent_docs = get_docstrings(ParentDataClass)
    assert "parent_field" in parent_docs
    assert "shared_field" in parent_docs

    child_docs = get_docstrings(MultiLevelChildDataClass)
    assert "child_field" in child_docs
    assert "shared_field" not in child_docs  # No docstring for this field

    # Test MRO resolution for child class

    assert MultiLevelChildDataClass.__doc_grandparent_field__ == "Grandparent field documentation."
    assert MultiLevelChildDataClass.__doc_parent_field__ == "Parent field documentation."
    assert MultiLevelChildDataClass.__doc_child_field__ == "Child field documentation."
    assert MultiLevelChildDataClass.__doc_shared_field__ == "Shared field from parent."

    # Test MRO resolution for parent class
    assert ParentDataClass.__doc_grandparent_field__ == "Grandparent field documentation."
    assert ParentDataClass.__doc_parent_field__ == "Parent field documentation."
    assert ParentDataClass.__doc_shared_field__ == "Shared field from parent."


# Test dataclass inheritance with field metadata


@docstrings
@dataclass
class BaseWithMetadata:
    """Base dataclass with field metadata."""

    name: str = field(metadata={"validator": "str_validator"})
    """Name field with metadata."""

    age: int = field(default=30, metadata={"min": 0, "max": 120})
    """Age field with metadata."""


@docstrings
@dataclass
class ChildWithMetadata(BaseWithMetadata):
    """Child dataclass inheriting fields with metadata."""

    # Override with new metadata
    age: int = field(default=18, metadata={"min": 18, "max": 100})
    """Age field with overridden metadata."""

    child_field: str = field(default="", metadata={"required": True})
    """Child-specific field with metadata."""


def test_inheritance_with_field_metadata():
    """Test inheritance of fields with metadata."""
    # Check that each class has its own field docstrings
    base_docs = get_docstrings(BaseWithMetadata)
    assert "name" in base_docs
    assert "age" in base_docs

    child_docs = get_docstrings(ChildWithMetadata)
    assert "age" in child_docs
    assert "child_field" in child_docs

    # Check field metadata
    base_fields = {f.name: f for f in dataclasses.fields(BaseWithMetadata)}
    child_fields = {f.name: f for f in dataclasses.fields(ChildWithMetadata)}

    # Base class metadata
    assert "validator" in base_fields["name"].metadata
    assert base_fields["name"].metadata["validator"] == "str_validator"
    assert "min" in base_fields["age"].metadata
    assert base_fields["age"].metadata["min"] == 0

    # Child class metadata (should override parent)
    assert "validator" in child_fields["name"].metadata  # Inherited
    assert child_fields["name"].metadata["validator"] == "str_validator"
    assert "min" in child_fields["age"].metadata  # Overridden
    assert child_fields["age"].metadata["min"] == 18
    assert "required" in child_fields["child_field"].metadata
    assert child_fields["child_field"].metadata["required"] is True

    assert "name" in base_fields
    assert base_fields["name"].metadata["__doc__"] == "Name field with metadata."

    assert "age" in child_fields
    assert child_fields["age"].metadata["__doc__"] == "Age field with overridden metadata."


# Test complex inheritance with mixins and multiple inheritance


class MixinClass:
    """A mixin class with attributes."""

    mixin_attr: str = "mixin_value"
    """Mixin attribute."""


@docstrings
class RegularBaseClass:
    """A regular base class."""

    regular_attr: str = "regular_value"
    """Regular attribute."""


@docstrings
@dataclass
class ComplexDataClass(MixinClass, RegularBaseClass):
    """A dataclass with complex inheritance."""

    dataclass_field: str = "dataclass_value"
    """Dataclass field."""


def test_complex_inheritance():
    """Test complex inheritance with mixins and multiple inheritance."""
    # Check docstrings
    docs = get_docstrings(ComplexDataClass)
    assert "dataclass_field" in docs
    assert docs["dataclass_field"] == "Dataclass field."

    # MixinClass doesn't have docstrings decorator, so its attributes won't have docstrings

    # RegularBaseClass has docstrings
    regular_docs = get_docstrings(RegularBaseClass)
    assert "regular_attr" in regular_docs
    assert regular_docs["regular_attr"] == "Regular attribute."

    assert ComplexDataClass.__doc_dataclass_field__ == "Dataclass field."

    assert ComplexDataClass.__doc_regular_attr__ == "Regular attribute."

    assert not hasattr(ComplexDataClass, "__doc_mixin_attr__")

    # Test instance creation
    instance = ComplexDataClass()
    assert instance.dataclass_field == "dataclass_value"
    assert instance.regular_attr == "regular_value"
    assert instance.mixin_attr == "mixin_value"


# Test inheritance with field default factory functions


@docstrings
@dataclass
class BaseWithFactory:
    """Base dataclass with default factory."""

    items: list[str] = field(default_factory=list)
    """List of items with default factory."""


@docstrings
@dataclass
class ChildWithFactory(BaseWithFactory):
    """Child dataclass inheriting default factory."""

    # Override with new default factory
    items: list[str] = field(default_factory=lambda: ["default"])
    """List of items with overridden default factory."""

    child_items: dict[str, int] = field(default_factory=dict)
    """Child-specific dictionary with default factory."""


def test_inheritance_with_default_factory():
    """Test inheritance with field default factory functions."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithFactory)
    assert "items" in base_docs
    assert base_docs["items"] == "List of items with default factory."

    child_docs = get_docstrings(ChildWithFactory)
    assert "items" in child_docs
    assert child_docs["items"] == "List of items with overridden default factory."
    assert "child_items" in child_docs
    assert child_docs["child_items"] == "Child-specific dictionary with default factory."

    # Test instance creation
    base_instance = BaseWithFactory()
    assert base_instance.items == []

    child_instance = ChildWithFactory()
    assert child_instance.items == ["default"]
    assert child_instance.child_items == {}


# Test inheritance with __post_init__ processing


@docstrings
@dataclass
class BaseWithPostInit:
    """Base dataclass with __post_init__."""

    name: str
    """Name field."""

    processed: str = field(init=False)
    """Field processed after initialization."""

    def __post_init__(self):
        """Process after initialization."""
        self.processed = f"Processed: {self.name}"


@docstrings
@dataclass
class ChildWithPostInit(BaseWithPostInit):
    """Child dataclass with __post_init__."""

    age: int = 0
    """Age field."""

    full_info: str = field(init=False)
    """Full information field."""

    def __post_init__(self):
        """Override parent's __post_init__."""
        super().__post_init__()
        self.full_info = f"{self.name} ({self.age})"


def test_inheritance_with_post_init():
    """Test inheritance with __post_init__ processing."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithPostInit)
    assert "name" in base_docs
    assert "processed" in base_docs

    child_docs = get_docstrings(ChildWithPostInit)
    assert "age" in child_docs
    assert "full_info" in child_docs

    # Test instance creation and post-init processing
    base_instance = BaseWithPostInit("Base")
    assert base_instance.name == "Base"
    assert base_instance.processed == "Processed: Base"

    child_instance = ChildWithPostInit("Child", 10)
    assert child_instance.name == "Child"
    assert child_instance.age == 10
    assert child_instance.processed == "Processed: Child"
    assert child_instance.full_info == "Child (10)"


# Test inheritance with slots


@docstrings
@dataclass(slots=True)
class BaseWithSlots:
    """Base dataclass with slots."""

    name: str
    """Name field."""

    value: int = 0
    """Value field."""


@docstrings
@dataclass(slots=True)
class ChildWithSlots(BaseWithSlots):
    """Child dataclass with slots."""

    child_value: str = "default"
    """Child-specific value."""


def test_inheritance_with_slots():
    """Test inheritance with slots."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithSlots)
    assert "name" in base_docs
    assert "value" in base_docs

    child_docs = get_docstrings(ChildWithSlots)
    assert "child_value" in child_docs

    # Test instance creation
    base_instance = BaseWithSlots("Base")
    assert base_instance.name == "Base"
    assert base_instance.value == 0

    child_instance = ChildWithSlots("Child", child_value="test")
    assert child_instance.name == "Child"
    assert child_instance.value == 0
    assert child_instance.child_value == "test"


# Test inheritance with ClassVar fields


@docstrings
@dataclass
class BaseWithClassVar:
    """Base dataclass with ClassVar fields."""

    name: str = "default"
    """Name field."""

    DEFAULT_VALUE: ClassVar[int] = 42
    """Default value constant."""


@docstrings
@dataclass
class ChildWithClassVar(BaseWithClassVar):
    """Child dataclass with ClassVar fields."""

    age: int = 0
    """Age field."""

    # Override class variable
    DEFAULT_VALUE: ClassVar[int] = 100
    """Overridden default value."""

    CHILD_CONSTANT: ClassVar[str] = "child"
    """Child-specific constant."""


def test_inheritance_with_classvar():
    """Test inheritance with ClassVar fields."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithClassVar)
    assert "name" in base_docs
    assert "DEFAULT_VALUE" in base_docs

    child_docs = get_docstrings(ChildWithClassVar)
    assert "age" in child_docs
    assert "DEFAULT_VALUE" in child_docs
    assert "CHILD_CONSTANT" in child_docs

    # Test class variables
    assert BaseWithClassVar.DEFAULT_VALUE == 42
    assert ChildWithClassVar.DEFAULT_VALUE == 100
    assert ChildWithClassVar.CHILD_CONSTANT == "child"

    # Test instance creation
    base_instance = BaseWithClassVar("Base")
    assert base_instance.name == "Base"

    child_instance = ChildWithClassVar("Child", 10)
    assert child_instance.name == "Child"
    assert child_instance.age == 10


# Test inheritance with frozen dataclasses


@docstrings
@dataclass(frozen=True)
class BaseFrozen:
    """Base frozen dataclass."""

    name: str
    """Name field."""

    value: int = 0
    """Value field."""


@docstrings
@dataclass(frozen=True)
class ChildFrozen(BaseFrozen):
    """Child frozen dataclass."""

    child_value: str = "default"
    """Child-specific value."""


def test_inheritance_with_frozen():
    """Test inheritance with frozen dataclasses."""
    # Check docstrings
    base_docs = get_docstrings(BaseFrozen)
    assert "name" in base_docs
    assert "value" in base_docs

    child_docs = get_docstrings(ChildFrozen)
    assert "child_value" in child_docs

    # Test instance creation
    base_instance = BaseFrozen("Base")
    assert base_instance.name == "Base"
    assert base_instance.value == 0

    child_instance = ChildFrozen("Child", child_value="test")
    assert child_instance.name == "Child"
    assert child_instance.value == 0
    assert child_instance.child_value == "test"


# Test inheritance with InitVar fields


@docstrings
@dataclass
class BaseWithInitVar:
    """Base dataclass with InitVar."""

    name: str
    """Name field."""

    password: InitVar[str]
    """Password used only during initialization."""

    hashed_password: str = field(init=False)
    """Hashed password stored after initialization."""


@docstrings
@dataclass
class ChildWithInitVar(BaseWithInitVar):
    """Child dataclass with InitVar."""

    extra_data: InitVar[dict]
    """Extra data used only during initialization."""

    age: int = 0
    """Age field."""

    metadata: dict = field(default_factory=dict, init=False)
    """Metadata stored after initialization."""


def test_inheritance_with_initvar():
    """Test inheritance with InitVar fields."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithInitVar)
    assert "name" in base_docs
    assert "password" in base_docs
    assert "hashed_password" in base_docs

    child_docs = get_docstrings(ChildWithInitVar)
    assert "age" in child_docs
    assert "extra_data" in child_docs
    assert "metadata" in child_docs


# Test inheritance with field renaming


@docstrings
@dataclass
class BaseWithRename:
    """Base dataclass with field renaming."""

    field_name: str = field(metadata={"original_name": "field_name"})
    """Field with metadata about original name."""


@docstrings
@dataclass
class ChildWithRename(BaseWithRename):
    """Child dataclass with field renaming."""

    # Same field name but different metadata
    field_name: str = field(metadata={"original_name": "renamed_field"})
    """Renamed field with updated metadata."""


def test_inheritance_with_field_renaming():
    """Test inheritance with field renaming."""
    # Check docstrings
    base_docs = get_docstrings(BaseWithRename)
    assert "field_name" in base_docs

    child_docs = get_docstrings(ChildWithRename)
    assert "field_name" in child_docs

    # Check field metadata
    base_fields = {f.name: f for f in dataclasses.fields(BaseWithRename)}
    child_fields = {f.name: f for f in dataclasses.fields(ChildWithRename)}

    assert "original_name" in base_fields["field_name"].metadata
    assert base_fields["field_name"].metadata["original_name"] == "field_name"

    assert "original_name" in child_fields["field_name"].metadata
    assert child_fields["field_name"].metadata["original_name"] == "renamed_field"

    assert "field_name" in base_fields
    assert (
        base_fields["field_name"].metadata["__doc__"] == "Field with metadata about original name."
    )

    assert "field_name" in child_fields
    assert child_fields["field_name"].metadata["__doc__"] == "Renamed field with updated metadata."

    # Check that the docstrings are accessible via get_docstrings
    base_docs = get_docstrings(BaseWithRename)
    assert "field_name" in base_docs
    assert base_docs["field_name"] == "Field with metadata about original name."

    child_docs = get_docstrings(ChildWithRename)
    assert "field_name" in child_docs
    assert child_docs["field_name"] == "Renamed field with updated metadata."

    # Test instance creation
    base_instance = BaseWithRename("base_value")
    assert base_instance.field_name == "base_value"

    child_instance = ChildWithRename("child_value")
    assert child_instance.field_name == "child_value"
